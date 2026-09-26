# 通勤手当認定簿 HTML版 1.00 候補 — 2026-09-20中断記録

**未完成・実運用不可。公開済みなのは固定架空データのレイアウト確認版のみ。**

## 承認・対象

ユーザーの今回指示でA4横2ページへ確定。JavaScriptによるDataverse Web API読取り方式と公開を承認。暫定項目対応は承認され、後日精査をIssue #68へ登録した。新たな権限拡大、PoC置換・削除は対象外。

今回の対象は既存検証専用アプリの追加帳票。既存メインアプリ、既存PoCボタンとPoC Webリソース、他Workの変更を保持する。環境固有URL・認証情報・実データは本記録に含めない。

開始記録は2026-09-20 14:23 UTC頃。17:43 UTCの時刻確認で運用方針の60分停止期限超過を認識し、新規実装・アプリ変更を停止した。期限内に停止できなかった点は運用上の不備。以下は停止時の記録。再開時はユーザーの再開指示を確認し、承認済みの方式・公開承認は再取得しない。

## 現状照合

- mainの基準コミット: `e8a6de4f01f614cb96db0e61f539a51481c5457a`。停止時にも同一。
- 作業ルール: `AGENTS.md`、`docs/operations/work-policy.md`、`docs/handoff/STATUS.md`。
- PoC記録: `docs/poc/html-report-launch-poc.md`。元PoCはA4縦の簡易固定値。今回の正式様式は横2ページ。
- 最新資料の背景画像 `assets/commute-ledger/ledger-page1-template.png`、`ledger-page2-template.png` と既存帳票設計を照合。
- 検証専用アプリのStudioとプレビューを読取り確認。既存 `btnHtmlReportPoc` のHTTPS Launch、3つのDataverse接続、`btnCertificate111` の選択認定／職員チェックを確認。アプリの保存・公開・変更は未実施。編集ロック上書きなし。
- 既存画面で架空職員004／TK-910003／月額16,800円を確認。画面初期部署フィルターは03会計課で7件。過去記録の全25件と混同しない。
- ソリューションのWebリソース一覧はPoCのみから2件へ増加。新規 `crb3c_reports/commute-ledger.html` を作成。旧PoCは変更しない。

## 正式様式と項目対応

| 帳票欄 | 読取り元／扱い |
|---|---|
| 氏名・職員番号・所属 | `crb3c_staffbasics`: `crb3c_fullname`, `crb3c_staffnumber`, `crb3c_orgshort`。現在のマスタ値（履歴時点値ではない） |
| 認定主キー | `crb3c_commuteid`。URLはこのGUIDのみ。認定番号は一意キーにしない |
| 職員参照 | `_crb3c_staffbasicid_value` → `crb3c_staffbasicid`。親子の職員番号一致も検査 |
| 認定表示番号 | `crb3c_recognitionid`。ツールバーに表示 |
| 事実発生・届出・受理日 | `crb3c_eventdate`, `crb3c_submitteddate`, `crb3c_receiveddate` |
| 適用期間 | `crb3c_startdate`, `crb3c_enddate`。ツールバーに表示 |
| 普通交通機関1〜4 | `crb3c_route{1..4}_{operator,from,to,tickettype,ticketbasis,distancekm,ticketamount,passamount,passmonths,amount,recognitionstart,paymonth,remarks}` |
| 普通交通機関5〜8 | 元様式の欄を残して空欄。現定義は4明細 |
| 月額合計 | `crb3c_monthlytotal`。独自再計算なし |
| 4月〜3月の支給額 | `crb3c_month04`〜`crb3c_month12`, `crb3c_month01`〜`crb3c_month03` |
| 自動車、新幹線、駐車場、決定、返納、平均所要回数・算出式 | 対応列が未確定／未定義のため空欄。非該当・0と断定しない |

