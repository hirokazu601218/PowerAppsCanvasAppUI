# UI試作 v1.24 — PDF以外の残件対応

基準: main 001f1539、公開環境 StaffMaster-Automation-Test。既存6画面を継続。

- 認定簿・基準給与簿・TSVの起動ボタンをScreen1直下のClassic Buttonへ移動。閉じる時のSetFocusを有効化。Modern Buttonを例外的に置換した理由は実環境でのSetFocus非対応。ClassicにはAccessibleLabelを設定せずTextを操作名とする。
- 40件時の2ページ目が5行分の高さになる固定25件計算を実件数へ変更。
- ホームの職員検索は通常データが読めるまで無効にし、早すぎる画面遷移を防止。
- メンテナンスに通常/0/1/20/21/40/長文・負数の切替を追加。008800000001〜040は内蔵表示試験専用。アプリ終了で通常へ戻る。Dataverseへの書込みなし。

## 導入と復元

正本はStudio読戻し4ファイルとmanifest。未変更3画面はv1.22の読戻しを使用。

1. 適用前にv1.23の読戻しとバックアップを確認。
2. 同名3起動ボタンを元のコンテナから削除し、Screen1直下へmodal-actions.paste.yamlを1回だけ貼付する。既存名が残っている場合は中止。
3. patches.jsonの対象プロパティを適用。App.Formulasは全文置換し二重追加しない。
4. conMaintenanceBodyへfixture-selector.paste.yamlを1回だけ貼付。ddUiFixture124/lblUiFixture124が既存なら中止。
5. App checker、読戻し一致、公開版スモークを確認。

復元はv1.23のApp.Formulas・Screen1・scrHome・scrMaintenanceの読戻しから行う。公開版への復元演習は未実施。PDF生成・保存・印刷を今回の合格対象に含めない。

## 実行結果

[回帰結果](../../../records/docs/testing/regression-v124/results.md)と95項目監査を参照。39ケース予定の一括回帰runは35318861503。結果確定までは全面合格を宣言しない。
