# PAY-IMPLEMENT-001 公開・試験準備

確認時点: 2026-10-10 00:19 UTC。これはローカルの計画・準備結果であり、アプリ更新・公開・実機試験の完了記録ではない。

## 結論

- 同じ試験アプリへのStudio変更・保存・公開と、既存PAC読戻し／公開Player E2Eを組み合わせる経路がある。旧pack/import/publish/restoreは使わない。
- 初版の00:19時点はリリース不可。バックアップ・候補・試験の準備を下記の追記で更新する。実機結果と公開後SHAは未確定。
- 親担当の実行チェック後にだけワークフロー起動へ進む。試験環境・隔離データ・既存資格情報のみ。新しい同意・共有・認証・セキュリティ設定・有料契約・本番・main統合は対象外。

## 固定対象と分離

- 環境: StaffMaster-Automation-Test、68e00049-b7e5-eda6-9888-9a3cc493c5be
- 唯一のApp ID: 204a48dc-7f23-43dd-b934-4654a3cfa306
- 最新GitHub mainは252abe4aa5d3b1d99a584a30c97d9b48153c91f5とGETで再確認。
- PR135はDraft、c1008452348fd27448742796069647584278dca6のまま。今回の実装と混ぜない。
- 親担当からの観測引継ぎ: Maker live v35、これより新しいdraftなし。これは私の実機確認ではない。
- 最新既存公開記録: 2026-10-07T01:17:13.7960236Z、PAC SHA-256 465dcdc2eec6deb181f8df811558bdade4f0b6494675346e1cac700d90f1a740。今回の現在値として流用せず、新しい観測で照合する。
- Wave 1候補: 履歴タブ保持、検索状態を戻り先で保持、SCR005の古い説明選択消去と固定サマリー。src/screen-ui/v1.31を候補領域とする。制度判定・テーブル定義・実データを変えない。

## 利用可能な機能と制約

1. GitHubコネクターはファイル・ブランチ・PR・run・job・ログ・artifactの読取り、既存job再実行が可能。新規workflow_dispatchツールは見当たらない。Actions workflow別run collection URLは未対応だが、repoのactions/runsは取得可能。
2. 第一候補はブラウザー担当がGitHub公式ActionsのRun workflowを使い、候補／文書ブランチ、change_id、readback_onlyを明示する方法。GitHub所有者セッションの存在は今回未確認。
3. 代替案は今回のブランチ＋変更ID＋marker pathを固定した起動条件を既存workflowへ追加する方法。現在のmarkerはSCR003・UI旧変更の特定ブランチだけ。既存ブランチを再利用せず、親レビューなしで追加しない。contents: read、powerapps-test、固定App/環境、全validatorを維持する。
4. 既存共同所有者用secrets参照を継続する。値を取得しない。認証失敗・403・同意表示はBLOCKEDで停止し、権限変更で迂回しない。現在のライセンス／Actions残量による追加費用は未確認。新しい契約や購入はしない。
5. 定期Staff Master E2Eは別環境／別アプリ用。最新成功37999394529を今回の試験合格に転用しない。

## バックアップと復元

- ブラウザー担当が変更前に同AppのDetails/VersionsのLive版、最終保存版、公開日時を記録し、StudioのSaveメニューからDownload a copyで最新msappを取得する。
- バイナリは公開GitHubへ入れない。パッケージSHAと全Source YAMLのパス／SHA、接続メタデータの差分判定だけを記録する。資格情報やデータ内容をログへ出さない。保存先のアクセスと実ファイルを確認する。
- 2026-10-07のLibraryバックアップは履歴。現在のv35バックアップと同一だとは推定しない。
- 失敗時は同Appの公式Versionsから記録済み版をRestoreする。Restoreは新しいdraft版を作るので、Liveの復旧が必要なら確認した復元版を再公開し、PAC読戻しとPlayerを再検査する。旧アプリ／旧Solutionのrestore workflowは使用不可。
- 最新バックアップを取得できない、変更前プロパティが候補のbefore SHAと異なる、接続先が隔離表でない場合は変更前に停止する。

## PAC初回取得と既存v25ガード

current-app-postpublish-docs.ymlのreadback_only=trueはアプリを更新しない。PAC download前後にメタデータを取得し、Ready、固定App URI、before==afterを検査する。その後、SCR002画面SHAを古いv25値498029d25c9191a3cf3157f8a294690afd90b4cbb4a4d3c0845cc27b2ea08e6dと比べる。

- PAC候補SHAはダウンロード直後にstep summaryへ書く。
- メタデータ検査成功後は公開日時・最終draft・msapp SHA・SCR002 SHA・v25一致結果をsummaryへ書いてから、不一致ならFAILにする。
- capture jobにはartifact uploadがない。パッケージ本体・before/after JSON・source YAMLは回収できない。
- capture段階にdraft<=publish検査はない。summaryの両時刻を別途比較し、draftが新しい場合は公開版の証明に使わない。
- よって親承認後、初回は「PAC取得と限定観測、v25ガード不一致FAIL」の証跡取得に使える。FAILをPASSには変えず、パッケージバックアップ取得済みとも扱わない。
- current-ui-capture.ymlおよびcommute-capture.ymlは成功時だけcapture.jsonをuploadする。if未指定はsuccess条件なので、ガード失敗後にartifactは出ない。msappはどちらもuploadしない。
- v25ガードの調整が必要なら、独立に取得・照合した現行snapshot／候補sourceの正確な期待SHAへ変更要求単位で固定する。期待値を実行時ダウンロードから自己採用しない。

## 候補に追加したローカルガード

