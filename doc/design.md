# SnapTranslate 詳細設計

## 1. アーキテクチャ概要

SnapTranslate は Windows 常駐型の Python アプリケーションとして構成する。
グローバルホットキーを入口に、画面範囲画像翻訳フローとテキスト入力翻訳フローを非同期に実行し、結果をオーバーレイ表示またはクリップボードへ反映する。

読み取り翻訳ではローカル OCR を使わない。指定範囲のスクリーンショットを ChatGPT API の画像入力へ直接渡し、画像内テキストの読み取りと翻訳を 1 回の API 呼び出しで行う。

UI と外部 API 呼び出しを密結合にしないため、アプリケーション全体を以下の層に分ける。

- Presentation: 設定 GUI、入力欄、オーバーレイ、ステータス表示
- Application: ユースケース、状態遷移、ホットキーイベント制御
- Domain: 設定モデル、範囲情報、翻訳リクエスト/結果、アプリ状態
- Infrastructure: ChatGPT API、スクリーンショット、画像エンコード、クリップボード、設定永続化、ログ

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
        image_encoder.py
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

`ocr.py` と PaddleOCR 依存は主経路から外す。将来ローカル OCR を任意機能として戻す場合も、画像翻訳の主ユースケースには直接依存させない。

## 3. 主要クラス

### 3.1 `SnapTranslateApp`

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

### 3.2 `AppSettings`

アプリ全体の設定モデル。

主な属性:

- `read_hotkey: str`
- `input_hotkey: str`
- `region_mode: RegionMode`
- `saved_region: ScreenRegion | None`
- `show_status: bool`
- `read_image_prompt: str`
- `input_translation_prompt: str`
- `chatgpt_model: str`
- `overlay_text_color: str`
- `overlay_font_family: str`
- `overlay_font_size: int`
- `api_key_source: ApiKeySource`
- `api_key: str`
- `keep_draft_on_hide: bool`
- `enable_history: bool`
- `history_path: str`
- `request_timeout_seconds: int`

互換性のため、既存設定ファイルに `read_translation_prompt` がある場合は `read_image_prompt` へ移行する。`ocr_language` は廃止予定フィールドとして読み込みは許容するが、新規保存では出力しない。

### 3.3 `HotkeyController`

pywin32 を使ってグローバルホットキーを登録・解除する。

主なイベント:

- `on_read_hotkey_pressed`
- `on_input_hotkey_pressed`

動作:

- A 指定キー押下時、読み取りオーバーレイが表示中なら非表示にする。
- A 指定キー押下時、読み取りオーバーレイが非表示なら画像翻訳フローを開始する。
- B 指定キー押下時、入力欄の表示/非表示を切り替える。

### 3.4 `ReadTranslateUseCase`

画面範囲をスクリーンショットとして取得し、ChatGPT API の画像解析翻訳結果をオーバーレイへ表示する。

依存:

- `RegionProvider`
- `ScreenshotService`
- `ImageTranslator`
- `OverlayWindow`
- `StatusWindow`
- `AppState`

処理手順:

1. 現在の状態を確認し、処理中なら二重起動を抑止する。
2. 範囲指定モードを確認する。
3. 事前設定方式の場合は保存済み範囲を取得する。
4. 逐次指定方式の場合は `RegionSelector` を表示し、ユーザー選択範囲を取得する。
5. 指定範囲のスクリーンショットを取得する。
6. 状態を `[read]: analyzing` に更新する。
7. スクリーンショット画像と `read_image_prompt` を `ImageTranslator` に渡す。
8. 画像内に翻訳対象がない、または API 応答が空ならエラー表示して終了する。
9. 指定範囲の位置にオーバーレイを表示する。
10. 状態を `[read]: visible` に更新する。

エラー時:

- 範囲未設定: `[read]: region not set`
- スクリーンショット取得失敗: `[read]: capture failed`
- 画像解析失敗: `[read]: analysis failed`
- 翻訳対象なし: `[read]: no text`
- ChatGPT API 失敗: `[read]: api failed`

