# 詳細設計書 v1.02

対象：v1.08を基にするB案開発。仕様目標と現行の実装名を以下で区別する。

## 1. ファイルと部品

管理用pa.yamlのScreens/scrStaffMasterSearch_v108/Childrenと貼付用paste.yamlのルート配列を同一にする。v1.09では画面・部品・変数の版識別子を一括更新し、v108参照の残存を検査する。

| 機能 | 現行部品 | 主なプロパティ |
|---|---|---|
| 検索 | txtKeyword108, ddOrg108, ddStatus108, btnSearch108 | Text/Selected/OnSelect |
| 結果 | galStaff108, lblListTitle108 | Items/Text |
| ページ | btnPrev108, btnNext108, lblPage108 | OnSelect/DisplayMode/Text |
| 詳細 | conPerson108, lblName108 | Visible/Text |
| 履歴 | galWork108, galCommute108, galSocial108, galResident108, galTax108, galPayroll108 | Items |
| 帳票 | btnCertificate108, conLedgerModal108, pdfLedger108 | OnSelect/Visible/Document |
| PDF保存 | tmrLedgerPdf108 | OnTimerEnd（任意フロー接続） |
| サイドバー | conSearchSidebar109, conSearchContent109, conSidebarRail109, btnSidebarToggle109 | Width/Visible/OnSelect/Tooltip |

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

項目台帳は[field-inventory.json](field-inventory.json)を参照。これはv1.08から機械抽出した部品表示・テストレコードのキー一覧であり、本番データ辞書の代替ではない。旧HTMLの業務書式・69帳票フィールドは[参考詳細設計](../reference/html-v0.807-detailed.md)の8～11章を参照。旧JavaScript構造や接続URLは移植しない。
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

v1.09で `varSearchSidebarExpanded109` を追加する。初期値未設定も展開として扱い、App.OnStartへの依存は増やさない。

| 対象 | 式・仕様 |
|---|---|
| 開閉ボタン OnSelect | `Set(varSearchSidebarExpanded109, !Coalesce(varSearchSidebarExpanded109, true))` |
| サイドバー Width | `If(Coalesce(varSearchSidebarExpanded109, true), 360, 48)` |
| 検索内部 Visible | `Coalesce(varSearchSidebarExpanded109, true)` |
| 折りたたみ操作帯 Visible | `!Coalesce(varSearchSidebarExpanded109, true)` |
| ボタン表示/説明 | 展開時「検索を閉じる」、折りたたみ時「検索を開く」。Tooltipも同じ状態に追従 |
| 右詳細 | サイドバー幅と展開時の列間を引いた残幅。固定の左360pxを残さない |

- `conSearchSidebar109` は展開内容と折りたたみ操作帯の親とし、親幅を開閉する。検索内容を幅0にするだけではなく `Visible=false` にしてTab移動・読み上げ対象から外す。
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

## 変更履歴

| 版 | 内容 |
|---|---|
| 1.02 | v1.09向け職員検索サイドバーの変数、部品、式、状態保持、アクセシビリティを追加 |
| 1.01 | 現行部品・データ・B案状態遷移・配置・PDFの具体的実装契約を定義 |
