# 軽量版の構造移行と自動配布

対象は既存の自動テスト専用アプリ。旧版のテスト・成功タグを削除または緩和しない。

## 2026-09-24 隔離した改訂配布の実証

従来の安定版SolutionテンプレートはCanvasの`DatabaseReferences`が空であり、実際のimportで元の3テーブル参照が消えた。Studioの版履歴から安定版を復旧済み。現行の`lightweight-transaction.py`は現行Solutionのexportを元にpackし、3参照を照合するが、`automation/lightweight-expected.json`に`deployment_enabled: true`を設定していないため、安定版へのimportは実行できない。このガードを単に有効化しない。

隔離した検証用アプリ`bd256de5-c7a5-4487-9aef-91ee26d4c946`と、Canvas 1件だけを含む`LightweightDeploymentProbe`で以下を確認した。

|試験|run|結果|
|---|---|---|
|現行Solutionのexport、3参照、pack/unpack|[35985782401](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35985782401)|合格|
|同一版importとソース・実行定義の読戻し|[35986462161](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35986462161)|合格。管理メタデータのハッシュは変更|
|ラベルTextの実改訂、import、サーバー読戻し、元版復旧|[35992512542](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35992512542)|合格。3参照と全ソース・実行定義を復旧|
|元の安定版公開物と3参照の読取り専用再確認|[35992833627](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35992833627)|合格。公開msapp SHA256は`4078adc1c7e3c4a7122b2fe8731bb4a3904061f33272ebbb99259bd46e995518`|

PACのサービスプリンシパルでは新規コピーの`canvas download`列挙が`No canvas apps in the selected environment`となり、[公開状態の読取りAPIも403](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35993159879)となるため、検証用SolutionのexportからCanvas文書を読んだ。サービスプリンシパルにこのコピーの公開権限があるとは扱わない。取込み後の照合は参照・ソース・実行定義で行い、変動する管理メタデータのハッシュは別記する。元の安定版では`canvas download`に成功している。

所有者のStudioプレビューと公開Playerではコピーの職員7件・給与163項目/1レコードを確認した。実改訂がPlayerへ公開された結果、専用ユーザーの実画面確認、広い安定版Solutionへの配布・復旧は未実証。コピーの共有画面は所有者1名のみで最大共有数到達と表示し、サービスプリンシパルへの追加共有は不可。Power Appsの画面は別環境への配布を案内する。この制限を越えるための環境設定変更や権限拡張を実施していない。自動最終化が要求する全ゲートを隔離試験で代替しない。次に必要なのは、自動化アカウントが対象コピーを編集・公開できる別の検証環境または管理可能な配布先の決定、実改訂の公開Player試験、安定版への配布経路を同じ構成範囲で検証する安全な方法の確立である。

## 構造移行
新規コントロールや画面構造はPower Apps Studioで作成・コンパイルする。保存コピーの全6画面とAppのソース、実行ルール、数式エラー、編集版Playerを確認する。任意YAMLを一般コンパイルする方式ではない。

今回の保存コピーは検索画面69部品、全画面228部品。接続情報を含むmsappを公開GitHubへ追加せず、承認済みの全ソース/実行ルールのハッシュをautomation/lightweight-expected.jsonへ固定する。未公開下書きをPACが返すとは仮定しない。

## 自動処理
- lightweight-studio.yml: 隔離HTML配置・読戻し、境界値fixtureの準備/削除。元テーブルの前後ハッシュを照合。
- lightweight-ui.yml: 公開編集版の現行P0と指示別試験。公式認証フローと既存専用ユーザーを使用。機能試験のretryは0。
- lightweight-readback.yml: 公開安定版を取得し、全7ソースの事前固定ハッシュを照合。Ready/取得成功だけを合格にしない。
- lightweight-transaction.yml: Studioで公開・読戻し済みの軽量版を基準に、既存bridgeでbuild、Solution pack/import、publish、ソースと全実行ルールreadback、change_test、独立起動P0を実行する。7ゲートが揃わなければ成功版へ昇格しない。

## 回帰試験の構成
旧Screen1・旧Canvas帳票を前提とする既存の全ユニット試験は、構造移行直前コミット408a5f11e6bcc02ce88cc690afb4200030b128f7を固定チェックアウトして、変更せず全件実行する。現行の軽量版では独立したハッシュ・対象・構造ガード試験を実行し、既存bridgeの実build/import/readbackと独立P0で新構成を検証する。旧試験を軽量版の合格件数に合算せず、各プロファイルの結果を分ける。

## 要求と停止条件
automation/lightweight-transaction.jsonのmode=qualifyは変更0件の実配布受入。mode=releaseは承認済みissueと既存プロパティのsource/control/property/before/afterを明示する。100件を超える変更、ファイル追加、部品追加、未対応の省略プロパティ、before不一致、対象ID不一致、公開基準のソース/実行ルール不一致、未公開下書きがある場合は配布前に停止する。

将来の機能変更では今回の固定試験だけで代用せず、その変更に対する独立した試験を同じ候補コミットへ追加する。給与レコード登録可否など未確定業務仕様を自動的に変更しない。

配布直前のパッケージを復旧用にpackする。配布開始後に失敗した場合はその内容へ復元・公開し、固定ハッシュとP0で復元を検証する。復元成功は元の要求の成功ではない。ジョブ強制終了時は復旧保証がないため、最後のresultと公開内容を確認してから復旧する。

## 証跡
Actionsのresult.jsonに対象、候補commit、公開時刻、各ゲート、パッケージSHA、復元結果を記録する。パッケージ・画面・ログは14日保持。認証失敗画面のみ1日保持し、認証状態や資格情報はartifactへ追加しない。

資格認定の実行前はこの文書の処理を実証済みとは扱わない。今回はStudioによる構造移行と、自動配布経路の実証を別々に記録する。200%表示、実端末、業務受入や旧版の未解決事項を、自動P0合格へ読み替えない。

## 軽量版基準の最終化

旧フローのv1.14成功タグと復元方式を上書きしない。構造移行後は別名前空間lightweight-v1.27を使用する。lightweight-finalizeはmainへのPR mergeの第2親とtree一致を検査し、その候補の最新qualification run・固定対象・全7ゲート・実パッケージSHA・全ソース/実行式・現在の公開時刻を照合する。変更のないqualificationだけを対象にする。

READMEだけを更新した専用コミットを作り、差分がREADMEのみであることを再検査する。注釈タグに候補/main/READMEコミット、run、公開時刻、全ゲート、パッケージSHA、全固定ハッシュを永続記録する。Workが生成済みREADMEブランチを文書PRでmainへ統合して完了する。旧schema 2やv1.14の成功に読み替えない。最終化はアプリを再配布しない。

Solutionテンプレートはmainと同一のtree a81f1a891b8668112e76a9f38d6e69a60c8e088aへ固定。未公開下書き判定はUTCの保存時刻が公開時刻より新しいかで検査し、時刻欠落・不正値・Ready以外は拒否する。
