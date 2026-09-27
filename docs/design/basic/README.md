# 基本設計書：文書の関係

[要件定義](../../requirements/README.md)の子、[詳細設計](../detailed/README.md)の親に当たる。現行版について次の順に読む。

| 文書 | 関係 | 内容・重複させない事項 |
|---|---|---|
| [基本設計書](basic-design.md) | 親・正本 | SCR-001～006の機能・画面間状態、責務分担、構成・配置。個々の列定義やPower Fxの式は子を参照 |
| [Dataverseデータ設計](data-model.md) | 子 | 職員基本・通勤・給与簿の親子関係とデータ契約。全84/163列の定義は機械可読な設定ファイルに集約 |
| [B案デザイン基準](design-system.md) | 子 | 文字、色、余白、操作性の共通基準。画面固有の要件は画面要件を参照 |

子同士は兄弟であり、データ項目と見た目を互いの正本として引用しない。保存先・権限・公開版との一致を判断するときは[未決一覧](../../requirements/open-decisions.md)を参照する。旧版の構成・配置は[記録](../../../records/docs/design/basic-design-before-consolidation.md)に保存した。
