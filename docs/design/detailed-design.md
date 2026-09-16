# 詳細設計書 v1.03

> 対象アプリ：共通（自動テスト／ハンドメイド）

対象：v1.08正本を基にしたv1.11のB案開発。Studio実機確認を含む残件はSTATUSに記載する。

## 1. ファイルと部品

管理用pa.yamlのScreens/scrStaffMasterSearch_v111/Childrenと貼付用paste.yamlのルート配列を同一にする。v1.11では旧v108と別画面へ導入できるよう識別子を111へ移行した。**v1.12以降は111の識別子を固定し、一括改名しない。** 版はファイル名・表示メタ情報・変更履歴で管理する。

| 機能 | 現行部品 | 主なプロパティ |
|---|---|---|
| 検索 | txtKeyword111, ddOrg111, ddStatus111, btnSearch111 | Text/Selected/OnSelect |
| 結果 | galStaff111, lblListTitle111 | Items/Text |
| ページ | btnPrev111, btnNext111, lblPage111 | OnSelect/DisplayMode/Text |
| 詳細 | conPerson111, lblName111 | Visible/Text |
| 履歴 | galWork111, galCommute111, galSocial111, galResident111, galTax111, galPayroll111 | Items |
| 帳票 | btnCertificate111, conLedgerModal111, pdfLedger111 | OnSelect/Visible/Document |
| PDF保存 | tmrLedgerPdf111 | OnTimerEnd（任意フロー接続） |
| サイドバー | conSearchSidebar111, conLeftScroll111, conLeftSurface111, btnSidebarToggle111 | Width/Visible/OnSelect/Tooltip |
| 文字切替 | btnTextSize111, varLargeText111 | OnSelect、各Size/Height/TemplateSize |

モダンコントロールへ変更する際、Text/Value等は実際の対象部品から出力したコードで確認し、旧部品のプロパティ名を流用しない。

## 2. データ契約

職員番号は文字列キー。各履歴にStaffIdを保持し、表示名の一致で結合しない。数値・日付の型と表示文字列を分け、0と空値を区別する。

| データ群 | 現行テスト件数 | 保持する内容 |
|---|---:|---|
| Staff | 25 | 基本9項目と検索項目 |
| Work | 27 | 適用期間・単価・勤務条件全項目 |
| Commute | 24 | 通勤認定ID・適用期間・支給方式・月別額等 |
| Social | 25 | 保険・共済・加入等全項目 |
| Resident | 25 | 徴収期間・税額等全項目 |
| Tax | 25 | 税表・固定控除等全項目 |
| Payroll | 25 | 概要列と全項目詳細 |

項目台帳は[field-inventory.json](field-inventory.json)を参照。これはv1.11から機械抽出した部品表示・テストレコードのキー一覧であり、本番データ辞書の代替ではない。基本9項目・履歴列・給与詳細15項目・69帳票フィールドについてv1.08との表示式一致を検査する。旧HTMLの業務書式は[参考詳細設計](../reference/html-v0.807-detailed.md)の8～11章を参照。旧JavaScript構造や接続URLは移植しない。
元HTMLは未知の列も動的表示するため、サンプルにない本番列が存在し得る。本接続前に実データの列台帳を取得して全項目照合すること。推測で列を削らない。

## 3. 状態遷移

| イベント | 更新順と結果 |
|---|---|
| 初期 | Tableを参照、25名、ページ1、先頭職員。起動イベント待ち不要 |
| 検索 | 条件を確定→AND抽出→ページ1→先頭選択または空→旧帳票とPDF解除 |
| クリア | 入力をReset→条件解除→全件→ページ1→先頭選択→旧帳票解除 |
| ページ前後 | ページを1～最終へ制限。結果集合は変えない |
| 行選択 | 選択キー更新→その職員の履歴表示→旧帳票とPDF解除 |
| サイドバー開閉 | 展開フラグだけを反転。検索条件・結果・選択キー・ページは変更しない |
| 認定簿 | 通勤レコード有無確認→対象ID・職員固定→差込→モーダル表示 |
| PDF作成 | 二重押下防止→対象帳票描画完了→生成→成功時Viewer/失敗時エラーと再試行 |
| 閉じる | モーダル閉鎖→元の起動ボタンへフォーカス復帰 |

検索条件は空を無条件、キーワードは前後空白を除去。氏名/番号に加え元仕様の検索対象を維持し、対象列は台帳で明記。番号は数値化しない。全角半角の自動正規化を追加する場合はテストを追加する。
履歴の状態は表示基準日と適用期間から判定し、現行・過去・予定を文字で表示する。未登録と該当なしを根拠なく推定しない。

## 4. 職員検索サイドバー開閉

v1.11で `varSearchSidebarExpanded111` を追加。初期値未設定も展開として扱い、App.OnStartへの依存は増やさない。

| 対象 | 式・仕様 |
|---|---|
| 開閉ボタン OnSelect | モーダル中以外で`Set(varSearchSidebarExpanded111, !Coalesce(varSearchSidebarExpanded111, true))` |
| サイドバー Width | `If(Coalesce(varSearchSidebarExpanded111, true), 360, 48)` |
| 検索内部 Visible | `Coalesce(varSearchSidebarExpanded111, true)` |
| 開閉ボタン | 同一ボタンを常時表示。44×44px。展開時は右上、閉鎖時は操作帯上端 |
| ボタン表示/説明 | 表示文字‹／›。AccessibleLabelとTooltipを「職員検索を閉じる」／「職員検索を開く」に切替 |
| 右詳細X | `conSearchSidebar111.X + conSearchSidebar111.Width + If(Coalesce(varSearchSidebarExpanded111,true),16,0)` |
| 右詳細Width | `Parent.Width - Self.X - 16`。折りたたみで328px拡張する |

