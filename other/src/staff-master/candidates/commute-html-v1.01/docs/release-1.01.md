# 通勤手当認定簿HTML版 1.01 — 実装・検証記録

## 状態

ユーザーの再開指示により、今回の60分制限は解除。A4横2ページ、JavaScript＋Dataverse Web API読取り、指定検証アプリとWebリソースの公開は承認済み。

動的HTMLとCanvas入口を実装・配置。**実環境のHTML表示、Web API接続・権限、Windows/EdgeのPDF保存は未確認。正式業務受入完了ではない。** クラウドブラウザのURL安全ポリシーが帳票へのアクセスを拒否したため、別経路・別ブラウザ・認証の持出しで回避していない。

## 変更

- 新規 `crb3c_reports/commute-ledger.html` を固定架空版から動的HTML版1.01へ更新。旧PoC `crb3c_poc/html-report-launch.html` は保持。
- 指定検証アプリ `検証専用_職員マスタ_20260918_残件` の `conLedgerHeader111` に `btnLedgerHtmlReport` を追加。ModernButton@1.0.0は現在の既存ヘッダーと同じコントロール版。
- ヘッダーHeightは `If(Parent.Width<1200,128,80)` から `If(Parent.Width<1200,180,132)` へ。帳票スクロール領域のY=`conLedgerHeader111.Height+8`、Height=`Parent.Height-Self.Y-12` が追従することを読取り確認。
- ヘッダーの変更前後コード比較で、既存子コントロールの定義は完全一致。変更は高さと新ボタンだけ。新規OnSelectとHeightをStudioで読戻し、数式エラーなしを確認。
- Studio数式編集の途中で式が重複入力される問題が発生。保存前に修正し、最終式・画面を再確認した。エラー状態を公開していない。
- `btnHtmlReportPoc`、既存認定簿・PDF/Downloadボタン、他Workの`ScreenContainer1`等は置換・削除しない。主アプリへの反映なし。データ・テーブル・権限の更新削除なし。

## データと安全策

`src/report.js`が同一オリジン `/api/data/v9.2/` へGETのみ送る。URLは認定主キーGUIDの`id`だけで、氏名・金額・認証情報を渡さない。Dataverse利用者本人の認証・Read権限・行アクセスが必要。ロール変更、新しいアプリ登録、Power Automateは追加していない。

| 項目 | データ元 |
|---|---|
| 認定 | `crb3c_commutes` / `crb3c_commuteid` |
| 親職員 | `_crb3c_staffbasicid_value` → `crb3c_staffbasics` / `crb3c_staffbasicid` |
| 氏名・番号・所属 | 現在の親レコードの `crb3c_fullname`, `crb3c_staffnumber`, `crb3c_orgshort` |
| 日付 | `crb3c_eventdate`, `crb3c_submitteddate`, `crb3c_receiveddate` |
| 経路1〜4 | `crb3c_route{1..4}_*` の既存13列。全選択列は`report.js`の`columns`で固定 |
| 合計・月別 | `crb3c_monthlytotal`, `crb3c_month04`〜`12`, `01`〜`03` |
| 未定義欄 | 空欄。非該当や0を推測しない |

親子GUIDと職員番号を照合してから表示。アプリ側でもモーダル保持認定・現在のギャラリー選択認定・保持職員・現在職員を照合する。未選択・不一致・対象なし・権限/通信エラー・20秒タイムアウトでは帳票を非表示にし印刷無効。textContentで挿入しHTMLとして解釈しない。NULLと0を区別し、独自の手当再計算なし。

EntitySetNameと列はリポジトリの現Dataverse定義／作成スクリプトを根拠とする。今回の実Web API読戻しは安全ポリシーで未実施。メタデータ確認・実データ照合の合格とは記載しない。

