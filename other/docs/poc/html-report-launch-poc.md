# Power Apps HTML帳票 Launch PoC 検証結果

## 最終検証結果（2026-09-20・ユーザー環境で成功）
**HTTPS方式PoC：成功。PoCは削除指示まで継続・保持。**
ユーザーがアカウント選択後の別タブHTML表示とPDF保存を報告。添付HTML帳票PoC.pdfを解析・全2ページを画像化して目視し、A4縦2ページ、日本語、罫線、意図した改ページ、1ファイルへの保存を確認した。クラウドブラウザでの未検証をユーザー環境の実測で補完。元のdata URL方式の失敗とは区別する。

## 明示承認後・ユーザー検証前の状態（2026-09-20）
**部分成功・継続中。HTTPS版PoCボタンを保存し、アプリ再読込後も同じ式が保持されることを確認済み。**
ユーザーが、既存Dataverseへの固定HTML配置とHTTPS方式への変更を当初制約の例外として明示許可。btnHtmlReportPocを1個保持。HTML Webリソースも保持。Canvasアプリの公開は今回行っていない。
帳票の直接表示は前回成功。今回のボタン経由表示・印刷・PDFはクラウドブラウザのURL安全ポリシー制限により未検証。権限追加なし。本番帳票フェーズへ進んでいない。

## 明示承認前の状態（2026-09-20）
再認証してStudioへ復帰。旧data URL版ボタンが残っていたことを確認。HTTPS版への入替は自動安全審査で拒否されたため中止し、元のdata URL版ボタンを復元した。ボタン定義974文字・OnSelect全文一致を読戻し確認。保存操作を実行したが今回の保存済み時刻表示は取得できていない。公開なし。HTTPS版の実行・印刷・PDF検証は未完了。

## HTTPS方式の前回中断時点（2026-09-20）
**部分成功・継続中：DataverseのHTML登録・公開・直接表示に成功。ボタン切替中に作業環境が切断され、Launch経由・印刷・PDFは未検証。**
追加権限の付与・変更なし。Webリソースは保持。ボタン入替操作の応答が失われたため、現在のボタン残存状態は再接続後に確認してHTTPS版1個を確実に残す必要がある。完了扱いにしない。

## HTTPS方式への変更前の状態（2026-09-20追記）
**PoC継続中。ユーザーの削除指示があるまでボタン・機能を保持する。**
2026-09-20の追加指示により、当初の「検証後に完全削除」を上書きした。検証専用アプリのscrHomeにHTML帳票PoCボタンを再追加し、下記の元の2ページHTML式を保存済み。公開は行っていないため、Studioの保存済み編集版で利用する。
最新の対照試験：通常HTTPSのLaunchTarget.Newは別タブ成功、17文字のdata URLは別タブ不成立。方式の判定は引き続き今回環境で失敗だが、PoC自体は終了扱いにしない。

## 初回検証の結論（2026-09-19時点）
**判定：失敗（今回のクラウドChrome／Power Apps Studioプレビュー環境）。**
Power Apps内に一時ボタンを実装して押下したが、data:text/htmlの別タブ・HTML表示に到達しなかった。印刷・2ページPDF保存は未実施。公開PlayerやEdgeでの実現不可まで断定する結果ではない。
PoC機能は完全削除し、変更対象scrHomeの開始前後の定義11529文字が完全一致。復元保存と通常検索の確認を完了。本番帳票フェーズには進まない。

