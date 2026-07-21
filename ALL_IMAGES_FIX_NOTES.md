# All-images stimulus fix

This patch addresses two independent failure modes:

1. `CloseCycle` is a custom Bonsai extension, so a fresh checkout must build `Extensions.dll`
   before running Bonsai. The repo ignores `bin`, `obj`, and `*.dll`, so these artifacts are not
   present after a fresh `git clone`/checkout.

2. The stimulus selection branch previously used:

   EnumerateFiles -> Variation(Count=8) -> LoadImages -> SelectedImages

   For an experiment intended to use all available images in `stimuli/images_A`, this branch should
   not randomly select a subset before loading images. The workflow is changed to:

   EnumerateFiles -> LoadImages -> SelectedImages

   The downstream branch still randomizes presentation order:

   SelectedImages -> Permutation -> CloseCycle -> task sequence

Run `build_extensions.cmd` after each fresh checkout, or run `run_detection_of_change.cmd`, which
builds the extension and then launches the workflow from the `src` folder.
