# Build tools

The `tools/build_pack.py` compiler writes the contents of `pack/`. `tools/check_pack.py` decodes the generated output and checks its specifications.

Requirements: Python 3.14 (including compression.zstd) and cryptography. Install the Python dependency from requirements.txt.

Local inputs, excluded from Git:

- The user's native `Chase Sample WB.fmf`, `Chase Corrected CB.fmf` and `Chase Position Map.fmf` exports in a private native-samples folder outside the installed filter pool.
- `person_filter_metadata.xml` extracted from the installed FM27 search definitions.
- `player-table-factory.json` extracted from the installed PlayerTableFactory Unity definition.

Environment settings:

- `FM27_USER_DIR`: Football Manager 27 user directory containing the native sample exports.
- `FM27_BUILD_INPUTS`: directory containing the two extracted metadata files; defaults to private-inputs in the repository.
- `FM27_NATIVE_SAMPLES`: folder containing the original private exports; defaults to native-samples inside FM27_BUILD_INPUTS.
- `FM27_PACK_PROJECT`: output project root; defaults to this repository.

Run `python tools/build_pack.py`, then `python tools/check_pack.py`. These are local build checks; the samples and game-derived inputs needed to run them are not published. They are not configured as public CI.

Signed integer serialization, native position-mask checks and rejecting unsupported percentage increments are necessary. The initial implementation passed its structural checks while containing display errors. New profiles still need native import checks.

Rebuilding uses fresh encryption IVs, so archive hashes can change while logical contents stay the same. Do not edit installed game assets. The builder does not install files or modify saves.