- current-app-test-gate.ymlのPR/push対象にsrc/screen-ui/v1.31/**を追加。
- validate_selection.pyのSOURCE_PREFIXESにv1.31を追加。公開後validatorも同関数を使うので、公開後のv1.31変更を拒否する。
- v1.31の選定漏れ拒否、postpublish選定、公開後変更拒否の3回帰を追加。
- attendance-ui.test.tsの自動Allow/許可clickを除去し、必要同意が見えたらBLOCKEDエラーとする。
- ローカル検査: automation 35件PASS、governance 3件PASS、git diff --check PASS。Power Fxコンパイル、Studio、実機E2Eではない。
- CIは変更されたtest fileの全ケースも実行するため、attendance-ui修正で既存SCR003/SCR006の4ケースがPR回帰へ追加される。postpublishは選定JSON内のケースだけなので、この差を記録する。

## 実行チェックリスト（親レビュー後）

1. 変更要求と同IDの選定JSONを完成。各v1.31ファイルと変更部品を全件登録し、各部品の実画面単体、状態受渡しの結合、既定ホーム／詳細スモークを含める。未決制度項目は除外し理由を残す。
2. ソース・テスト・request/selection・gate修正を同じ候補コミットSとして固定。リモートSHAを再読し、PRはDraftで維持する。
3. 最新Studioバックアップ、全Source差分、接続先、before SHAを照合する。ブラウザー担当へ変更するプロパティだけ渡す。
4. Studioで変更・式検査・プレビュー試験。成功／失敗／未実施を分け、検証データ以外への書込みがないことを確認。保存版Dと候補Sの対応を記録する。
5. 同Appへ試験公開。Live版／公開時刻Pを記録。新規起動／更新したPlayerで候補ケースを操作し、初期値・切替・戻る・繰返し・0件・取消など対象状態を検証する。
6. PAC方式の公開後SHA Hを取得し、before/afterメタデータ同一・Ready・App/環境一致・draft<=Pを確認。Studio保存sourceと候補Sの全変更プロパティ、非対象sourceと接続が不変であることを照合。Maker msappのbyte SHAだけでPAC Hを代用しない。
7. S以降はsource/request/selection/testを変更しない。文書編集前コミットBを固定。docs/verification/postpublish/pay-implement-001.jsonへS、B、P、H、観察時刻、checked_paths、結果・残件を書く。未実機をPASSにしない。
8. 公開後にrequirements.md、basic-design.md、detailed-design.mdを内容まで更新し、PAY-IMPLEMENT-001とPを明記。結合対象なのでtest-specification.mdへ選定結合ID・独立期待値・変更ID・Pを反映。STATUSへ今回の対象／残件を追記。文書のみのコミットCを作る。
9. 文書ブランチCでcurrent-app-postpublish-docs.ymlをchange_id=PAY-IMPLEMENT-001、readback_only=falseとして起動。既存validatorはS→Cのsource不変、B→Cの3文書更新、時刻・H・固定App・no newer draft、選定E2Eを検査する。全jobのrun/head SHAと結果を確認する。
10. 要求→候補→保存／公開→読戻し→実画面→3文書→最終再照合を一覧化。FAIL/BLOCKED/NOT_RUNを残す。総合D-07・業務受入は別判定。main統合は行わない。

## 必要な新規ケースの最低観点

- 履歴表示／非表示を切り替えた後のカテゴリ変更で選択が保持される。別職員・0件で旧職員の履歴は残らない。
- 検索語／所属／ページ／選択職員／タブなど確定された状態だけがSCR005から戻ったとき復元される。再度往復と直接入口も確認する。
- SCR005の職員・支給月・明細切替時に前の説明を消去し、現在行の説明と固定サマリーだけを表示する。0件／未選択で前の情報を残さない。
- 既存履歴列表示、ホーム→一覧→詳細、給与簿→SCR005→戻る、通勤帳票の隔離接続・既存入口が壊れていない。正確なケースID／操作は実装担当の選定と確定設計へ対応付ける。

## 根拠

- リポジトリ: docs/operations/current-app-request-to-release.md、single-app-workflow.md、docs/testing/current-app-e2e.md、test-policy.md、change-records/README.md
- [直近の実読戻し・選定E2E成功（履歴）](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/37567285581)。job112617961968でPAC読戻し検査成功、job112618565145で選定E2E成功をGET確認。
- [Microsoft: Download a copy](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/export-import-single-app)、[保存と公開](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/save-publish-app)、[同Appの版復元](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/restore-an-app)、[PAC canvas download](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/canvas)。公式資料を2026-10-10に確認。

このルート直下のrelease-readiness.mdは親担当指定のローカル受渡し用。GitHubへ記録するときはrecords/changes/pay-implement-001/manual-20261010-release-preflight/内のコピーを使い、ルート直下版をコミットしない。

## 00:29 UTC 更新

- 公式Exportによる現在live v35のmsappを取得し、SHA-256が465dcdc2eec6deb181f8df811558bdade4f0b6494675346e1cac700d90f1a740であること、全10 Src YAMLが審査済みsnapshotと同一であることを実行担当が確認した。Export前後のlive v35も不変。バイナリと生の接続メタデータは公開コミットから除外する。
- Wave 1 r4のsource/request/selection/E2Eは固定準備済み。対象source16件、状態保持9ケース。独立レビューが351コントロール集合不変・14プロパティと親移動1件だけの差分を確認。最終公開ソースSHAは送信後に別途記録する。
- 全体のローカル候補検査はautomation49件とgovernance3件がPASS。これは実装担当と独立レビューの新しい結果であり、このフォルダの00:19時点の35件ログを上書きしない。
- この時点でもStudio適用・保存・公開・変更後PAC読戻し・変更後Player試験は未実施。
