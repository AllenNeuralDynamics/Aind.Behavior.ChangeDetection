# All-images stimulus fix

This repository version addresses the passive DoC 7-of-8 image problem without changing the
OpenScope launcher.

## Summary of the issue

The intended image path for the passive DoC task is:

```text
Path -> EnumerateFiles -> Variation(Count=8) -> LoadImages -> Concat -> SelectedImages
SelectedImages + Random -> Permutation -> CloseCycle -> presentation sequence
```

Two independent things need to be true:

1. `Variation` must receive the enumerated image-file stream as `Source1` and the `Random` stream
   as `Source2`. In an intermediate edit, the workflow was left in a malformed state where
   `Random` was connected to `Variation` as `Source1`, while `EnumerateFiles` bypassed `Variation`
   and fed `LoadImages` directly. That graph can run, but it is not the intended Bonsai topology
   and makes the selected-image stream difficult to reason about.

2. `CloseCycle` must be loaded as a real custom Bonsai combinator, not as a red unresolved proxy.
   This operator appends the first image in each randomized permutation once more at the end of the
   sequence. This is necessary because the task uses the first image as the starting state and then
   logs/presents transitions. Without the closing item, one image is systematically absent from the
   transition sequence.

## Workflow change in this patch

The image-loading branch in `src/DetectionOfChange_with_template_and_mpe_comp.bonsai` has been
restored to the valid original topology:

```text
Random         -> Variation Source2
EnumerateFiles -> Variation Source1
Variation      -> LoadImages Source1
```

The downstream presentation-order branch is kept as:

```text
SelectedImages -> Permutation -> CloseCycle -> CreateObservable -> Concat -> task
Random         ----------------^
```

This means the task should use all 8 files from `stimuli/images_A`, randomize their presentation
order, and close the transition loop so the initially displayed image is also reached by a later
transition.

## Important runtime note

`CloseCycle` is source code in the repo, but Bonsai loads it from `Extensions.dll`. Git does not track
`bin`, `obj`, or `*.dll`, so a fresh checkout will not contain the compiled extension.

Before running the workflow after a fresh checkout, build and copy the extension:

```bat
cd /d C:\BonsaiDataDoC\Code\Aind.Behavior.ChangeDetection
call build_extensions.cmd
```

Then confirm the DLLs exist:

```bat
dir /S /B Extensions.dll
```

You should see at least:

```text
C:\BonsaiDataDoC\Code\Aind.Behavior.ChangeDetection\src\Extensions.dll
C:\BonsaiDataDoC\Code\Aind.Behavior.ChangeDetection\bonsai\Extensions.dll
```

When opened in Bonsai, `CloseCycle` should not be red. If it is red, the custom operator is not being
loaded and the task is not fixed.

## Suggested validation after a short test run

After a 2-3 minute test run, check the event log:

```bat
python scripts\check_bonsai_event_log_images.py C:\path\to\bonsai_event_log.csv --expected-count 8
```

Expected result:

```text
Unique presented images: 8
Missing expected images: none
```

This is a post-run diagnostic only. It does not hard-fail the Bonsai task during acquisition.
