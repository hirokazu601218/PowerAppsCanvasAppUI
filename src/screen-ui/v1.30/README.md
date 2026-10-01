# v1.30 SCR001～003 UI変更候補

変更要求 CHANGE-20261001-SCR001-003-UI。実アプリの基準版から必要なコントロールのみ変更。

- ホーム：conscrHomeRootを置換、旧単独Button3を削除して新root内へ配置。旧btnHomePayrollは削除。
- SCR002：conHeader111のみ置換。
- SCR003：conAttendanceFormalRoot置換、旧conAttendanceEditOverlayを削除。OnVisibleを添付式へ変更。Classic/TextInputは既存表のセル内編集・数値右寄せの互換性のため使用。
- 下書きStudioで数式エラー0。架空10件で保存と再表示を検証中。公開版・PAC・選定E2Eは未確認。