現行氏名・所属、金額の期間単位、未定義欄、長文運用の業務精査は [Issue #68](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/68) を継続する。

公式根拠:
- [HTML Webリソースとidパラメーター](https://learn.microsoft.com/en-us/power-apps/developer/model-driven-apps/webpage-html-web-resources)
- [Webリソース内JavaScriptのWeb API認証](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/authenticate-web-api)

## レイアウト

正式参考画像の欄構成をHTML/CSS化。A4横、余白5mm、本文287×199mm、2ページ目の直前で改ページ。普通交通8行（データは4明細まで）、自動車、併用、新幹線4行、駐車場3行、上限、4月〜3月、決定・返納欄を保持。初期候補で発生した下部欄の欠けとrowspanによる過大行高を修正。

氏名などは折返す。固定枠に収まらない経路・備考は黙って切らず、表示・印刷を停止する。最大100文字の経路や255文字の備考を常に2ページで出力できるものではない。最大長ケースはローカル検査で経路・備考のあふれを検出した。文字縮小やページ追加の業務判断はIssue #68で扱う。

## 検証結果

| 検証 | 実結果・限界 |
|---|---|
| Node単体 | 10試験群PASS。既存架空6件、GUID不正/重複、不一致、NULL/0、日付、HTML文字列、GET限定、HTTP/通信エラー、表示/印刷前のあふれ抑止。HTTPとDOMはモック |
| ローカル組版 | WeasyPrint 70.0＋日本語QAフォント。架空6件＋4明細ケースは全て297×210mmの2ページ、表がページ内、データ枠のあふれなし。`qa/layout-results.json` |
| PDF目視・解析 | TK-910003の全2ページを画像化して確認。日本語、罫線、下部欄、2ページ目の決定・返納欄あり。PDF寸法841.89×595.28pt。ブラウザ印刷の証跡ではない |
| 最大長 | 経路名称・出発地・備考のあふれを検出。完成帳票として合格にしない。DOM模擬試験ではあふれで帳票非表示・印刷無効・値消去を確認 |
| Studio入口 | 架空004/TK-910003で新ボタン表示・有効を確認。画面上の重なりなし。別タブを開く操作は安全ポリシー拒否の回避となるため未実施 |
| 検索0件 | 検索ボタンで0件を確定後、旧職員詳細・認定簿入口が消えることを確認。検索クリアで7件へ復帰 |
| 職員切替・認定なし | 架空008へ切替、通勤0件、既存認定簿ボタン無効を確認。004へ復帰 |
| 既存帳票 | 004の既存認定簿表示、閉じる、月額16,800等の表示を確認。既存PDF生成やTSVダウンロードの再試験は未実施 |
| 動的HTML・認証・実権限 | 未確認。クラウドブラウザの安全ポリシー拒否。一般利用者・権限なしアカウントでの実試験なし |
| Edge/Windows・1PDF保存 | 未確認。以前の固定PoC成功を今回の成功へ転用しない |

## 配置証跡

HTMLアップロード後のMaker「コード」欄を読み戻し、ローカルソースとの完全一致を確認（24,734文字）。SHA-256:
`70923fd131ed25b1f3f66925f7f58c410ddf222e80471746bcd2950387f21a70`

対象Webリソースの保存後、対象のみ公開し、Makerの「公開 に成功しました。」を確認。「すべてのカスタマイズの公開」は使用していない。

アプリはStudioの保存済み表示を確認した後、指定環境・指定検証アプリの公開ダイアログで「このバージョンの公開」を実行。公開バージョンの読戻し結果は`deployment.json`を参照。Studio終了時に編集ロックを解放。

## 利用・受入手順

1. 指定検証アプリを再読込み。架空職員004を選び、TK-910003の行を選択。
2. 「選択職員の認定簿を表示」→「HTML版（別タブ・2ページ）」を押す。
3. 必要なら普段の業務アカウントでサインイン。別タブの版表示が1.01、認定IDがTK-910003、氏名・職員番号・月額16,800円・月別値がアプリと一致するか確認。
4. 「印刷／PDF保存」。A4、横、倍率100%、ヘッダーとフッターなし、全ページを選ぶ。プレビューが2ページであることを確認し、1つのPDFとして保存。
5. 架空6件で照合、空欄・0・4明細・長文・対象なし・権限なし・通信失敗を確認する。権限拡大や実データ書換えで試験しない。
6. 実職員を使う前に上記受入結果を記録。共有する証跡は架空データのみとし、実職員・認証情報はGitHubやチャットへ貼らない。

本人のWindows/Edgeで確認が必要なため、現在は利用者の受入待ち。保存できた架空データのPDFを提供してもらえば、全2ページを解析・目視確認できる。

## 再生成・運用・戻し方

- `python src/build.py` → `src/commute-ledger.html`。JSやレイアウト変更後は必ず再生成する。
- `node --test tests/*.test.js`。固定版は`node tests/build-fixture.js`、追加ケースは`node tests/layout-cases.js`。
- ローカル組版確認はWeasyPrint 70.0とPyMuPDFを用意し、`python qa/check-layout-cases.py`。ブラウザの代用合格判定にしない。
- Canvas追加用`src/btnLedgerHtmlReport.paste.yaml`の`{DATAVERSE_ORIGIN}`は管理者が配置環境のHTTPS組織URLへ置換する。GitHubには環境固有URLを保存しない。
- 新ボタンの追加先は`conLedgerHeader111`。既に追加済みの場合は再追加せず、該当コントロールだけ差分反映する。ヘッダーHeightは上記式。完全画面の旧版で上書きしない。
- 不具合時は新ボタンを非表示にして保存・公開する。必要に応じてヘッダー高を旧式へ戻す。新Webリソースを固定架空版へ戻すと選択対象に関係ない値を表示するため、入口を有効にしたまま固定版へ戻さない。
- 旧PoC・既存ボタン・新Webリソースの削除は今回承認範囲に含めない。
