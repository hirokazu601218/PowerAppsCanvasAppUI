# v1.16 内蔵履歴追加・Dataverse併用 回帰結果

日付：2026-09-16。対象：StaffMaster-Automation-Test の自動開発_職員マスタ検索。

## 結果

[run 35098953055](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35098953055) / job 104803216172 は成功。試験対象commitは `cf990af19e9c8403299dce6300373f5f23c22b16`。専用利用者 `powerapps-test@govaca.onmicrosoft.com` で7件、再試行0、1.9分ですべて合格。

|試験|確認した内容|結果|
|---|---|---|
|AUT-META-001|公開Playerのv1.16表示|PASS|
|AUT-SIDEBAR-001|開閉2往復、検索条件・職員・ページ保持|PASS|
|AUT-LAYOUT-001|900/1100/1366/1600/1920px×標準/大文字、9基本項目の値・位置・幅、最大6列、状態バッジ|PASS|
|AUT-LIST-001|同姓同名の番号別キーボード選択、行背景、区切り線|PASS|
|HYBRID-001|勤務3・通勤1・保険1・税1・給与2件、給与詳細2行、011/012認定簿の番号・経路分離、005の0円、001の履歴なし・出力無効|PASS|
|Dataverse access|初期25件、2ページ目025、同姓同名検索、012詳細、再読込、0件、クリア|PASS|
|P0（現行fixture）|検索・選択・右側詳細、900×600の項目非重複・右端到達、クリア|PASS|

旧P0は削除せず、同じ操作・配置・横スクロールの判定を現行12桁fixtureへ移した。旧「山田」/11桁番号を現行の「試験 同姓同名」011/012へ置換。旧版回復用の既存ファイルは保持する。

Studioで数式エラー0・ランタイムエラー0を確認。アクセシビリティ544件・パフォーマンス10件の警告は存在し、今回の7試験の合格と区別する。全アクセシビリティ適合を認定したものではない。

## 読戻しと証跡

- Studioで保存・テスト公開。GitHub Actionsは読み取り試験のみでアプリを配布・復元しない。
- 既存AutomationのOIDC/PACで保存msappを取得。`bridge.verify_download` が全11変更プロパティのYAMLとコンパイル済みInvariantScript、その他の全ソースの意味的同一性を確認：`source_and_rules: exact`。
- 保存msapp SHA-256：`9d1bc8a33e111710736c7ae12e481355a1d6535257e1316c54926b3119c9cf36`。
- スクリーンショットartifact：`dataverse-read-only-35098953055`（ID10447925198）。保存パッケージ・照合結果：`hybrid-readback-35098953055`（ID10447278837）。保存期限2026-09-30。
- 認証状態、Cookie、トークン、資格情報、通信トレースはartifactへ含めない。動画は無効、証明書検証は有効。
- ローカルfixture検査：職員番号12桁・親25件との対応・履歴ID一意・給与収支・通勤12か月列・生成数式一致を確認。
- 権限・共有・ライセンス・従量課金・MFA・Dataverseのレコード/スキーマ変更なし。

## 範囲の境界

現在の残件（共通内蔵データ追加・画面接続・現行fixtureでの回帰）を検証。正式な履歴Dataverseテーブル、給与簿の未確定全列、認定簿の別WorkのレイアウトとPDF保存接続は今回の対象外。給与計算・法定判定・PDF生成保存・本番業務受入の合格とは扱わない。

通常のSolution再配布フローは今回実行していない。旧標準自動受入タグv1.14と、今回のStudio公開＋読み取り受入v1.16を区別する。v1.14を現行Dataverseアプリへそのまま復元しない。

Work開始UTC `2026-09-16T12:36:25.961Z`。Actions開始時に同じ起算時刻から40分未満を検査し、job timeout20分と合わせて60分以内に終了。job終了13:02頃、約26分。

保存パッケージは期限付きartifactに加え、`powerapps/dataverse-v1.16/staff-master.msapp`へ保全。Connections/References/DataSourcesに該当する6ファイルは、v1.15基準とバイト単位で同一。接続維持の判定はファイルが存在したことも含めて確認した。