## 目的・実施日・対象
- 検証日：2026-09-19（UTC/JSTとも同日）。再開後の復元動作確認・本記録作成を含む。
- 目的：Power Apps → HTML生成 → Launch → 別タブ → ブラウザ印刷 → A4縦2ページを1つのPDFへ保存できるか。
- 環境：StaffMaster-Automation-Test。
- アプリ：検証専用_職員マスタ_20260918_残件、画面表示v1.26。
- App ID：28006813-32bb-49c8-810e-5141f1b3bfdc。
- 実行：Power Apps Studioのプレビュー。クラウドブラウザのChrome。ブラウザ詳細バージョン・OS・ブラウザ拡大率100%は未確認。
- 元の自動開発_職員マスタ検索とDataverseは変更なし。PoC状態の保存・公開を意図して実施していない。削除後の復元状態を明示保存した。Studioの自動保存履歴に一時定義が残る可能性と、現行定義からの削除は区別する。
- STATUSにあった別作業の「HTML帳票PoC除外」は、本会話のユーザーによる「実行して」を優先。本書は別PoCの記録であり、既存95項目の合否は変更しない。

## 実装
ホームscrHomeにボタン1個「HTML帳票PoC」を一時追加。最終検証用コントロール名btnHtmlReportPoc、ModernButton@1.0.0、X40/Y650/幅180/高さ40。専用変数・データソース・追加システムなし。
Power Apps標準のコード貼付でボタンを追加し、処理はPower Fxのみ。読戻し974文字のボタン定義に、下記789文字のOnSelect全文が完全一致することを確認してから実行した。

### OnSelect
```powerfx
Launch("data:text/html;charset=utf-8," & EncodeUrl("<!DOCTYPE html><html lang='ja'><head><meta charset='UTF-8'><title>HTML帳票PoC</title><style>@page{size:A4 portrait;margin:10mm}body{margin:0;font-family:'Meiryo',sans-serif}.page{box-sizing:border-box;width:190mm;min-height:277mm}.page-break{break-before:page;page-break-before:always}table{width:100%;border-collapse:collapse}th,td{border:1px solid #000;padding:6px}</style></head><body><div class='page'><h1>通勤手当認定簿 PoC</h1><h2>1ページ目</h2><table><tr><th>職員番号</th><td>000123</td></tr><tr><th>氏名</th><td>テスト 太郎</td></tr></table></div><div class='page page-break'><h1>通勤手当認定簿 PoC</h1><h2>2ページ目</h2><table><tr><th>通勤方法</th><td>電車</td></tr><tr><th>備考</th><td>Power Apps HTML帳票出力検証</td></tr></table></div></body></html>"), {}, LaunchTarget.New)
```

### 使用HTML/CSS（712文字）
```html
<!DOCTYPE html><html lang='ja'><head><meta charset='UTF-8'><title>HTML帳票PoC</title><style>@page{size:A4 portrait;margin:10mm}body{margin:0;font-family:'Meiryo',sans-serif}.page{box-sizing:border-box;width:190mm;min-height:277mm}.page-break{break-before:page;page-break-before:always}table{width:100%;border-collapse:collapse}th,td{border:1px solid #000;padding:6px}</style></head><body><div class='page'><h1>通勤手当認定簿 PoC</h1><h2>1ページ目</h2><table><tr><th>職員番号</th><td>000123</td></tr><tr><th>氏名</th><td>テスト 太郎</td></tr></table></div><div class='page page-break'><h1>通勤手当認定簿 PoC</h1><h2>2ページ目</h2><table><tr><th>通勤方法</th><td>電車</td></tr><tr><th>備考</th><td>Power Apps HTML帳票出力検証</td></tr></table></div></body></html>
```

A4縦、余白10mm、190mm幅、277mm最小高さ、2ページ目の改ページ指定を含む。ただし記述が存在することと、印刷で有効であることは別。実際の印刷ページ数は未検証。

### URL長・EncodeUrlの切り分け
2ページHTMLの参考エンコード長は1501文字（記録作成側のencodeURIComponent換算）。**Power Fxが実際に渡したURL長の実測ではない**。Power Fx EncodeUrlとLaunch内部のエンコードの差は未測定。
追加試験ではHTML・日本語・CSS・EncodeUrlを除き、17文字のASCII data URLを使用した。

```powerfx
Notify("PoC開始",NotificationType.Information); Launch("data:text/html,PoC",{},LaunchTarget.New); Notify("PoC終了",NotificationType.Information)
```