- `conSearchSidebar111` は検索内部と常設開閉ボタンの親。`conLeftScroll111.Visible=false`にしてTab移動・読み上げ対象から外す。開閉ごとに別ボタンを生成しない。
- 職員行のOnSelectでは開閉フラグを変更しない。複数職員を続けて確認する操作を妨げない。
- 開閉操作では `txtKeyword`、ドロップダウン、抽出結果、選択職員番号、ページ番号、帳票対象をReset/Clear/Setしない。
- 再展開後は選択行が同じページに見えること。Galleryの任意スクロール量までの厳密な保持は完成条件にせず、選択行が確認できる位置への復帰でよい。
- 開閉後は起点ボタンへフォーカスを保つ。必要な環境では `SetFocus` を使うが、対象コントロールが対応することをStudioで確認する。
- Classic/Buttonには未対応の `AccessibleLabel` を記述しない。実際に出力したコントロールの対応プロパティを確認し、表示TextとTooltipを必ず設ける。
- 1366×768と1920×1080で、展開・折りたたみを繰り返しても右側の表、水平スクロール、モーダル位置が崩れないことを確認する。

## 5. 配置の実装原則

自動レイアウトではFillPortions/LayoutMinWidthを明示し、固定座標と混在させない。手動コンテナ/ギャラリーは各X/Y/Width/Heightを明示。列位置は前列X＋前列Widthから算出し、同じX=0の重複を検出する。
行高は最大セル高さ＋上下余白。ラベルと入力欄の高さ、親高さ、TemplateSizeを合わせる。文字を拡大したら親と行も拡大する。横幅不足は水平スクロールか折返しで解決し、極小幅を許さない。
トークンはデザイン基準に従い集約。ただし今回のデータ初期化不要という条件を維持する。App.Formulasを新依存にするなら単独ファイルと適用手順を必ず添える。

## 6. 帳票・出力

PDFViewerはScreen直下、Documentに生成PDF。モーダルの位置と表示条件は共有する。PDF対象に背面、ボタン、影を含めない。
現行はPDF実験機能が必要。SaveCommuteLedgerPdfは任意接続フローで、ファイル入力とfileurl応答を使う。接続しなければ保存完了を表示しない。既存fxはApp.FormulasではなくOnTimerEnd用。
2ページ改ページ、文字の欠け、拡大、保存ファイル名と対象職員、権限は実機で確認。現在A3横起点だが正式用紙サイズは未決。帳票背景は空様式PNGを内蔵しているため、外部画像URL接続は不要。
TSVコピーは現行の暫定出力。XLSX実装は別のフロー等を設計して承認し、数値型・先頭0・全項目・出力対象を検証する。

## 7. v1.11の部品・配置契約

- 実操作ボタンは`ModernButton@1.0.0`。検索入力は`ModernTextInput@1.0.0`、`Default`で初期値、`Text`で現在値を読む。`TriggerOutput.Keypress`を明示する。
- 組織・状態・用紙の3ドロップダウンは`Classic/DropDown@2.3.1`を維持。`Selected.Value`と`Default`/`Reset`の既存契約を保つための互換性例外。将来のモダン化は実環境コードを確認した個別パッチとする。
- 行選択の透明ヒット領域はClassic Button、表セルはLabel、帳票背景はImageを維持。透明行ボタンはText/Tooltip/可視フォーカスを使い、不正なAccessibleLabelを追加しない。
- `conMain111.Width=Parent.Width`。`conPerson111`を右の縦スクロールの外に配置し、`conRightScroll111.Y=conPerson111.Y+conPerson111.Height+12`とする。
- `conLeftSurface111`は自動レイアウトの子として`FillPortions=0`、最小寸法を自身の寸法に一致させる。孫のX/Yは手動配置。横長表もスクロール親＋寸法明示した手動Surfaceで分離する。
- 基本情報は行高64／大文字72。履歴は48／56。見出しとデータセルは同じ列位置・幅の式を使い、節Yは直前のY+Height+20とする。
- 検索一覧の氏名・在籍状態、番号・所属の4フィールドを保持。不要になった旧4列の見出しコントロールだけを撤去する。
- 勤務履歴に「適用状態」列を追加し、固定基準日2026/09/11による現行・過去・予定を文字表示。サンプルの金額・経路・保険判定を法定計算の検証結果と扱わない。
- 簡易出力は5行／ページ、64px行高。表示ページのみの印刷と全結果TSVコピーを区別し、正式認定簿PDFとは別機能にする。
- モーダル中は背面のボタン・入力・一覧をDisabled。検索／クリア／職員切替は旧帳票・PDFを破棄。開閉自体ではそれらを変更しない。

## 8. v1.12以降

[コントロール単位差分配布方針](../operations/control-diff-policy.md)を適用する。部品IDは111のまま固定。親・子・兄弟の参照を含む最小の完全サブツリーか、対象プロパティのPower Fxを配布する。貼付は追加操作であり自動上書きではない。GitHub完全版と管理版の同期は必須。

## 変更履歴

| 版 | 内容 |
|---|---|
| 1.03 | v1.11実装名、モダン部品、固定サマリー、状態保持、文字切替、差分契約へ更新 |
| 1.02 | v1.09向け職員検索サイドバーの変数、部品、式、状態保持、アクセシビリティを追加 |
| 1.01 | 現行部品・データ・B案状態遷移・配置・PDFの具体的実装契約を定義 |
