# SCR-002履歴4表のStudio反映候補

- 対象：現行App ID `204a48dc-7f23-43dd-b934-4654a3cfa306` の公開v25（v22を復元したv24から編集・保存）。公開時刻 `2026-09-28T05:00:02.0455229Z`。
- `btnLoadDetails111.OnSelect.fx` は従来の内蔵fixture分岐を維持し、通常表示時には職員基本Lookupと12桁職員番号で隔離4表を取得する。住民税は税固定控除の履歴に `R:` 接頭辞で追加する。
- `galDetailFields111.Items.fx` は通常表示時に選択された履歴の元Dataverse行から定義順に勤務条件15、社会保険26、税固定控除9、住民税6項目を表示する。内蔵fixtureと基本情報・通勤タブは従来式を維持する。空欄と数値0を区別する。
- 2026-09-28、StudioのApp Checkerで数式エラー0件を確認。架空職員011の隔離4表（Action 36376777042）をプレビューで選択し、15・26・9・6列の値、数値0とNULL空欄（Action 36377952175）を観察。職員004への切替で旧履歴が消えることを確認した。専用利用者への隔離4表Readのみ付与（Action 36377417327）。ユーザーのv25置換承認後に公開。公開Playerの専用利用者6ケースは [Action 36380881898](https://github.com/hirokazu601218/PowerAppsCanvasAppUI/actions/runs/36380881898) でPASS。PAC読戻しは [公開後記録](../../../docs/verification/postpublish/change-20260928-scr002-history.json) に記載。
- 元の候補と復旧時の版記録は `records/changes/change-20260928-scr002-history/manual-20260928-studio/`。列契約は `config/dataverse/scr002-history-columns.json`。
