# Independent review of r5 layout E2E additions

## Final source review result

PASS. The body-scroll and ancestor-clip helpers correctly target the known clipping regression. They do not move the hidden deduction scroller or use scrollIntoView to conceal clipping. All three initial review findings below have been addressed in the reviewed revision. Final file identities are recorded in `reviewed-source-test-hashes.json`. This is source and synthetic-helper acceptance, not application acceptance.

### Verified properties

- The scroller must have computed vertical overflow auto/scroll, a positive scroll range, and its nearest named control must be conPayBody. Nested named controls cannot qualify.
- Only that scroller's scrollTop is assigned. No hidden ancestor's scroll position, overflow, height, or style is changed.
- Reaching the body's actual bottom is asserted within 1px.
- Name7, Basis7, and Amount7 each require near-complete viewport intersection, positive area, and no clipping by any current-document ancestor whose overflow is auto/scroll/hidden/clip.
- Ancestor client edges are calculated from border-box bounds, client border offsets, and client dimensions. Scale factors account for the axis-aligned scaling seen in preview. This calculation is not a general rotated/skewed-transform or clip-path validator.
- The revised helper also collects nonempty text-node Range rectangles and checks them against the text parent and all ancestors, including the label itself. This detects ordinary internal text overflow/ellipsis that exceeds a clipping ancestor. Each label must supply at least one rendered text rectangle. This does not replace actual font/readability or occlusion assessment.
- The 450/683/960 cases explicitly retain height 768 and identify themselves as horizontal reflow stress, not actual browser 200% zoom. An eventual pass cannot be reported as actual 200% verification.

### Initial findings and resolution

1. RESOLVED: WIDE/REFLOW initially only checked a non-null summary bounding box and an unchanged Y coordinate. The revised tests require summary viewport intersection ratio 0.99 both before and after scrolling.
2. RESOLVED: Before the pre-scroll geometry is sampled, waitForPayrollGeometry now polls four named regions and requires two consecutive equal snapshots after the first observation. Missing regions cannot pass. The explicit geometry wait materially reduces the immediate-resize race; it is not a proof that a later asynchronous event can never occur.
3. RESOLVED: The helper now inspects rendered text-node ranges as well as control rectangles. Internal horizontal/vertical text clipping and absence of rendered text are included in the synthetic negative checks. Actual reading quality and actual 200% remain separate Player gates.

## Independent helper execution

`node test_e2e_helpers_mock.cjs` executes the reviewed helper functions after TypeScript type stripping against synthetic DOM objects:

- Old wide: advertised 698 / content 728 rejects.
- Old narrow: advertised 698 / content 1240 rejects.
- Correct wide: advertised 728 / content 728 accepts.
- Correct narrow: advertised 1240 / content 1240 accepts.
- All four are repeated at axis scale 1 and 0.681.
- In every fixture, the hidden deduction scrollTop remains 0 and only the body reaches its bottom.

Additional cases reject internal horizontal text overflow, internal vertical text overflow, and missing rendered text; another two establish that changed geometry waits for stable snapshots and missing geometry is rejected.

Result: 13/13 expected outcomes; 11 test cases registered; TypeScript syntax accepted by Node's type stripper. This is a helper mock execution, not an official TypeScript type check, Playwright browser run, or Power Apps test. The viewport assertion is stubbed so these fixtures independently exercise the explicit ancestor-clip calculation rather than pretending to test browser intersection behavior.

## Primary references

[Playwright toBeInViewport](https://playwright.dev/docs/api/class-locatorassertions#locator-assertions-to-be-in-viewport) documents viewport intersection and its ratio threshold. The separate explicit ancestor checks avoid relying only on an unqualified visibility assertion.

[MDN getBoundingClientRect](https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect) defines viewport-relative border-box bounds. [MDN clientWidth](https://developer.mozilla.org/en-US/docs/Web/API/Element/clientWidth) defines the inner width excluding border and vertical scrollbar. These support the reviewed scrollport-edge calculation for ordinary axis-aligned scaling.

## Final small revision

The 1366 and 900px cases now use the same 0.99 summary visibility ratio before and after body scrolling; the redundant narrow assertion was removed. The README now explicitly includes deduction-container Height in the full-v36 application order. Both changes preserve the one-property core fix. All 8 source/model checks and 13 helper mock cases were rerun successfully. Final hash coverage includes 23 files, adding the new r5 layout static test to the earlier 22-file set.
