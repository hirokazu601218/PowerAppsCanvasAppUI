// DADSベース Power Apps デザイントークン v1.0
// 対応基準: DADS_PowerApps_デザイン基準_v1.01
// 貼り付け先: App.Formulas
//
// 注意:
// - Power Appsのモダンテーマは App.Theme を使用するため、
//   独自トークンのルート名は衝突を避けて DadsTokens とする。
// - モダンコントロールでは組み込みテーマを優先し、設定可能な
//   BasePaletteColor等へ DadsTokens.Color.Primary を指定する。
// - 本トークンは、画面、コンテナ、クラシックコントロール、
//   複合部品およびモダンコントロールの追加設定から参照する。

DadsTokens =
{
    Meta: {
        TokenVersion: "1.0",
        DesignStandardVersion: "1.01",
        DadsReferenceVersion: "2.18.0",
        DesignSystemName: "DADSベース Power Apps"
    },

    Color: {
        // 基本色
        White: ColorValue("#FFFFFF"),
        Black: ColorValue("#000000"),
        Transparent: RGBA(0, 0, 0, 0),

        // 背景・面
        Background: ColorValue("#FFFFFF"),
        BackgroundSubtle: ColorValue("#F2F2F2"),
        Surface: ColorValue("#FFFFFF"),

        // テキスト
        TextPrimary: ColorValue("#1A1A1A"),
        TextSecondary: ColorValue("#4D4D4D"),
        TextDisabled: ColorValue("#4D4D4D"),
        TextOnPrimary: ColorValue("#FFFFFF"),

        // 境界線・区切り線
        Border: ColorValue("#949494"),
        BorderStrong: ColorValue("#666666"),
        Divider: ColorValue("#CCCCCC"),
        DisabledBackground: ColorValue("#E6E6E6"),

        // 主色
        Primary: ColorValue("#0017C1"),
        PrimaryHover: ColorValue("#00118F"),
        PrimaryPressed: ColorValue("#000071"),
        PrimarySubtle: ColorValue("#E8F1FE"),

        // リンク
        Link: ColorValue("#0017C1"),
        LinkVisited: ColorValue("#6C006C"),

        // 成功
        SuccessText: ColorValue("#197A4B"),
        SuccessBackground: ColorValue("#E6F5EC"),

        // エラー
        ErrorText: ColorValue("#CE0000"),
        ErrorBackground: ColorValue("#FDEEEE"),

        // 警告
        WarningText: ColorValue("#C74700"),
        WarningBackground: ColorValue("#FFEEE2"),

        // 情報
        InfoText: ColorValue("#0017C1"),
        InfoBackground: ColorValue("#E8F1FE"),

        // フォーカス
        FocusOuter: ColorValue("#FFD43D"),
        FocusInner: ColorValue("#000000")
    },

    Font: {
        // クラシックコントロール等のFontプロパティ用
        Family: Font.'Segoe UI',

        // モダンテーマのフォント名指定用
        FamilyName: "Segoe UI",

        WeightRegular: FontWeight.Normal,
        WeightBold: FontWeight.Bold,

        Size: {
            PageTitle: 32,
            SectionTitle: 24,
            SubsectionTitle: 20,
            Body: 16,
            InputLabel: 16,
            Button: 16,
            Caption: 14
        },

        // LineHeightプロパティで使用する倍率
        LineHeight: {
            PageTitle: 1.3,
            SectionTitle: 1.4,
            SubsectionTitle: 1.4,
            Body: 1.5,
            InputLabel: 1.4,
            Button: 1.3,
            Caption: 1.5
        }
    },

    Space: {
        XS: 4,
        S: 8,
        M: 16,
        L: 24,
        XL: 32,
        '2XL': 48,
        '3XL': 64
    },

    Radius: {
        None: 0,
        Control: 8,
        Card: 12,
        Dialog: 16,
        Full: 9999
    },

    Border: {
        WidthDefault: 1,
        WidthStrong: 2,
        WidthFocus: 2
    },

    Size: {
        // 操作領域
        TargetMinimum: 44,

        // コントロール高
        ControlSmall: 36,
        ControlMedium: 48,
        ControlLarge: 56,

        // ボタン
        ButtonMediumMinWidth: 96,
        ButtonLargeMinWidth: 136,

        // アイコン
        IconCompact: 20,
        IconDefault: 24,

        // 画面・一覧
        HeaderHeight: 64,
        RowMinimumHeight: 48,
        ContentMaximumWidth: 1200
    },

    Breakpoint: {
        MobileMaximum: 767,
        DesktopMinimum: 768
    }
};

// レスポンシブ判定
IsMobileLayout = App.Width < DadsTokens.Breakpoint.DesktopMinimum;
IsDesktopLayout = Not(IsMobileLayout);

// レスポンシブ共通値
PagePadding =
    If(
        IsMobileLayout,
        DadsTokens.Space.M,
        DadsTokens.Space.XL
    );

LayoutGap =
    If(
        IsMobileLayout,
        DadsTokens.Space.M,
        DadsTokens.Space.XL
    );

CardPadding =
    If(
        IsMobileLayout,
        DadsTokens.Space.M,
        DadsTokens.Space.L
    );

ContentWidth =
    Min(
        App.Width - (PagePadding * 2),
        DadsTokens.Size.ContentMaximumWidth
    );
