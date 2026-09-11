# PowerAppsCanvasAppUI

デジタル庁デザインシステム（DADS）をPower Appsキャンバスアプリ向けに適用するための、設計資料・Power Fxデザイントークン・共通UI YAMLです。

## 基本方針

- Power Appsへ実装する成果物は、Power AppsのYAMLおよびPower Fxを使用します。
- 利用可能な部品は、モダンコントロールを優先します。
- DADSをそのまま再現するのではなく、Power Appsの仕様に合わせて変換したデザイン基準を使用します。
- HTMLまたは画像は、UIイメージの作成を明示的に依頼された場合だけ使用します。

## ディレクトリ構成

```text
PowerAppsCanvasAppUI/
├─ README.md
├─ docs/
│  ├─ PowerApps_UI試作ルール.md
│  ├─ DADS_PowerApps_デザイン基準_v1.01.md
│  └─ 非常勤給与_PowerApps給与計算UI_要件定義概要_v0.1.md
└─ src/
   ├─ DADS_PowerApps_AppFormulas_デザイントークン_v1.0.fx
   ├─ DADS_PowerApps_共通UIパーツ_v1.0.yaml
   └─ scrDadsStyleGallery_v1.2.pa.yaml
```

## Power Appsへの適用順

1. `docs/PowerApps_UI試作ルール.md` と `docs/DADS_PowerApps_デザイン基準_v1.01.md` を確認します。
2. `src/DADS_PowerApps_AppFormulas_デザイントークン_v1.0.fx` の内容を `App.Formulas` に貼り付けます。
3. `src/scrDadsStyleGallery_v1.2.pa.yaml` の内容をコピーし、Power Apps Studioのツリービューへ貼り付けます。
4. スタイル確認画面で、色、文字、ボタン、入力欄、カード、通知、レスポンシブ表示を確認します。
5. `src/DADS_PowerApps_共通UIパーツ_v1.0.yaml` を参考に、実際の業務画面を作成します。

## 現在の採用バージョン

| 成果物 | バージョン |
|---|---:|
| Power Apps UI試作ルール | 現行版 |
| DADSベース デザイン基準 | 1.01 |
| App.Formulas デザイントークン | 1.0 |
| 共通UIパーツ | 1.0 |
| スタイル確認用スクリーン | 1.2 |
| 給与計算UI 要件定義概要 | 0.1 |

## スタイル確認用スクリーン v1.2

- 16:9の画面幅を最大限利用します。
- デスクトップ時の外側余白は左24px、右32pxです。
- 右余白には縦スクロールバー用の安全域を含みます。
- 通知コンテナには右枠欠け防止用の4pxの安全余白を設けています。
- モバイル時の外側余白は左16px、右24pxです。

