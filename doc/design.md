# SnapTranslate 詳細設計

## 1. アーキテクチャ概要

SnapTranslate は Windows 常駐型の Python アプリケーションとして構成する。
グローバルホットキーを入口に、OCR 翻訳フローとテキスト入力翻訳フローを非同期に実行し、結果をオーバーレイ表示またはクリップボードへ反映する。

UI と外部 API 呼び出しを密結合にしないため、アプリケーション全体を以下の層に分ける。

- Presentation: 設定 GUI、入力欄、オーバーレイ、ステータス表示
- Application: ユースケース、状態遷移、ホットキーイベント制御
- Domain: 設定モデル、範囲情報、翻訳リクエスト/結果、アプリ状態
- Infrastructure: OCR、ChatGPT API、スクリーンショット、クリップボード、設定永続化、ログ

## 2. ディレクトリ構成

```text
SnapTranslate/
  README.md
  LICENSE
  pyproject.toml
  uv.lock
  doc/
    requirements.md
    design.md
  src/
    snaptranslate/
      __init__.py
      main.py
      app.py
      domain/
        __init__.py
        models.py
        state.py
      application/
        __init__.py
        hotkey_controller.py
        read_translate_usecase.py
        input_translate_usecase.py
      infrastructure/
        __init__.py
        config_store.py
        screenshot.py
        ocr.py
        history_store.py
        translator.py
        clipboard.py
        logging.py
      presentation/
        __init__.py
        settings_window.py
        overlay_window.py
        input_window.py
        status_window.py
        region_selector.py
  tests/
    unit/
    integration/
```

メインルートには `README.md`、`LICENSE`、`pyproject.toml`、`uv.lock` 程度を置き、実装は `src/snaptranslate/` に集約する。

## 3. 主要クラス

### 3.1 アプリケーション起動

#### `SnapTranslateApp`

アプリケーション全体のライフサイクルを管理する。

責務:

- 設定読み込み
- GUI 初期化
- ホットキー登録
- タスクトレイ常駐
- ユースケース生成
- アプリ終了処理

主なメソッド:

- `start() -> None`
- `stop() -> None`
- `reload_settings() -> None`

### 3.2 設定

#### `AppSettings`

アプリ全体の設定モデル。

主な属性:

- `read_hotkey: Hotkey`
- `input_hotkey: Hotkey`
- `region_mode: RegionMode`
- `saved_region: ScreenRegion | None`
- `show_status: bool`
- `read_translation_prompt: str`
- `input_translation_prompt: str`
- `chatgpt_model: str`
- `overlay_text_color: str`
- `overlay_font_family: str`
- `overlay_font_size: int`
- `api_key_source: ApiKeySource`
- `keep_draft_on_hide: bool`
- `enable_history: bool`
- `history_path: str`
- `request_timeout_seconds: int`

#### `ConfigStore`

設定の永続化を担当する。

責務:

- 設定ファイルの読み込み
- デフォルト設定の生成
- 設定ファイルへの保存
- 設定値のバリデーション

保存先候補:

- `%APPDATA%/SnapTranslate/config.json`

API キーは環境変数 `OPENAI_API_KEY` を優先し、必要に応じてローカル設定ファイルの参照も許可する。

### 3.3 ホットキー

#### `HotkeyController`

pywin32 を使ってグローバルホットキーを登録・解除する。

責務:

- A 指定キーの登録
- B 指定キーの登録
- 設定変更時の再登録
- ホットキー重複チェック
- Windows メッセージループとの連携

主なイベント:

- `on_read_hotkey_pressed`
- `on_input_hotkey_pressed`

動作:

- A 指定キー押下時、読み取りオーバーレイが表示中なら非表示にする。
- A 指定キー押下時、読み取りオーバーレイが非表示なら OCR 翻訳フローを開始する。
- B 指定キー押下時、入力欄の表示/非表示を切り替える。

### 3.4 OCR 翻訳ユースケース

#### `ReadTranslateUseCase`

画面範囲を OCR し、翻訳結果をオーバーレイへ表示する。

依存:

- `RegionProvider`
- `ScreenshotService`
- `OcrService`
- `Translator`
- `OverlayWindow`
- `StatusWindow`
- `AppState`

処理手順:

