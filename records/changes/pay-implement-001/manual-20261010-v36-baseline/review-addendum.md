# v36 baseline review addendum

The original v35/r4 candidate review remains historical evidence. This addendum rebinds its unchanged formulas and named control structure to the published36 export.

- All9 App/screen YAML and _EditorState are byte-identical. CanvasManifest is absent from both packages; absence is not a byte-equality observation.
- The exact full-file guard passed unchanged, and both regenerated candidate screen bytes match r4.
- The browser inspector matched372 controls by identity;318 internal ControlUniqueId values were renumbered. Actual modernButton count is51 in both; cached Properties52→51 corrects the prior aggregate. No named component was deleted.
- DataSources matches after nested JSON decoding and MetadataId-array normalization. The four changed TableDefinition strings differ in relationship-array order, not connection or field meaning. Header save time and Properties timing/Id fields reflect the newer authoring save.
- Therefore only current-baseline descriptions/evidence are changed. The14 property changes and one summary parent move remain the same candidate.

This is not approval of applying or publishing the repaired UI. Recheck current editing version immediately before any application. Independent review of this metadata-only rebind and final commit/privacy checks remain separately required.