route2〜4のamount列の名称と月数の意味、現在氏名・所属の使用、回数／距離／定期期間の対応、未定義欄の運用は [Issue #68](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/issues/68) で後日精査する。架空テストのNULLと数値0は区別する。住所は採用様式・現対応項目に独立の印字欄を設けていない。住所を含む長い経路文字列も含め、長文実描画試験は未実施。

## 実装候補

`src/report.js` はDataverse同一オリジンのWeb APIへGETを2回実施する。認定GUIDを検証し認定を取得、親参照の職員を取得し、対応が確認できてから帳票を表示。氏名・金額をURLに載せない。認証トークンの取得・保存、外部CDN、Power Automate、追加アプリ登録は使用しない。

401/403/404、通信・タイムアウト、形式不正、親子不一致では帳票を隠し、印刷ボタンを無効化。値はtextContentで設定し、HTMLとして解釈させない。空欄と0を区別。文字やページの収まりを実測し、はみ出した場合は帳票を表示せずエラーにする。長文が全件印刷できる保証はまだない。

`src/build.py` はHTML/CSSとJavaScriptを単一HTMLへ組み立てる。`@page size:A4 landscape; margin:5mm`、2つの固定ページ要素、2ページ目直前の改ページを指定。ページ数はCSS指定だけでは合格にしない。

DataverseのRead権限は利用者のセキュリティロール・行アクセス・列セキュリティに従う。識別子は権限を代替しない。今回ロール変更なし。実環境の一般利用者・権限なしアカウントでの検証は未実施。

公式仕様（2026-09-20確認）:
- [HTML Webリソースと許可されたidパラメーター](https://learn.microsoft.com/en-us/power-apps/developer/model-driven-apps/webpage-html-web-resources)
- [Webリソース内JavaScriptのWeb API認証](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/authenticate-web-api)

## 配置済み／未配置

| 対象 | 停止時点 |
|---|---|
| 新規Webリソース `crb3c_reports/commute-ledger.html` | `qa/layout-fixture.html` をアップロード、保存、対象のみ公開。Makerの「公開 に成功しました。」を確認。**固定架空TK-910003、実データ取得なし** |
| 動的 `src/commute-ledger.html` | ソース候補のみ。未アップロード、未公開 |
| アプリ新ボタン | 未追加。アプリの保存・公開なし |
| 既存PoCボタン／リソース | 保持。削除・変更・置換なし |
| Dataverseレコード／スキーマ／権限 | 更新・削除・変更なし |

停止時、Makerは新規リソースの編集ダイアログを開いた状態（新しい変更の入力なし）。公開済み候補のHTML表示・PDF保存は未確認。実データ連携成功と扱わない。

## 試験結果

Nodeの `node --test tests/report.test.js` は6試験グループ全てPASS。既存架空6レコードに対し、金額／月別値／NULL・0、GUID入力・重複パラメーター、親子不一致、日付・元号境界、マークアップの文字列扱い、GET限定・same-origin・no-store・認証/通信エラー処理を検査した。HTTPはモックであり、実環境の認証・権限・接続成功を示さない。

| 工程 | 結果 |
|---|---|
| 1 現状確認 | 成功。資料と現在Studio・架空レコード画面を照合 |
| 2 Issue・方式整理 | 成功。Issue #68登録、承認範囲記録 |
| 3 HTML/CSS・読取り処理 | 一部実施。候補実装、固定版のみ配置。描画調整未完 |
| 4 検証 | 一部実施。単体6グループPASS。実接続・印刷・長文描画は未実施 |
| 5 アプリ追加・公開 | 未実施。固定HTML候補の公開のみ成功 |
| 6 GitHub記録 | 中断時点の候補ソース・状態を保存。正式完了ではない |

## 再開手順／残件

1. main、他Workの変更、アプリ保存状態・ロック、新規Webリソース内容を再確認。旧ソースで全画面上書きしない。
2. 固定架空版を開き、全2ページを視認・計測。特に1ページ目の見出し＋8行＋合計の総高さ、2ページ目の決定・返納欄を調整。現CSSははみ出しの可能性が残る。認定期間・支給月・定期券月数の単位表記も確認。
3. ブラウザ印刷でA4横、100%、余白5mm相当、ヘッダー／フッターなし、全2ページ・1PDFを確認。UIの日時／URLはCSSだけでは強制抑止できないため印刷設定で無効にする。
4. 現DataverseのEntitySetNameと列型を読戻し確認してから動的版へ切替。現在コードの`crb3c_commutes`は定義からの候補で、実API接続は未確認。
5. 既存架空6件を使い、名前・日付・全経路・金額・月別値をアプリと比較。未選択、対象なし、権限なし、通信失敗、長文、空欄、複数明細を実描画確認。権限試験のための権限拡大をしない。
6. 選択中の`galCommute111.Selected`と`StaffSelected`の整合を確認してGUIDのみをLaunchする新ボタンを追加。`Text(c.T_通勤)`を候補としてStudioで検証。既存PoCは保持。
7. 差分を読み戻して指定検証アプリだけ保存・公開。ユーザーの公開承認は既にある。既存検索・職員切替・0件・旧帳票のスモークを実行。
8. Windows/Edgeでの認証、別タブ、A4横2ページPDFを確認。クラウドブラウザ結果と区別する。実施できない試験は未確認として記録。

戻し方: 現時点ではアプリに入口を追加していないので既存フローへの影響はない。新規候補は削除せず、次版への更新対象とする。将来ボタン追加後に問題が判明した場合は新ボタンを非表示にし、旧PoCには手を加えない。
