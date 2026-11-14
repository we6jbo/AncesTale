# AncesTale 0.2.0 local update

- Source/build stay strictly inside `/home/we6jbo/Projects/AncesTale/`. No sibling project directories.
- This package preserves signed library, DB, signatures, and certificate byte-for-byte. The installer refuses mismatches with existing protected assets.
- Run the accompanying installer pasted into a Manjaro T14 terminal. It checks `t14-finish deadline`, verifies the project directory, certificates/signatures, and backs up affected source files under `.ancestale-backups/` **inside the same root**.
- Open `CMakeLists.txt` in Qt Creator. Configure an IN-SOURCE-TREE build location such as `/home/we6jbo/Projects/AncesTale/build/Desktop_Debug` (not a sibling AncesTale-build directory), then Build and Run.
- The research button checks the signed library and DB, prepares local snapshots and instructions, creates `/tmp/ancestale/run.sh`, and **only copies** `bash /tmp/ancestale/run.sh` to the clipboard. It does not start Vibe.
- Paste the copied command yourself to start interactive Vibe. The script checks local `vibe --help` at runtime. **Vibe CLI syntax was not independently verified here**. Inside Vibe, explicitly ask it to read `/home/we6jbo/.ancestale/begin.md`.
- Screenshot button saves the app window to `~/.38bTqEvQc/ancestale/` and calls `infoartrecorder add ... --project AncesTale` with no shell. Photos remain pending review; no publishing.
- No automated final Pedigree JSON validation/import is claimed. Follow the research instructions, review candidate records manually, and validate before replacing destination. The research agent is instructed to handle final backup/validation, not the GUI.
- The screenshot feature and GUI could not be executed on this host's Manjaro desktop; test on T14 before declaring it working.
- No root-owned service, signing material, or external security configuration is changed.
