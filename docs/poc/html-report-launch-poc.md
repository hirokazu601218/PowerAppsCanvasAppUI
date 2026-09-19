# Power Apps HTML帳票 Launch PoC 検証結果

## 結論
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
