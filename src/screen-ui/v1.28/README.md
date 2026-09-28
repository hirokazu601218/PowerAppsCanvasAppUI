# SCR-002履歴4表のStudio反映候補

- 対象：現行App ID `204a48dc-7f23-43dd-b934-4654a3cfa306` の未公開v24。公開v22は変更しない。
- `btnLoadDetails111.OnSelect.fx` は従来の内蔵fixture分岐を維持し、通常表示時には職員基本Lookupと12桁職員番号で隔離4表を取得する。住民税は税固定控除の履歴に `R:` 接頭辞で追加する。
- `galDetailFields111.Items.fx` は通常表示時に選択された履歴の元Dataverse行から定義順に勤務条件15、社会保険26、税固定控除9、住民税6項目を表示する。内蔵fixtureと基本情報・通勤タブは従来式を維持する。空欄と数値0を区別する。
- 2026-09-28、StudioのApp Checkerで数式エラー0件を確認。テーブル内の隔離試験行が未作成のため、実データの値・履歴切替・専用利用者の確認と公開は未了。公開後の読戻しが終わるまで完成版とは扱わない。
- 元の候補と復旧時の版記録は `records/changes/change-20260928-scr002-history/manual-20260928-studio/`。列契約は `config/dataverse/scr002-history-columns.json`。
