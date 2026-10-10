# Independent r6 layout proposal review

Result: PASS for source integrity and the independently checked geometry model. The candidate is an unapproved UI proposal. Power Apps compilation, application/save, readback, actual browser zoom, keyboard/focus and runtime rendering have not been performed by this reviewer. This result is not a release gate or an assertion that the 200% defect is resolved in the app.

Only local review artifacts were written. Candidate source, external services, application state, data, and business rules were not changed by the review.

## Scope and independently verified evidence

- Base source commit recorded by the proposal: `4f7b5c8df63a198e6d4c121d7135f3305f36f8f1`.
- The actual r5 post-test payroll UI readback equals the complete baseline root. The readback file SHA matches `proposal-delta.json`.
- Both r6 screen/paste forms are semantically identical.
- Across all 86 named controls, exactly nine properties differ. Control identity, type, parent, order, visibility, action formulas, calculation formulas, displayed amounts/bases and data references are otherwise unchanged.
- The nine changes are root Align/OverflowX/OverflowY, four immediate-child Width properties, and body Height/OverflowY. Root placement and external width/height ratios remain unchanged.
- Proposal delta entries, before/after values, property hashes and four standalone formula files match the actual YAML.

## Requirement decision remains open

Current SCR005-UI-004/015 explicitly require the summary and target controls to stay fixed while the body scrolls. The narrow-screen guidance calls for wrapping. The proposal introduces two exceptions:

1. When the root content width is below 750px, use a 750px readable content width and allow horizontal navigation.
2. When narrow or when the remaining body height is below one readable row plus existing body padding, move vertical scrolling to the root, including the summary and target controls.

These are material UI behavior choices, despite changing no payroll logic. They must be approved before applying the proposal or presenting it as confirmed specification. The local review does not grant that approval.

## Why these nine properties were selected

The initial three-property low-height repair (root scrolling, intrinsic body height, body overflow hidden) restores a usable vertical scrolling extent but does not address independently observed narrow text clipping. The r5 450px effective-width evidence shows the final basis label has only about 36.6 logical pixels of width and its text exceeds the 128px available height.

An additional responsive actions-height formula would fix the known 190+190+136px button-wrapping issue, but would still leave the target staff label and deduction basis text compressed. Full narrow-screen stacking is a separate, larger responsive-layout design.

Using four `LayoutMinWidth` properties could be smaller, but its precise interaction with explicit Width and parent Stretch needs actual runtime proof. The chosen root Align.Start plus four explicit `Width=Max(750,Parent.Width)` formulas directly specifies the intended content width.

The narrow-mode predicate also selects root vertical scrolling. This prevents a horizontal root scrollbar from reducing the normal fixed-body viewport while the body Height still assumes the full root outer height. No guessed scrollbar thickness is subtracted.

## Content width and threshold derivations

The 750px minimum comes from the unchanged target controls:

`116 + 150 + 260 + 168 + 3*8 + 16 + 16 = 750`.

The 128px minimum readable row comes from the larger branch of every unchanged deduction-row Height formula, `If(Parent.Width<750,128,64)`. A source guard locks all eight formulas to that contract. The existing 12px top and 20px bottom body padding are referenced dynamically.

The narrow fixed-region total is `64+108+104=276`, giving a low-height threshold of `276+12+20+128=436`. When the root reaches 900px width, the target height changes to60 and the threshold becomes388. Equality selects ordinary fixed mode, provided root width is at least750.

No actual row Width or Height participates in the mode predicate. Therefore changing scrollbar ownership cannot flip the predicate through a row breakpoint or introduce resize-history-dependent mode selection.

At minimum body width750, modeled basis widths are about250.4px with a12px body gutter and257.6px without that gutter. Tests include gutters0/12/15/17 and retain at least247px. Actions have at least669px before their child content, which is sufficient for the unchanged532px button row. These are bounds from source geometry, not measured text-fitting results.

## Body intrinsic-height review

The Height expression lists each of the seven direct body children exactly once as a numeric Height and a Visible flag. It sums visible heights, adds exactly `max(0, visibleCount-1)` actual body gaps, and adds both body paddings. This avoids phantom gaps when state/earnings/deductions are hidden.