このボタン押下後に「PoC終了」が表示されたが、新規タブは増えず既存7タブのままだった。したがって今回の不成立を長いHTML、CSS、日本語、EncodeUrlだけで説明することはできない。Launchが内部でどのようにURLを扱ったかは未確定。

## テスト結果
| 項目 | 結果 | 観測・限界 |
|---|---|---|
| 検証ボタン追加・押下 | PASS | 表示と押下を確認 |
| 最終実装式の読戻し | PASS | 予定OnSelect789文字の全文一致 |
| エラーなく処理実行 | 部分確認 | 最小式はLaunch後のPoC終了を表示。Launch成功を意味しない |
| 新しいブラウザタブ | FAIL | 完全HTML式および短いdata URL式で増加なし |
| HTML表示 | 未到達 | 新規帳票タブなし |
| 日本語文字化けなし | 未実施 | 帳票HTML未表示。アプリの日本語表示を代用しない |
| 1・2ページ目を表示 | 未実施 | HTML未表示 |
| 表罫線 | 未実施 | CSS定義のみ |
| ブラウザ印刷画面 | 未実施 | 帳票HTML未表示 |
| 印刷プレビュー2ページ | 未実施 | 前提未成立 |
| PDF保存可能な構造 | 未確認 | CSSの存在のみでは合格にしない |
| 2ページを1PDF保存 | 未実施 | PDFファイル未生成 |
| Edge | 未実施 | 今回はChrome |
| ブラウザ拡大率100% | 未確認 | Studioキャンバスの40%とは別 |
| A4縦・意図しない分割なし | 未実施 | CSS指定のみ、印刷未検証 |
| 公開PlayerからのPoC実行 | 未実施 | Studioプレビューで試験を終了 |
| PoC機能削除・復元 | PASS | scrHome全文が開始前と完全一致 |
| 復元保存 | PASS | All changes are saved. / Saved: 9/19/2026, 2:52:54 PM（UI表示時刻、タイムゾーン表記なし） |
| 復元後の通常動作 | PASS（限定スモーク） | ホーム→職員検索7件→011検索1件・選択011→クリア7件→ホーム。全回帰試験の代用ではない |

### 成功条件6項目
①別タブ：不成立。②HTML帳票表示：未到達。③日本語正常：未検証。④2ページを1HTMLとして扱える：定義作成のみ、実表示未検証。⑤印刷2ページ：未検証。⑥1PDF保存：未検証。
実装できたことだけでは「部分成功」とせず、目的フローが入口で不成立のため上記環境で失敗と判定する。

## エラー・技術的制約と切り分け
- 開始時StudioのSession expiredをResume this sessionで再開し、編集可能になった。
- 初回の数式欄への自動入力では既存falseが末尾に残り、Expected operator診断が発生。該当一時ボタンButton1を削除して解消。これをdata URL方式そのものの失敗根拠にしない。
- 初回のYAMLプレーン値ではCSSの「 #000」がコメント扱いになり式が欠落。該当ボタンを削除し、OnSelectをブロックスカラーにして再作成、全文一致確認で解消。
- 最終完全式の押下は通常クリックと座標クリックで確認したが、帳票タブは現れなかった。
- 17文字data URL、EncodeUrlなしでも同様。「PoC終了」表示によりボタン処理の実行・後続到達を確認。
- 取得したログにLaunch失敗理由を直接示す診断は得られなかった。拡張機能のError sending browser metadata to extension: Objectは観測したが、Launch不成立の原因とは断定しない。
- ブラウザ側data URL遷移制約、Power Apps側URL取扱い、Studioの埋込実行、ポップアップ抑止のどこが今回の直接原因かは未確定。HTTPS対照試験、公開Player試験は未実施。