1. 現在の状態を確認し、処理中なら二重起動を抑止する。
2. 範囲指定モードを確認する。
3. 事前設定方式の場合は保存済み範囲を取得する。
4. 逐次指定方式の場合は `RegionSelector` を表示し、ユーザー選択範囲を取得する。
5. 指定範囲のスクリーンショットを取得する。
6. OCR を実行してテキストを抽出する。
7. OCR 結果が空ならエラー表示して終了する。
8. ChatGPT API で翻訳する。
9. 指定範囲の位置にオーバーレイを表示する。
10. 状態を `[読み取り]: 表示中` に更新する。

エラー時:

- OCR 失敗: `[読み取り]: OCR失敗`
- 翻訳失敗: `[読み取り]: 翻訳失敗`
- 範囲未設定: `[読み取り]: 範囲未設定`

### 3.5 入力翻訳ユースケース

#### `InputTranslateUseCase`

入力欄のテキストを翻訳し、結果をクリップボードへコピーする。

依存:

- `InputWindow`
- `Translator`
- `ClipboardService`
- `StatusWindow`
- `AppState`

処理手順:

1. 入力欄で Enter が押される。
2. 入力テキストを取得する。
3. 空文字なら翻訳せず終了する。
4. 状態を `[入力]: 翻訳中` に更新する。
5. ChatGPT API で翻訳する。
6. 翻訳結果をクリップボードへコピーする。
7. 状態を `[入力]: コピー完了` に更新する。
8. 必要に応じて入力欄をクリアする。

エラー時:

- 翻訳失敗時はクリップボードを更新しない。
- エラー内容を短く表示する。

### 3.6 翻訳

#### `Translator`

翻訳処理のインターフェース。

```python
class Translator(Protocol):
    def translate(self, text: str, prompt: str) -> TranslationResult:
        ...
```

#### `ChatGptTranslator`

ChatGPT API を利用する実装。

責務:

- API キー読み込み
- ユーザー設定プロンプトへの入力文埋め込み
- API 呼び出し
- タイムアウト制御
- エラーハンドリング

プロンプト方針:

- 読み取り翻訳と入力翻訳で、それぞれユーザー設定プロンプトを利用できるようにする。
- 原文言語の判定は LLM に任せる。
- 初期プロンプトでは、説明や注釈を付けず翻訳結果のみ返す方針にする。

### 3.7 OCR

#### `OcrService`

OCR 処理のインターフェース。

```python
class OcrService(Protocol):
    def extract_text(self, image: ImageLike) -> OcrResult:
        ...
```

OCR エンジンの確定前でも実装を進められるよう、インターフェースを先に固定する。

初期実装では PaddleOCR を利用する。PaddleOCR 固有の初期化、モデルパス、言語設定は `PaddleOcrService` に閉じ込め、ユースケース側からは `OcrService` として扱う。

PaddleOCR のモデルは初回起動時に自動ダウンロードしてよい。モデル、キャッシュ、生成物は `.gitignore` により Git 管理対象外にする。

### 3.8 オーバーレイ

#### `OverlayWindow`

翻訳結果を指定範囲上に表示する透明ウィンドウ。

責務:

- 指定座標へのウィンドウ生成
- 常に最前面表示
- 背景透明化
- クリック透過
- テキスト描画
- 表示/非表示切り替え

pywin32 利用候補:

- `CreateWindowEx`
- `WS_EX_LAYERED`
- `WS_EX_TOPMOST`
- `WS_EX_TRANSPARENT`
- `SetLayeredWindowAttributes`
- `UpdateLayeredWindow`

表示仕様:

- ウィンドウ位置は `ScreenRegion` と一致させる。
- 背景は完全透明とする。
- テキストは範囲内で折り返す。
- テキスト色、フォント、サイズは `AppSettings` から反映する。
- テキストが範囲内に収まらない場合はフォントサイズ調整またはスクロール表示を検討する。

### 3.9 入力欄

#### `InputWindow`

B 指定キーで表示/非表示を切り替えるテキスト入力欄。

責務:

- 入力欄表示
- 入力テキスト管理
- Enter キー検知
- 翻訳中の入力抑止
- 完了/エラー表示

Enter の扱い:

- Enter: 翻訳実行
- Shift+Enter: 改行

### 3.10 ステータス表示

#### `StatusWindow`

アプリ状態を小さく表示するウィンドウ。

責務:

- 右上などへの常時表示
- 状態テキスト更新
- 表示/非表示切り替え
- 一時メッセージの自動消去

#### `AppState`

読み取り機能と入力機能の状態を保持する。

状態例:

- `idle`
- `read_translating`
- `read_overlay_visible`
- `input_visible`
- `input_translating`
- `input_copied`
- `error`

