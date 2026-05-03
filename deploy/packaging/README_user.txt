SnapTranslate ユーザーガイド

1. 初回設定（APIキー）

SnapTranslateで翻訳するにはOpenAI APIキーが必要です。

推奨設定（環境変数）:
1. Windowsの検索で「環境変数」を開きます。
2. ユーザー環境変数に `OPENAI_API_KEY` を追加します。
3. 値に自分のOpenAI APIキーを入力します。
4. SnapTranslateを起動中の場合は、一度終了して起動し直します。

アプリ内で設定する方法:
1. `SnapTranslate.exe` を起動します。
2. タスクトレイのSnapTranslateアイコンを右クリックし、`Settings` を開きます。
3. `API` タブで `API key source` を `Saved in config.json` に変更します。
4. `API key` にAPIキーを入力し、`Save` を押します。

APIキーは他人に見せないでください。`config.json` に保存した場合、設定ファイルは `%APPDATA%\SnapTranslate` に作成されます。

2. 操作方法

起動:
- `SnapTranslate.exe` をダブルクリックします。
- 起動するとWindowsのタスクトレイにSnapTranslateアイコンが表示されます。

画像内の文字を翻訳する:
1. `Ctrl+Enter` を押します。
2. `Region mode` が `Interactive` の場合は、翻訳したい画面範囲をドラッグします。
3. 翻訳結果は、設定に応じてオーバーレイまたは通常ウィンドウに表示されます。
4. 結果表示中に `Ctrl+Enter` をもう一度押すと、表示を閉じます。

手入力テキストを翻訳する:
1. `Shift+Enter` を押します。
2. 入力ウィンドウに翻訳したい文章を入力または貼り付けます。
3. `Enter` を押すと翻訳し、結果をクリップボードへコピーします。
4. 改行したい場合は `Shift+Enter` を使います。
5. `Shift+Enter` をもう一度押すと、入力ウィンドウを非表示にします。

終了:
- タスクトレイのSnapTranslateアイコンを右クリックし、`Quit` を選びます。

3. 設定方法

設定画面は、タスクトレイのSnapTranslateアイコンを右クリックして `Settings` を選ぶと開けます。

General:
- `UI language`: 設定画面の表示言語を切り替えます。保存後、設定画面を開き直すと反映されます。
- `Read hotkey`: 画像翻訳を実行するホットキーです。
- `Input hotkey`: 手入力翻訳ウィンドウを表示するホットキーです。
- `Keep input draft on hide`: 入力ウィンドウを非表示にしても、入力途中の文章を残します。

API:
- `ChatGPT model`: 翻訳に使うOpenAIモデルです。画像翻訳には画像入力対応モデルが必要です。
- `API key source`: APIキーを環境変数から読むか、`config.json` から読むかを選びます。
- `API key`: `API key source` が `Saved in config.json` の場合に使います。
- `Request timeout seconds`: API応答を待つ最大秒数です。

Read:
- `Region mode`: 画像翻訳の範囲選択方法です。`Saved` は保存済み範囲、`Interactive` は毎回ドラッグで選択します。
- `Set saved region`: `Saved` モードで使う画面範囲を登録します。

Overlay:
- `Read result display`: 画像翻訳結果をオーバーレイで表示するか、通常ウィンドウで表示するかを選びます。
- `Overlay text color`: オーバーレイ文字色です。例: `#FFFFFF`
- `Overlay font`: オーバーレイ文字に使うフォントです。
- `Overlay font size`: オーバーレイ文字のサイズです。
- `Show status`: 小さなステータス表示を出すかどうかを切り替えます。

History:
- `Enable local history JSONL`: 翻訳履歴を `%APPDATA%\SnapTranslate\history.jsonl` に保存します。

Prompts:
- `Read image translation prompt`: 画像翻訳時に使う指示文です。
- `Input translation prompt`: 手入力翻訳時に使う指示文です。`{text}` は入力文が入る場所なので残してください。

設定項目にマウスを重ねると、詳細説明が表示されます。

4. ステータスについて

共通:
- `[ready]`: アプリが起動し、待機中です。

Read系:
- `[read]: selecting`: 画面範囲を選択中です。
- `[read]: capturing`: 選択範囲を撮影中です。
- `[read]: analyzing`: 画像を送信し、翻訳中です。
- `[read]: visible`: 翻訳結果を表示中です。
- `[read]: idle`: 画像翻訳が待機中です。
- `[read]: busy`: 画像翻訳処理がすでに実行中です。少し待ってから再実行してください。
- `[read]: canceled`: 範囲選択がキャンセルされました。
- `[read]: error` または `[read]: ...`: 画像翻訳でエラーが発生しました。表示された内容を確認してください。

Input系:
- `[input]: visible`: 入力ウィンドウを表示中です。
- `[input]: hidden`: 入力ウィンドウは非表示です。
- `[input]: translating`: 入力文を翻訳中です。
- `[input]: copied`: 翻訳結果をクリップボードへコピーしました。
- `[input]: empty`: 入力文が空です。
- `[input]: busy`: 手入力翻訳がすでに実行中です。少し待ってから再実行してください。
- `[input]: error` または `[input]: ...`: 手入力翻訳でエラーが発生しました。表示された内容を確認してください。

困ったとき:
- `OPENAI_API_KEY is not set.` と表示された場合は、APIキー設定を確認してください。
- 詳細ログは `%APPDATA%\SnapTranslate\snaptranslate.log` に保存されます。
