# Dataverse接続前レビュー（工程6）

2026-09-16。基準: main 298678953fb2a9115232e9f47ed6c3fa4559a04a、公開v1.14。

## 実行IDと接続方式

Dataverse構築・投入・自動配布は既存のPowerAppsCanvasAppUI-Automationを優先する。
これはGitHub ActionsがOIDCで使用するサービスプリンシパルであり、通常の対話サインイン用ユーザーとは区別する。
本人アカウントへの編集権限追加を再開条件にした前記録は撤回する。
権限拡張、MFA変更、有料設定は自動実施しない。

工程4のテーブル作成と工程5の5件読戻しは成功済み。
現在のbridge.pyは既存プロパティ更新用で、新規接続に必要な構造変更・一般コンパイルを実装していない。
自動化用IDが所有者であることだけではこの制限を解消しない。

Microsoftの外部コード編集経路も、開いたPower Apps Studio共同編集セッションを必要とし、
接続追加はStudioのDataパネルで行う。現状の自動配布経路単独での接続追加は未実証。
既存ゲートを解除して未検証のmsappを公開しない。

参照:
- [公式の外部コード編集](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/create-canvas-external-tools)
- [公式CLI canvas（pack/unpackは非推奨）](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/canvas)

## ソースレビュー結果

Screen1.pa.yamlをYAMLとして解析し、各プロパティのTable定義を集計した。
全プロパティの一覧は[fixture-inventory.json](fixture-inventory.json)を参照。

|データ定義|重複箇所|
|---|---:|
|demoStaff|57|
|demoWork|3|
|demoCommute|4|
|demoSocial|3|
|demoResident|3|
|demoTax|3|
|demoPayroll|7|
|合計|80|

demoStaffは初期読込・検索・一覧・詳細・出力・帳票にも埋め込まれている。
ボタン1個の置換では外部化は完了しない。初期表示でFirst(demoStaff)に戻る経路も置換対象。

|旧表現|確定仕様への変更|
|---|---|
|11桁のStaffId|12桁数字文字列。旧履歴の関連キーも影響するため単純な番号差替えは不可|
|保存済みStatus文字列|採用日・退職日から日本時間で導出。採用日空欄は最優先で採用前|
|Hire/Leave/Birth文字列|Dataverse DateOnly。表示時だけ整形|
|Hours文字列|保存値は分の整数、画面はH:mm|
|TaxClassの甲欄/乙欄|Choiceの甲/乙。必須|
|Pension等の制度名・登録状態|今回の4列は加入有無。制度名を加入と機械変換しない|
|ResidentReg/TaxMay/TaxJune/TaxJuly|M_職員基本から除外済み。出力・画面の参照もレビュー対象|

## 段階的な接続作業

1. StudioでM_職員基本を接続し、型とChoiceを確認した基準パッケージを保存する。
2. 接続追加済みパッケージをGitHubで管理し、自動配布で接続を保全できることを検証する。
3. 検索は日付・職員番号・氏名等のDataverse条件へ移す。全件をコレクション化する方式を前提にしない。
4. 一覧、選択、基本情報、出力の57か所の職員データ参照を統一する。0件時・通信失敗時に旧サンプルへ戻さない。
5. 5件で空欄・未来採用・在籍・退職・0円を実機確認し、その後25件へ進む。

M_職員基本は最新情報1人1行であり、勤務・通勤・保険・税・給与の複数履歴を表すテーブルではない。
これらの履歴定義は今回の24列へ押し込めない。職員基本の外部化後も履歴用サンプルが残る場合は残件と明示する。
住民税4列の削除を、履歴機能全体の廃止や既存履歴削除の承認とみなさない。

## 読取診断結果

[run 35073900437](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/35073900437)で自動化用IDの一致・Owner・fixture5件読取を確認。
アプリの人の共有対象はCanViewのみ。テスト用メールの一意照合は未完了（systemusers一致0、aadusersフィルターHTTP400）。表示名だけで権限変更しない。
初回run 35073770871はsystemusers一致がないため停止。両runとも書込処理なし。
