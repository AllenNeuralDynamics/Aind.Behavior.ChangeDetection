# All-images stimulus fix

This patch addresses the passive DoC workflow issue in which an 8-image stimulus
folder produced only 7 presented image identities.

## Root cause

The problem is not the image folder: `src/stimuli/images_A` contains 8 TIFFs.
The problem was the image loading / filename pairing subworkflow.

Inside the `LoadImages` `CreateObservable`, the workflow branched each file event
into two paths:

```text
filename -> LoadImage ---------> WithLatestFrom -> (texture, filename)
filename ----------------------^
```

`WithLatestFrom` can drop the first loaded image because the filename branch may
not yet have a "latest" value when the first `LoadImage` output arrives. When
`Variation` randomizes the file order before loading, the dropped first file is
random, which made a different image disappear in different runs.

The fix changes the pairing operator to `Zip`:

```text
filename -> LoadImage -----> Zip -> (texture, filename)
filename ------------------^
```

`Zip` pairs one loaded image with one filename event and waits until both are
available, preserving all 8 images and maintaining the same tuple shape used by
downstream logging and drawing nodes.

## Workflow topology

The intended upstream topology is restored and should remain:

```text
Path -> EnumerateFiles -> Variation(Count=8) -> LoadImages -> Concat -> SelectedImages
Random --------------------------------------^
```

The downstream presentation topology remains:

```text
SelectedImages + Random -> Permutation -> CloseCycle -> presentation sequence
```

`CloseCycle` is still useful because the presentation logic treats the first
image in each randomized order as the initial state. Appending that first image
once more creates the final transition back to the initial image.

## Build step

`CloseCycle` is a custom Bonsai extension. The repo intentionally does not track
`bin`, `obj`, or compiled DLLs. After a fresh checkout, run:

```bat
call build_extensions.cmd
```

This builds `src/Extensions.csproj` and copies `Extensions.dll` into both:

```text
src/Extensions.dll
bonsai/Extensions.dll
```

Open the workflow and confirm `CloseCycle` is not red before running acquisition.

## Validation

After a short test run, validate the event log:

```bat
python scripts\check_bonsai_event_log_images.py "C:\path\to\bonsai_event_log.csv" --expected-count 8 --expected-folder src\stimuli\images_A
```

Expected output should report:

```text
Unique presented images: 8
Missing expected images: none
PASS: found expected unique image count (8).
```

This patch does not add a hard-failure mode to Bonsai acquisition. The diagnostic
script is post hoc only.

## 2026-07-21 follow-up: remove the upstream Variation dependency

After `LoadImages` was changed from `WithLatestFrom` to `Zip`, completed test
runs still showed a 7-image closed cycle: seven unique images followed by the
first image again. This pattern means the downstream `CloseCycle` operator is
active, but the image sequence entering the presentation branch still has only
seven unique images.

For this passive DoC protocol, the intended rule is now explicit: use every
TIFF in the selected stimulus folder. The workflow therefore no longer routes
the image-file list through `Variation(Count=8)`. Instead, the file path is
resolved, all matching TIFF files are enumerated, all are loaded, and the
resulting loaded-image sequence is randomized downstream by `Permutation` and
closed by `CloseCycle`.

Current intended topology:

```text
Path -> EnumerateFiles -> LoadImages -> Concat -> SelectedImages

SelectedImages + Random -> Permutation -> CloseCycle -> presentation sequence
```

`Variation` and its dedicated `Random` input may still appear as disconnected
legacy nodes in older Bonsai editor layouts. They should remain disconnected;
do not reconnect them. They are no longer part of the active image-loading path.

