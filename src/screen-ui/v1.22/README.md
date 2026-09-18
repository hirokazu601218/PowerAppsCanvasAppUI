# v1.22 UI試作のソース

画面要件v0.6／Issue #52。最新の実機検証範囲は [公開記録](../../../docs/releases/2026-09-18-screens-v1.22.md) を参照。

- `scr*.paste.yaml`：新規各画面のルートコンテナ貼付用。
- `scr*.pa.yaml`、`Screens.pa.yaml`：管理用定義。
- `App.Formulas.fx`：基準版の既存式＋所属フィルター＋新画面の名前付き数式。`App.Formulas.add.fx` は追加部分だけ。
- `App.StartScreen.fx`：scrHome。
- `Screen1.navigation.paste.yaml`：既存Screen1直下へ1回だけ追加するナビゲーション。
- `manifest.json`：既存画面の変更3式。
- `studio-readback/`：保存・公開後にStudioのコード表示から取得した新規画面。既定値の省略等があるため再編集時はこちらも参照。
- `Screen1.readback-diff.json`：v1.21の既存画面との読戻し差分。元の全画面は `src/staff-master/patches/v1.21/studio-readback/Screen1.pa.yaml` を基準にする。

## 再生成・適用

`python scripts/ui/build_v122.py`（PyYAMLが必要）。生成したYAMLはStudioで公式コンパイルすること。

1. 現行v1.21のアプリ複製で、manifestの5画面を空画面として追加する。
2. App.Formulasを完全版に、StartScreenをscrHomeにする。
3. 各画面に対応paste版を1回貼付。scrPayrollとscrMaintenanceのOnVisibleは管理用pa.yamlから設定する。画面FillのStudio既定値は白だが、全面ルートがUiTheme.Backgroundで覆う。
4. Screen1の直下へナビゲーションを追加し、manifestに記載した既存3プロパティのみ変更する。既存コントロールIDは維持する。
5. 公式チェック・対象ケースを実施してから保存・公開。旧bridgeは画面追加非対応のため使用しない。

仮入力と権限確認スイッチはUI検討用。実データ永続化・本番認可・正式計算ではない。復元時はv1.21のApp/Screen1を使い、新規5画面とナビゲーションを削除して公式確認を行う。
