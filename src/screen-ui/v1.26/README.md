# UI試作 v1.26

v1.25で検出したモーダル中の背面Tab到達を修正。conMain111とconStaffNavigation122のVisibleを、認定簿・給与詳細・TSVのいずれも閉じている時だけtrueにする。閉じる操作のSetFocusは維持する。

基準v1.25の5プロパティだけを変更。既存ID・階層は維持。App.Formulasはv1.24、追加3画面はv1.22読戻しを継承。

適用前にpatches.jsonのbeforeを照合。afterなら適用済みとして停止。既存コントロールの同名プロパティにafterを設定する。復元は同じ5プロパティをbeforeへ戻す。公式数式チェック・読戻し・回帰を実施する。別複製による適用/復元演習は未実施。

背面操作防止とブラウザー外枠を含む完全なフォーカストラップは別判定。[検証結果](../../../docs/testing/regression-v125/results.md)を参照。
