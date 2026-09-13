# B案デザイン基準 v1.03

Fluent 2の業務向け密度＋DADSの分かりやすい案内を採用。旧DADS資料は参考扱い。

## 文字

下表はCSS px相当の目標。Power Apps Sizeに一律転記しない。Classic/Modernの仕様と実際の100%表示で校正し、コントロール・設定値・スクリーンショットを記録する。以前のチャットのSize初期値は未校正候補。

| 用途 | 標準 | 大きな文字 | 太さ |
|---|---:|---:|---|
| 画面タイトル・職員名 | 20 | 24 | Semibold |
| セクション見出し | 16 | 18 | Semibold |
| 表・入力・ラベル | 14 | 16 | 本文Normal、ラベルSemibold |
| ボタン | 14 | 16 | Semibold |
| 操作案内 | 16 | 18 | Normal |
| 更新時刻等補足 | 12 | 14 | Normal |

表字間0、行ボックス20程度、説明24程度。v1.11の表行は48/大文字56、入力・ボタン44、セル左右12。長文は折返しと高さ増加で対応。Boldを常用しない。

v1.11の`Size`初期設定は、本文10.5pt／大文字12pt、節見出し12pt／13.5pt、画面タイトル15pt／18pt。1pt=4/3 CSS pxの換算を出発点にした設定であり、OS・ブラウザーの倍率や日本語フォールバックを含む実機校正済み値ではない。現行Modern Button／Text InputのSize単位はpointsである。[Microsoft Button](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/modern-controls/modern-control-button)、[Microsoft Text Input](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/modern-controls/modern-control-text-input)

帳票は固定様式のため、画面本文の文字サイズ切替を適用しない。セル内の余白不足は文字を小さくして解決せず、行高・列幅を調整する。

## 色・余白

| 用途 | 値 |
|---|---|
| ヘッダー | #073B78、白文字 |
| 主操作 | #0F6CBD、白文字 |
| 本文 | #242424 |
| 背景/面 | #F7F9FC / #FFFFFF |
| 見出し帯 | #EDF2F7 |
| 枠 | #CBD5E1、1px相当 |
| 選択 | #DCEAFF＋左マーカー＋選択状態 |
| 外余白/列間/節間 | 16 / 16 / 20 |
| 角丸 | 4程度 |
| サイドバー | 展開360px、折りたたみ操作帯48px程度、境界線1px |

状態は文字でも表示。金額右寄せ、日付yyyy/mm/dd、番号は文字列。v1.11の業務表は列対応を読み取れる1pxの薄い格子を維持し、基本情報の各値には枠を付けない。画像Bの見出しの強さは実装で抑える。

## 操作・検証

検索を主操作、クリア・閉じるは副操作。認定簿は「認定簿を表示」。TSVのみなら「Excel出力」と誤表示しない。
サイドバー開閉は44px以上の操作領域を取り、アイコンだけに依存せずTooltipまたは表示文字で「検索を開く／閉じる」を示す。折りたたみ時も選択職員のサマリーは右側に残す。
通常文字4.5:1を目標に実色を検証。Tab順・フォーカス・読み上げ・200%拡大を実機で確認。大きな文字切替だけでは合格にしない。
FluentのBody 1=14/20、Subtitle 2=16/22とDADS業務用Denseを参考にしたプロジェクト判断で、完全準拠の宣言ではない。

- https://fluent2.microsoft.design/typography
- https://design.digital.go.jp/dads/foundations/typography/

## 変更履歴

| 版 | 内容 |
|---|---|
| 1.03 | v1.11のポイント設定、表行48/56、基本情報と表の枠を具体化。実機校正との区別を明示 |
| 1.02 | 職員検索サイドバーの幅、操作領域、状態表現を追加 |
| 1.01 | B案採用、見出し抑制、Canvas設定値の校正を必須化 |