The mode-dependent body OverflowY is the inverse of root OverflowY. Body FillPortions remains0. None of the direct child Height formulas depends on body Height, and the explicit layout-property dependency graph has no cycle. The prototype label's implicit runtime defaults are a separate audited input supplied by the implementation task: FillPortions0, LayoutMinHeight40 and AutoHeight false in the official baseline export. Its actual Height is referenced rather than hard-coded in the candidate.

The existing earnings overflow property is unchanged. Its aggregate Height already represents its eight children and seven gaps, so a declared Scroll value alone does not prove a second active scroller. Actual overflow must still be checked after compilation.

## Known side effects and runtime gates

- In a wide but short fallback, root vertical scrollbar width can produce a small incidental horizontal pan because explicit child Width uses the root outer Width. Do not hide this by programmatically changing hidden ancestors or adding guessed pixel compensation.
- At ordinary900/1366/1920 viewport examples, root width is already above750, no root vertical gutter is introduced and the existing body Height branch is retained verbatim. Model parity does not replace measured regression tests.
- Studio's outer preview independently clips part of the logical app at native200%. Its legitimate outer scrollbar may need to be moved to expose the root's bottom edge. The r6 root repair does not change that external host viewport. Player must be measured separately when authorized.
- Test root width749.999/750/750.001, height thresholds immediately below/on/above436 and388, the target breakpoint900, actual required viewport sizes and native200% effective viewport.
- At450/683/960 effective widths and native200%, reach all last-row name/basis/amount fields, show their text fits inside their own rendered controls, and capture their complete clipping-ancestor chain.
- Verify normal-mode summary stays fixed while body scrolls; fallback has one active vertical content owner and both horizontal extremes are user-reachable.
- Test ordinary pointer and keyboard/focus navigation, including Home/search/recalculate controls. DOM scrollLeft assignments alone do not establish user reachability.
- Test100% to200% to100%, short to tall, narrow to wide, and collapse/expand while scrolled. Ensure root/body offsets reset or clamp correctly and do not retain an invisible scrolled-away summary.
- Test source-derived750 target row fit and default control padding/font behavior in the actual Power Apps engine. Formula/YAML checks do not compile Power Fx.
- Preserve named state-retention, invalidation, amount/basis and regression gates. No selector, clipping check or expected value should be weakened to accept this proposal.

## Independent tests and reproduction

Run from the candidate repository, using the review directory containing this document:

`PYTHONDONTWRITEBYTECODE=1 python <review-directory>/test_independent_r6_layout.py`

The portable script finds the candidate repository from the current directory or its own ancestors. It reverses the nine reviewed properties and validates the resulting root against the frozen r5 semantic SHA. It does not require or bundle the private r5 export/readback. The original review separately compared that complete readback against the r5 source. The portable script writes only its review result JSON. It checks eleven groups, including all128 visibility combinations with768 randomized intrinsic-layout fixtures, boundary modes, source contracts, unchanged control structure, complete nine-property scope and dependency cycles. The portable readback assertion is a frozen-hash check, not a fresh read of the original runtime export.

- `independent-r6-test.log`:11/11 PASS.
- `independent-r6-results.json`: source hashes and explicit unapproved/runtime-not-run limits.
- The fixture with proto40, earnings540, open narrow deductions1240 and UiReady true yields body intrinsic Height2064; this reproduces the aggregate arithmetic only and is not a runtime measurement.

## Microsoft primary-source basis

Microsoft documents Start/Stretch alignment, gaps, Scroll/Hide overflow and the role of fill portions in [Vertical container control](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/controls/control-vertical-container). These properties support the chosen explicit-width/scroll-owner approach, but do not prove its exact runtime behavior.

[Building responsive canvas apps](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/build-responsive-apps) describes auto-layout containers and highlights interactions and limitations among wrapping, alignment and overflow. That is why actual preview/Player tests remain mandatory.

[Create responsive layouts](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/create-responsive-layout) explains the distinction between app/device dimensions and minimum logical screen dimensions. The observed Studio outer viewport is therefore not interchangeable with root Height or a width-only zoom model.