## 公開資料による補足（実測と区別）
- [Microsoft Learn: Launch and Param](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-param)：LaunchTarget.Newは新しいウィンドウ／タブを指定する。引数のレコード形式、URLエンコードの説明あり。この資料だけではdata:text/htmlの成功を保証できない。
- [MDN: data URLs](https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Schemes/data)：フィッシング等の対策として、現代ブラウザはdata URLへのトップレベル遷移をブロックすると説明。
- 推論：data URLの遷移制約と今回の挙動は整合するが、今回の直接的な拒否箇所をログで特定したわけではない。

## セキュリティ・制約順守
架空の職員番号000123・氏名テスト 太郎のみをHTMLへ埋め込んだ。実データ取得・入力値連携・正式帳票・PDF()・Power Apps Print()・Power Automate・SharePointファイル生成・Excel生成・外部帳票サービス・Power Apps外のJavaScript実装は行っていない。
ブラウザのセキュリティ設定やポップアップ設定を弱める操作、data URL制限回避もしていない。将来URLへ実データを含める方式は、URLに含まれるデータの扱いを別途確認する。

## 撤去・復元証跡
1. 入力試行のButton1を削除。以降のbtnHtmlReportPocも都度交換し、最終的に削除。
2. 専用変数なし。HTML/CSSと短縮式はボタンのOnSelectだけに持たせたため、削除で現行アプリから撤去。
3. StudioのView code→Copy codeでscrHomeを開始前後に取得。双方11529文字、文字列完全一致true。
4. 復元後コードにbtnHtmlReportPoc、HTML帳票PoC、data:text/html、Button1:がないことを確認。
5. 復元状態を保存し、All changes are savedと保存時刻を確認。
6. PoCボタン0件、通常検索の限定スモーク合格、通常ホームへ復帰してプレビュー終了。
7. 今回PoCは公開していないため、PoC公開版を残した状態にはなっていない。元公開アプリを変更していない。古いPublish successful通知を今回の公開証跡に使用しない。

## 次フェーズ
**本番2ページレイアウト・実データ埋込フェーズには進めない。**
今回の条件で技術成立性を確認できなかった。公開Player・Edgeなどの追加試験をする場合は今回の未検証範囲を引き継ぐ。方式変更・本番帳票実装は別途ユーザー指示を受けてから行う。

## 追加原因調査（2026-09-20）

### 「簡易画面」の実体
別タブに表示しようとしたものは、ボタンのOnSelect内に文字列として定義した独立したHTML文書である。Power AppsのScreenコントロールを追加したものではない。HTMLファイルの生成、HTTPSでの帳票公開、帳票用Screenの作成はいずれも行っていない。2つのdiv.pageは印刷用のページ区切りであり、Canvasアプリの2つのScreenではない。

### 同一環境での対照試験
対象：同じ検証専用アプリv1.26、クラウドChrome、Studioプレビュー。scrHomeに同じ位置・サイズ・名称のボタン1個を用い、式を順に入れ替えた。試験前のscrHome定義を取得（11529文字）。

HTTPS対照式：
```powerfx
Notify("HTTPS開始",NotificationType.Information); Launch("https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-param",{},LaunchTarget.New); Notify("HTTPS終了",NotificationType.Information)
```

最小data URL式：
```powerfx
Notify("data開始",NotificationType.Information); Launch("data:text/html,PoC",{},LaunchTarget.New); Notify("data終了",NotificationType.Information)
```

| 試験 | 結果 | 実測 |
|---|---|---|
| HTTPS対照 | 成功 | タブ数2→3。新規タブにMicrosoft LearnのLaunch and Paramページ。HTTPS終了通知あり |
| 17文字data URL | 失敗 | タブ数3のまま。data終了通知あり。新規HTML表示なし |
| 診断式の確認 | 合格 | 両式ともStudioのコード表示で指定したOnSelectを確認 |