## 4. 状態遷移

### 4.1 読み取り機能

```text
idle
  -> read_region_selecting
  -> read_ocr_running
  -> read_translating
  -> read_overlay_visible
  -> idle
```

補足:

- `read_overlay_visible` 中に A 指定キーを押すと `idle` に戻す。
- 処理中に A 指定キーを押した場合、初期実装では無視する。
- キャンセル対応は将来拡張とする。

### 4.2 入力機能

```text
input_hidden
  -> input_visible
  -> input_translating
  -> input_visible
```

補足:

- `input_visible` 中に B 指定キーを押すと `input_hidden` に戻す。
- `input_translating` 中は二重送信を防ぐ。
- 翻訳完了後は入力欄を表示したままにするか、設定により非表示にする余地を残す。

## 5. スレッド・非同期設計

- Windows メッセージループと GUI 更新はメインスレッドで扱う。
- OCR と ChatGPT API 呼び出しはワーカースレッドまたは `asyncio` タスクで実行する。
- UI 更新はメインスレッドにディスパッチする。
- 同一ユースケース内では処理中フラグを持ち、多重実行を防止する。

初期実装では、pywin32 との相性を優先し、ワーカースレッド + キューによるメインスレッド通知を採用する。

## 6. 設定ファイル

設定ファイル例:

```json
{
  "read_hotkey": "Ctrl+Shift+F8",
  "input_hotkey": "Ctrl+Shift+F9",
  "region_mode": "saved",
  "saved_region": {
    "left": 100,
    "top": 100,
    "width": 800,
    "height": 300
  },
  "show_status": true,
  "read_translation_prompt": "Translate the OCR text naturally. Return only the translation.",
  "input_translation_prompt": "Translate the input text naturally. Return only the translation.",
  "chatgpt_model": "gpt-5.4-mini",
  "overlay_text_color": "#FFFFFF",
  "overlay_font_family": "Yu Gothic UI",
  "overlay_font_size": 18,
  "api_key_source": "env",
  "keep_draft_on_hide": true,
  "enable_history": false,
  "history_path": "%APPDATA%/SnapTranslate/history.jsonl",
  "request_timeout_seconds": 30
}
```

## 7. 翻訳履歴

翻訳履歴保存は任意機能とする。`enable_history` が `true` の場合のみ、ローカル JSONL へ保存する。

保存対象:

- 実行日時
- 翻訳種別。`read` または `input`
- 入力文。OCR 結果または入力欄の原文
- 翻訳結果
- 使用モデル

保存先候補:

- `%APPDATA%/SnapTranslate/history.jsonl`

履歴ファイルはローカル生成物として扱い、Git 管理対象外にする。

## 8. エラー処理

共通方針:

- ユーザー向けには短いメッセージを出す。
- 詳細はログへ出力する。
- API キーや入力全文を不用意にログへ出さない。

主なエラー:

- 設定ファイル破損
- ホットキー登録失敗
- 範囲未設定
- スクリーンショット取得失敗
- OCR 失敗
- OCR 結果なし
- API キー未設定
- ChatGPT API 失敗
- クリップボード更新失敗

## 9. テスト方針

### 9.1 単体テスト

- 設定モデルのバリデーション
- ホットキー文字列表現の解析
- 状態遷移
- OCR 結果なし時の制御
- 翻訳失敗時にクリップボードを更新しないこと
- 設定保存/読み込み

### 9.2 結合テスト

- OCR サービスをモックした読み取り翻訳フロー
- Translator をモックした入力翻訳フロー
- 設定変更後のホットキー再登録

### 9.3 手動確認

- A 指定キーで OCR 翻訳が開始されること
- オーバーレイ表示中に A 指定キーで非表示になること
- B 指定キーで入力欄が表示/非表示になること
- Enter で翻訳され、クリップボードへコピーされること
- ステータス表示が設定で非表示になること

## 10. 実装順序

1. uv プロジェクト作成と `src/snaptranslate/` 構成作成
2. 設定モデルと設定保存/読み込み
3. ChatGPT 翻訳クライアント
4. クリップボードサービス
5. 入力欄と入力翻訳フロー
6. ステータス表示
7. ホットキー制御
8. 範囲選択とスクリーンショット取得
9. OCR サービス
10. オーバーレイ表示
11. タスクトレイ常駐
12. 設定 GUI
13. 翻訳履歴保存
14. 結合・手動確認

## 11. 質問事項

質問事項と回答済み事項は `doc/question.md` に集約する。