### 3.5 `InputTranslateUseCase`

入力欄のテキストを翻訳し、結果をクリップボードへコピーする。

依存:

- `InputWindow`
- `TextTranslator`
- `ClipboardService`
- `StatusWindow`
- `AppState`

処理手順:

1. 入力欄で Enter が押される。
2. 入力テキストを取得する。
3. 空文字なら翻訳せず終了する。
4. 状態を `[input]: translating` に更新する。
5. ChatGPT API で翻訳する。
6. 翻訳結果をクリップボードへコピーする。
7. 状態を `[input]: copied` に更新する。
8. 必要に応じて入力欄をクリアする。

### 3.6 翻訳インターフェース

テキスト翻訳と画像翻訳は入力形式が異なるため、同じ `translate(text, prompt)` へ無理に寄せない。

```python
class TextTranslator(Protocol):
    def translate_text(self, text: str, prompt: str) -> TranslationResult:
        ...


class ImageTranslator(Protocol):
    def translate_image(self, image: Image.Image, prompt: str) -> TranslationResult:
        ...
```

`ChatGptTranslator` は両方の Protocol を実装してよい。ただし内部ではテキスト入力と画像入力の API ペイロードを分ける。

画像入力時の方針:

- 画像は PNG としてメモリ上でエンコードし、base64 data URL または SDK が要求する画像入力形式へ変換する。
- プロンプトには「画像内の翻訳対象テキストを読み取り、自然に翻訳し、翻訳結果のみ返す」ことを明記する。
- OCR 結果相当の中間テキストは原則保存しない。必要な場合はモデル応答に原文も含める別モードを将来拡張とする。
- モデルが画像入力に非対応の場合は早期に設定エラーとして扱う。

### 3.7 `ImageEncoder`

スクリーンショット画像を ChatGPT API に渡せる形式へ変換する。

```python
class ImageEncoder(Protocol):
    def to_data_url(self, image: Image.Image) -> str:
        ...
```

責務:

- PNG エンコード
- base64 化
- data URL 生成
- 必要に応じた最大サイズ制御

画像サイズ制御は翻訳精度に影響するため、初期実装では原寸維持を基本にする。API 制限に抵触する場合のみ縮小を検討する。

### 3.8 オーバーレイ

`OverlayWindow` は翻訳結果を指定範囲上に表示する透明ウィンドウ。

表示仕様:

- ウィンドウ位置は `ScreenRegion` と一致させる。
- 背景は完全透明とする。
- テキストは範囲内で折り返す。
- テキスト色、フォント、サイズは `AppSettings` から反映する。
- テキストが範囲内に収まらない場合はフォントサイズ調整またはスクロール表示を検討する。

### 3.9 入力欄

`InputWindow` は B 指定キーで表示/非表示を切り替えるテキスト入力欄。

責務:

- 入力欄表示
- 入力テキスト管理
- Enter キー検知
- 翻訳中の入力抑止
- 完了/エラー表示

Enter の扱い:

- Enter: 翻訳実行
- Shift+Enter: 改行

### 3.10 ステータス表示と状態

`StatusWindow` はアプリ状態を小さく表示するウィンドウ。

`AppState` の読み取り状態例:

- `idle`
- `read_region_selecting`
- `read_capturing`
- `read_analyzing`
- `read_overlay_visible`
- `error`

`AppState` の入力状態例:

- `input_hidden`
- `input_visible`
- `input_translating`
- `input_copied`
- `error`

既存の `read_ocr_running` / `OCR_RUNNING` は `read_analyzing` / `ANALYZING` へ置き換える。

## 4. 状態遷移

### 4.1 読み取り機能

