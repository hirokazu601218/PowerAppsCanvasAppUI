# r6a: 子コンテナの配置を明示する読戻し整合

## 結論

S″ `0c0c9f8c4141a898d0ea64cccbe0aefe3a9258fe` の9入力プロパティに加え、Studioが直下4子の AlignInContainer を SetByContainer へ連動変更した。r6aはこれをソースへ明記する4項目だけの追加差分。A案のレイアウト式、業務式、部品86件、親子構造は変更しない。13項目はr5からの合計であり、今回さらに13項目を編集する意味ではない。

親からA案の承認と公開ソースS″固定を受領した。r6aの公開ソース固定・実機ゲートは未完了。本追補は技術的なソース整合で、公開の許可や全表示試験の合格を意味しない。アプリ側は既に4つの実値が一致するため追加手動修正不要。

## 何を正規化と認めるか

- root LayoutAlignItems.Start の省略だけ。公式公開v36パッケージ内25件で、Controls JSONのStart明示に対応するSrc YAMLが省略されることを確認した。現在Studio公式数式バーもStart。比較器はこの1つの場所・値以外を補完しない。
- 直下4子は同値正規化とは認めない。v36 Controls.DynamicPropertiesではStretchだがSrcでは省略されていた。GroupContainerでは省略が型依存であり、一般的な既定値説明だけではSetByContainerを導けない。今回の実値はSetByContainerへ変更されている。
- したがって候補にも4子SetByContainerを明記し、読戻し側の4子の省略・Stretch・Startはすべて拒否する。親Start＋明示継承により、承認Aの幅750保持という意図を曖昧な型既定値に依存させない。

Microsoftの[縦コンテナの説明](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/control-vertical-container)はSetByContainerが親LayoutAlignItemsを継承すると説明する。ただし、それをすべての型のYAML省略規則と読み替えない。実パッケージから得た型別証拠を優先する。

## ガードと結果

- v36の10原本SHA・全rootガードはそのまま。4新項目のbefore_absentはYAML上の不存在であり、raw側のStretchを別記している。意味上の不存在ではない。
- r5→r6aの全13項目を逆変換するとr5 root SHAへ一致。4項目だけ逆変換すればS″のr6 root SHAへ一致する。
- 実際の全給与画面読戻しに対し、生成したr6a画面とroot Start省略1件のみで一致。画面OnVisibleを含め他差分0。Checker0・公式数式バー5実値・職員検索raw一致はブラウザ担当の読取り報告。表示品質の合格とは別。
- 自動94件・配置ルール単体3件PASS。最初の自動試験は作業コピーに未コピーだったflow fixture1件でエラー。その不変ファイルを補った後に94件すべて再実行した。Power Fx runtimeの代替ではない。
- 通常900/1366/1920、450/683/960、短高、実Chrome200%、24控除欄×2状態、全操作、Tab/Shift+Tab、100→200→100、公開後Playerのゲートは従来どおり必要。r5のPASSやローカルPASSを転記しない。

## 次と復旧

親が本最小差分を確認しS‴を固定するまで公開しない。現物は既に明示4実値と一致するため追加貼付は不要。再読戻しはcheck_payroll_readback.pyで完全画面比較し、root Start省略1件だけを記録する。expectedにはv36全10Srcを検証してapply_pay_implement_001.pyが新規private出力へ生成したscrPayroll.pa.yamlを渡す。配布用src/screen-ui/v1.31/payroll-root.pa.yamlはrootだけで画面Propertiesを含まないため、完全画面比較のexpectedに使わない。raw出力は公開リポジトリへ入れない。

復旧では当初9項目だけでなく、4子の実効配置Stretchも戻す必要がある。省略YAMLを貼るだけでStretchへ戻ったと仮定しない。公式数式バーまたはControls JSONで確認する。旧r5の200%・450幅の既知不具合が戻ることも明記する。