### 原因の絞り込みと限界
- 同じ操作・LaunchTarget.NewでHTTPSが成功したため、別タブ機能全体の故障や全ポップアップ一律遮断を原因とする説明は当てはまらない。
- 17文字、ASCIIのみ、EncodeUrlなしでも失敗したため、日本語・CSS・2ページ構造・長いHTML・EncodeUrlは失敗の必須条件ではない。
- 問題はdata URLをLaunchから遷移させる経路に絞られた。MDNが説明するdata URLへのトップレベル遷移のセキュリティ制約と整合する。
- **ブラウザ側のdata URL制限が有力。ただし、Power Appsが事前に拒否したのか、ブラウザが拒否したのかという直接の拒否箇所は未確定。** 今回、それを特定する直接的なエラーログは得ていない。
- 後続Notifyの表示は式の後続到達を示すだけで、Launch成功の証明ではない。
- 簡易な帳票へ縮小するだけでは、この遷移制約の解消にはならない。独立したCanvas Screenへの変更は別方式であり、このdata URL方式の成立を証明しない。
- 公開Player、Edge、印刷、PDF保存は追加検証していない。HTML表示以前の不成立のため、印刷CSSの良否は判断しない。

根拠資料：[Microsoft Learn — Launch and Param](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-param)、[MDN — data URLのSecurity issues](https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Schemes/data#security_issues)。仕様と実測、原因推定を区別して記録した。

### 最新の保持・保存状態
- ユーザー追加指示：「成功/失敗どちらでもボタンや機能は残す。削除してというまでPoCは続いている」。この指示を当初の削除条件より優先。
- HTTPS対照式・最小data式から、上記「OnSelect」に記録した元の2ページHTML式へ戻した。
- btnHtmlReportPocを1個保持。ボタン定義974文字の読戻しに元のOnSelect全文が含まれることを確認（完全一致true）。専用変数、追加Screenなし。
- 明示保存後、「すべての変更が保存されます。」「保存済み: 2026/9/20 9:17:51」を確認（UI表示時刻、タイムゾーン表記なし）。
- 公開操作は行っていない。画面に残っていた2026/9/19のPublish successful通知は今回の公開証拠ではない。
- 保存後スモーク：ホーム→職員検索7件→009900000011で1件・選択011→条件クリア7件→ホーム。HTML帳票PoCボタンの残存を確認してプレビュー終了。
- 全回帰試験は未実施。元アプリやデータ定義は編集していない。本番帳票フェーズへは進んでいない。
- 上記の撤去・復元証跡は2026-09-19時点の履歴として保持する。現在は削除済みではなく、検証専用アプリの保存済み編集版にPoCを残している。

## Dataverse HTML Webリソース方式の実施（2026-09-20）

ユーザーの「それでやってみて。権限追加必要なら許可します」に基づき、事前登録した固定HTMLをHTTPSで開く案を実施。元のdata URL方式とは区別する。

### 登録済みリソース
- 環境：StaffMaster-Automation-Test（68e00049-b7e5-eda6-9888-9a3cc493c5be）。
- ソリューション：職員マスタ自動化 / StaffMasterAutomation（25438a80-0a18-4ac8-bdce-5e328ef23297）。
- 表示名：HTML帳票PoC（2ページ・固定値）。
- 名前：crb3c_poc/html-report-launch.html。
- 種類：Web ページ (HTML)。
- リソースID：48e1393d-8cb4-f111-aaad-e4fb1eff79c7（管理画面から開いた編集URLで確認）。
- URL：https://orge762dd9e.crm7.dynamics.com/WebResources/crb3c_poc/html-report-launch.html
- 新規保存後、当該リソース行の「公開」を実行。「公開 に成功しました。」を確認。「すべてのカスタマイズの公開」は使用していない。
- 追加のロール付与や権限変更なし。元のCanvasアプリ・既存テーブルの定義変更なし。

### 実際に登録したHTML/CSS
```html
<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HTML帳票PoC</title><style>@page{size:A4 portrait;margin:10mm}*{box-sizing:border-box}body{margin:0;color:#000;background:#fff;font-family:"Meiryo","Noto Sans CJK JP",sans-serif}.page{display:flow-root;width:190mm;min-height:276mm;break-inside:avoid;page-break-inside:avoid}.page-break{break-before:page;page-break-before:always}h1{margin:0 0 8mm;font-size:22pt}h2{margin:0 0 6mm;font-size:16pt}table{width:100%;border-collapse:collapse}th,td{border:1px solid #000;padding:6px;text-align:left}th{width:35%}@media screen{body{padding:10mm}.page{margin:0 0 10mm;outline:1px solid #bbb}}</style></head><body><div class="page"><h1>通勤手当認定簿 PoC</h1><h2>1ページ目</h2><table><tr><th>職員番号</th><td>000123</td></tr><tr><th>氏名</th><td>テスト 太郎</td></tr></table></div><div class="page page-break"><h1>通勤手当認定簿 PoC</h1><h2>2ページ目</h2><table><tr><th>通勤方法</th><td>電車</td></tr><tr><th>備考</th><td>Power Apps HTML帳票出力検証</td></tr></table></div></body></html>
```
元の固定データを維持。見出しの既定余白によるはみ出しを避けるため余白を明示し、pageをflow-root、最小高さ276mmとした。A4の印刷可能高さ277mmに1mmの余裕を設けた。画面用の枠・余白は@media screenだけに指定。これらは印刷成功の実測を意味しない。

### ボタンに設定する予定式（未反映・未検証）
```powerfx
Launch("https://orge762dd9e.crm7.dynamics.com/WebResources/crb3c_poc/html-report-launch.html", {}, LaunchTarget.New)
```

### 実測結果
| 項目 | 結果 | 証跡・限界 |
|---|---|---|
| HTML登録 | PASS | 新規登録行を確認 |
| 対象Webリソース公開 | PASS | 公開成功通知 |
| HTTPS URLを直接開く | PASS | 新規タブで帳票DOMを確認。Launch経由とは区別 |
| 日本語・固定データ | 部分確認 | 見出し、職員番号000123、テスト 太郎、電車、備考をDOM上で確認。スクリーンショットによる字形確認は未実施 |
| 1・2ページ目の内容 | PASS（文書構造） | 同一HTMLに両見出し・2表を確認。印刷ページ数とは区別 |
| 表罫線・見た目 | 未確認 | CSS定義のみ。画像での目視未実施 |
| ボタンのHTTPS切替・Launch | 未完了 | 入替途中のツール通信切断 |
| 印刷画面・2ページ認識・PDF保存 | 未実施 | 作業環境オフライン |
| Edge・ズーム100% | 未実施 | 同上 |

### 切断と次回の再開点
1. 既存btnHtmlReportPocを選択した後、HTTPS版に入れ替えるため「その他のオプション→削除」の操作を送った時点で通信切断。これは撤去して終了する操作ではなく、同名ボタンを再作成する編集手順の途中。
2. 応答：exec-server transport disconnected、続いて409 Conflict / environment_offline / Environment is not connected。再試行でも回復せず。
3. このため削除が実行されたかは不明。削除されたとも、ボタンが残っているとも断定しない。HTTPS式の貼付・保存は未実施。
4. 再接続時はStudioの現在状態を確認し、同名ボタンがあればOnSelectを切替、なければ同名・同位置のボタンを1個再追加。保存・コード読戻し後にLaunchで開く。
5. 続いて表示の目視、ブラウザ印刷、A4縦2ページ・1PDF保存を検証し、必要な印刷CSSだけ調整する。
6. ユーザーの削除指示までHTML WebリソースとPoCボタンを保持する。本番帳票・実データ連携には進まない。

現時点は方式変更PoCの部分成功であり、成功条件6項目を満たしたとは判定しない。次フェーズ移行は未承認・未実施。

## 再開時の制限と復旧（2026-09-20）
- クラウドブラウザを再接続し、Microsoft再認証後、検証専用アプリを開いた。
- 登録済みHTTPS帳票を再確認しようとしたところ、クラウドブラウザからURL安全ポリシーによる拒否が返った（requested URL protocol is not allowed）。原因となった内部遷移は特定していない。帳票自体の仕様不成立や権限不足とは断定しない。回避操作・別経路での表示試行は行っていない。
- StudioではbtnHtmlReportPocが残っていた。HTTPS版への入替のため旧ボタンを削除した後、HTTPS版の準備操作が自動安全審査で拒否された。審査理由は当初の外部サービス禁止との範囲不整合。ユーザーの直前の方式変更指示はあるが、審査から明示的な再承認を要求されたため、同じ操作を再試行していない。
- 「削除指示まで残す」に従い、元のdata URL版を同名・同位置で復元。コード読戻し974文字、元OnSelect全文一致true。保存操作実行、公開操作なし。保存済み時刻のUI証跡は取得できず、次回確認する。
- HTTPSのWebリソースは削除していない。追加ロール付与やセキュリティ設定変更もなし。
- 次回は固定架空データのHTMLを既存Dataverseへ置き、検証専用アプリのボタンをそのURLへ変更することが、当初制約の例外として承認されていることを明示確認する。ブラウザ側のポリシー制限は別問題であり、承認だけで解消するとは扱わない。

## 明示承認後のHTTPS切替・保存確認（2026-09-20）
- ユーザーが「許可する」と回答し、当初制約の例外としてDataverse固定HTML・HTTPS Launchへの変更を承認。
- 検証専用_職員マスタ_20260918_残件（App ID 28006813-32bb-49c8-810e-5141f1b3bfdc）のscrHomeに、同名btnHtmlReportPocを1個配置。位置X40/Y650、幅180/高さ40、Text「HTML帳票PoC」。
- 実装したOnSelect：
```powerfx
Launch("https://orge762dd9e.crm7.dynamics.com/WebResources/crb3c_poc/html-report-launch.html", {}, LaunchTarget.New)
```
- View code→Copy codeでボタン定義を取得し、指定式の全文一致を確認。
- 保存を実行し、Studioを再読込。読取専用の編集ロック表示があったが、オーバーライドせず閲覧。再読込後のOnSelectに上記HTTPS式がそのまま保持されていることを確認し、保存の証拠とした。
- 再読込後の限定スモーク：ホーム→職員マスタ検索7件→009900000011検索1件・選択011→条件クリア7件→ホーム。PoCボタンの残存を確認。プレビューを終了。
- Canvasアプリは公開していない。保存済み編集版のStudioプレビューが検証対象。Webリソースは前回公開済みで、削除・権限変更なし。
- クラウドブラウザのURL安全ポリシーによる拒否は、方式変更の許可とは別の制限。禁止されたアクセスをLaunch等の別経路で回避する操作は行わず、当該PoCボタンの押下・印刷は今回実施していない。

| 最新の項目 | 結果 |
|---|---|
| Dataverse固定HTML登録・公開 | 前回成功、保持 |
| HTTPS直接表示 | 前回成功、今回再検証不可 |
| HTTPSボタン実装・式読戻し | PASS |
| 保存・再読込後の式保持 | PASS |
| 既存検索の限定スモーク | PASS |
| ボタンからの帳票別タブ表示 | 未検証 |
| 帳票の目視・印刷プレビュー2ページ | 未検証 |
| 1ファイル2ページPDF保存 | 未検証 |
| Edge | 未検証 |

継続時は保存済み検証アプリのStudioプレビューからHTML帳票PoCを押し、A4縦・倍率100%・ヘッダー/フッターなしで2ページを確認してPDF保存する。独立したユーザー環境での結果は、クラウドブラウザでの実測と分けて記録する。全6成功条件未達のため、現時点は部分成功。削除指示まではボタンとHTMLを保持する。

## ユーザー実機検証と添付PDF検査（2026-09-20）

### 証拠と検証環境
- ユーザー報告：「アカウントの選択が求められましたが、無事別タブでHTML帳票が開き、PDF保存もできました。」直前に案内したPoCボタンの検証に対する報告として記録。クリック操作自体をエージェントが実行・観察したものではない。
- 添付画面：Power Apps StudioとHTML帳票PoCが別タブで存在し、登録済みDataverse WebリソースのHTTPS URL、日本語の1ページ目、表罫線が表示されている。
- 添付PDF：HTML帳票PoC.pdf、60401バイト、PDF 1.4、タイトルHTML帳票PoC。
- SHA-256：85ef71afd37451ad63c8319e5528d19888ca8abbcb068b1f555f8c50844b99c2。
- PDFメタデータ：Windows NT 10.0 / Win64 x64、Microsoft Edge 153.0.0.0、Skia/PDF m153。OSのWindows 10/11の区別はこの情報だけでは確定しない。
- PDF作成日時：2026-09-20 04:14:16 UTC（13:14:16 JST）。帳票ヘッダーも2026/09/20 13:14。
- PyMuPDFでページ数・寸法・文字列を検査し、両ページを画像化して目視確認。ブラウザの印刷プレビュー画面そのものは添付されていない。

### 成功条件の判定
| 条件 | 判定 | 根拠 |
|---|---|---|
| ①Power Appsから別タブを開ける | PASS（ユーザー実機報告） | アカウント選択後に別タブが開いたとの報告、添付画面にStudioと帳票の別タブ |
| ②別タブでHTML帳票表示 | PASS | 報告と添付画面 |
| ③日本語正常 | PASS | 画面・PDF両ページの文字列抽出と目視 |
| ④2ページ分を1HTMLとして扱う | PASS | 単一登録HTMLの構造、両ページのPDF出力 |
| ⑤ブラウザ印刷で2ページ | PASS（出力結果） | Edge生成PDFが2ページ。プレビュー画面の直接確認はなし |
| ⑥1つのPDFに保存 | PASS | 添付1ファイル内に2ページ |

### PDFの詳細確認
- 両ページの寸法594.96×841.92pt（約209.89×297.01mm）。A4縦相当。
- 1ページ目：通勤手当認定簿 PoC／1ページ目／職員番号000123／氏名テスト 太郎。
- 2ページ目：通勤手当認定簿 PoC／2ページ目／通勤方法 電車／備考 Power Apps HTML帳票出力検証。
- 日本語文字化け、欠落、表罫線の欠落、表のページまたぎ、余分な3ページ目は認められない。2ページ目の内容は2ページ目に収まる。
- ブラウザ由来のヘッダー・フッターあり：日時、HTML帳票PoC、URL、1/2・2/2。前回案内した「ヘッダーとフッターなし」とは異なる設定だが、当初の成功条件に違反しないため合格。正式帳票時には不要なら印刷設定でオフにする。
- ブラウザ拡大率100%・印刷倍率100%は添付証拠から確定できない。A4縦の出力結果のみ実証。
- アカウント選択が発生したことを認証時の動作として記録。全利用者で常に選択が出る、または常に省略できるとは断定しない。他の利用者のライセンス・権限・認証動作は未検証。

### 最終結論と次フェーズ
承認済みの変更方式「Power Apps → Launch(HTTPS) → Dataverseの固定HTML → 別タブ → ブラウザ印刷 → 1ファイル2ページPDF」は、今回のユーザー環境で技術成立性を確認し成功と判定する。
元の「Power Fx生成HTMLをdata URLで直接Launch」方式は成功しておらず、今回の成功でその判定を上書きしない。実データ取得・動的埋込の成立も本PoCでは実証していない。

次フェーズ：
通勤手当認定簿の本番2ページレイアウトをHTML/CSSで再現し、
実データを埋め込んだ状態で再検証する。

次フェーズの検討へ進める。ただし実装は別途ユーザー指示後。静的Webリソースに実データをどう埋め込むかは別の設計・検証事項。今回、本番帳票や実データ連携は実装していない。
ユーザーの最新指示に従い、PoCボタンとHTML Webリソースは削除しない。Canvasアプリを新たに公開する操作も今回行っていない。