```text
idle
  -> read_region_selecting
  -> read_capturing
  -> read_analyzing
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
- スクリーンショット取得と ChatGPT API 呼び出しはワーカースレッドまたは `asyncio` タスクで実行する。
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
  "read_image_prompt": "Read the text in the image and translate it naturally. Return only the translation.",
  "input_translation_prompt": "Translate the input text naturally. Return only the translation.\\n\\n{text}",
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

移行方針:

- `read_translation_prompt` が存在し、`read_image_prompt` が存在しない場合は、値を `read_image_prompt` として読み込む。
- `ocr_language` は無視する。保存時には出力しない。
- 既存ユーザーに設定リセットを要求しない。

## 7. 翻訳履歴

翻訳履歴保存は任意機能とする。`enable_history` が `true` の場合のみ、ローカル JSONL へ保存する。

保存対象:

- 実行日時
- 翻訳種別。`read` または `input`
- 入力概要。読み取り翻訳では画像の保存は行わず、`source_text` は空文字または `[image]` とする。
- 翻訳結果
- 使用モデル
- メタデータ。読み取り翻訳では画像範囲、画像サイズなどの非機密メタデータのみ保存する。

保存先候補:

- `%APPDATA%/SnapTranslate/history.jsonl`

履歴ファイルはローカル生成物として扱い、Git 管理対象外にする。

## 8. エラー処理

共通方針:

- ユーザー向けには短いメッセージを出す。
- 詳細はログへ出力する。
- API キー、スクリーンショット画像、画像解析リクエスト、入力全文を不用意にログへ出さない。

主なエラー:

- 設定ファイル破損
- ホットキー登録失敗
- 範囲未設定
- スクリーンショット取得失敗
- 画像エンコード失敗
- 画像解析非対応モデル
- 画像内テキストなし
- API キー未設定
- ChatGPT API 失敗
- クリップボード更新失敗

## 9. テスト方針

### 9.1 単体テスト

- 設定モデルのバリデーション
- 旧設定から新設定への移行
- ホットキー文字列表現の解析
- 状態遷移
- 画像翻訳で画像入力が API クライアントへ渡されること
- 画像解析結果なし時の制御
- 翻訳失敗時にクリップボードを更新しないこと
- 設定保存/読み込み

### 9.2 結合テスト

- `ImageTranslator` をモックした読み取り翻訳フロー
- `TextTranslator` をモックした入力翻訳フロー
- 設定変更後のホットキー再登録

### 9.3 手動確認

- A 指定キーで画像翻訳が開始されること
- オーバーレイ表示中に A 指定キーで非表示になること
- B 指定キーで入力欄が表示/非表示になること
- Enter で翻訳され、クリップボードへコピーされること
- ステータス表示が設定で非表示になること

## 10. 実装順序

1. 設定モデルを `read_image_prompt` と旧設定移行へ対応させる。
2. `ReadState.OCR_RUNNING` を `ANALYZING` へ置き換える。
3. `ImageEncoder` を追加する。
4. `TextTranslator` / `ImageTranslator` Protocol を分離する。
5. `ChatGptTranslator.translate_image` を追加する。
6. `ReadTranslateUseCase` から `OcrService` 依存を削除し、画像翻訳へ置き換える。
7. `SnapTranslateApp` の `PaddleOcrService` 生成を削除する。
8. 設定 GUI から PaddleOCR language を削除し、画像翻訳プロンプトへ差し替える。
9. テストを画像翻訳モック前提に更新する。
10. PaddleOCR 依存と OCR テストを削除または任意機能扱いへ移動する。
11. README と手動確認手順を更新する。

## 11. 設計上の注意点

- 画像解析は OCR + テキスト翻訳より API コストとレイテンシが増える可能性がある。
- 画像内の不要な UI 文字まで拾う場合があるため、プロンプトで「翻訳対象らしい本文のみ」を指示できるようにする。
- 履歴に画像を保存しない方針を明確にし、スクリーンショット由来の機密情報を残さない。
- 画像対応モデルの可否は設定保存時または初回実行時に検出できるようにする。

## 12. 質問事項

質問事項と回答済み事項は `doc/question.md` に集約する。
