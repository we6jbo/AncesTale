# AncesTale

**From family records to an interactive family-history adventure.**

AncesTale is an evolving, open-source genealogy software project built around a C++/Qt desktop application, a SQLite-backed research library, and an envisioned web adventure game. The long-term goal is to make historical family connections easier to explore, verify, and experience through interactive storytelling.

**Status: active development and research prototype.** The signed genealogy viewer and research-preparation workflow are being developed and tested. A LAN-hosted browser alpha was tested November 14, 2026. Invitation acceptance by SMTP, live HTTP deployment, and the ending chime were reported; individual track playback and player activity were not independently verified. Version 0.7.3 adds a prepared recovery adventure and desktop fixes; on-device integration and compilation must still be verified.

## Why AncesTale?

Family trees often live in static tables. AncesTale explores what happens when careful research becomes the foundation for a living, interactive experience. Imagine following historical relationships through generations, opening a source for a claim, and exploring a story without treating an uncertain match as established fact.

This project welcomes contributors interested in **Qt/C++, SQLite, cybersecurity, genealogy, trustworthy AI agents, accessible interfaces, web storytelling, and open-source collaboration**.

## Current engineering direction

- **Qt desktop interface:** displays genealogy records read through the C++ library and offers a dedicated *Prepare Mistral Vibe Research* workflow.
- **Signed data and library:** existing signed `story.db` and `libhvza.so` use public-key signature verification. The intention is to detect changes before protected data is accepted; verification is not an assurance that genealogy claims are true.
- **Linux integrity monitoring:** a separately installed login-time certificate-checking service and Linux Audit monitoring have been configured on the development workstation. They are **not automatically installed by this repository**.
- **AI research handoff:** the application prepares local instructions and structured snapshots for Mistral Vibe. It copies a terminal command to the clipboard; **the GUI must never start Vibe, execute the script, or launch a shell automatically**.
- **Evidence-first genealogy:** research must separate verified records from tentative identifications, preserve stable identifiers, and provide citations. Existing Pedigree interchange data remains unchanged unless the user explicitly authorizes an import.
- **Crash recovery:** favor durable checkpoints and inspectable logs during long-running research.

## Adventure game and recovery prototype

We are exploring a browser-based family-history adventure that draws from reviewed genealogical relationships and documented historical events. Plans include historical exploration, linked sources, interactive narrative, and carefully verified public-domain music. The early LAN-only prototype is hosted on a Raspberry Pi. A nine-day prewritten recovery adventure is provided for November 21–29 (9 AM–3:30 PM Pacific), gated by owner approval and intended only when live AI assistance fails.

**A genealogy record is not game-ready merely because it exists in the database.** Before rendering or publishing, a separate export/review layer must check the accuracy, provenance, living-person privacy, and rights for the data used.

## Getting started for developers

### Requirements

- Linux workstation with a recent C++17 compiler and CMake (3.21 or newer for the currently supplied project snapshot).
- Qt 6 development libraries with the `Widgets`, `Network`, and `Multimedia` modules and Qt Creator (recommended).
- OpenSSL development libraries for the certificate-verification implementation.
- The existing AncesTale signed runtime components, installed separately and verified before use. **The public source repository may deliberately omit the database, compiled library, certificate, and signatures.**

### Build location policy

The maintainer's workstation has a strict, non-negotiable project root:

`/home/we6jbo/Projects/AncesTale/`

**All AncesTale GUI source code, project-generated source, and build output must remain under that exact root.** Do not create sibling project directories such as `AncesTale-fold2` or `AncesTale-build`. Use an in-project build directory, for example:

`/home/we6jbo/Projects/AncesTale/build/Desktop_Debug/`

Open `CMakeLists.txt` in Qt Creator, configure an **in-project** build directory, then build. A public source checkout by itself may not be runnable because signed local runtime dependencies are intentionally separate. Do not bypass signature verification to make the demo work.

Research handoff files may intentionally be prepared in `/home/we6jbo/.ancestale/` and `/tmp/ancestale/`. These are **runtime data and instructions, not locations for GUI source or compilation output**.

### Manual research launch

After running the GUI and clicking **Prepare Mistral Vibe Research**, and only after the GUI reports preparation success, the user may manually paste:

```bash
bash /tmp/ancestale/run.sh
```

This runtime file is not present merely because the project was installed. A reboot may clear `/tmp`. The exact Mistral Vibe invocation needs verification against the CLI installed on the workstation.

## Areas where contributions help

| Area | Example contributions |
| --- | --- |
| C++ / Qt | clearer user feedback, accessibility, tests, safe error handling |
| Data verification | reproducible signature checks, threat modeling, tamper-alert testing |
| Genealogy | source provenance, APA citation tools, uncertainty handling, schema tests |
| AI agents | safe research handoffs, prompt-injection resistance, checkpoint recovery |
| Game development | narrative prototypes, browser interface, historical-event modeling |
| Documentation | developer onboarding, diagrams, test instructions, translations |

AI-assisted contributions are welcome when a human reviews generated work, documents its provenance, tests changes, and confirms that no private records or secrets enter a public pull request. Genealogy sources and external web pages are **untrusted data**, never operational instructions for an agent.

## Security and responsible disclosure

Digital signatures can help detect unauthorized modification of a file; they do not verify historical truth and cannot guarantee a system is compromise-proof. The private signing key and signing credentials must not be committed, exported, or disclosed. Do not edit or re-sign `story.db` or `libhvza.so` outside the authorized password-protected signing workflow.

Please avoid posting vulnerabilities, private records, or credentials in public issues. Contact the maintainer privately through an appropriate project contact channel if one is published. No security-response SLA is represented by this document.

## Privacy, copyright, and publication

- No automatic upload or publication of the complete family tree.
- Default to local research, then explicitly review data before any public export, screenshot, or game scene.
- Keep personal labels and sensitive family relationships out of generated public text unless their release is approved.
- Review rights in memorial records, documents, screenshots, images, and music independently of the code license.
- Existing signed genealogy data and backups must not be rewritten by a documentation or packaging update.
- Historical source material and user records may have different copyright and privacy statuses from the program source.

## Licensing

For **original AncesTale code that the maintainer has authority to license**, the proposed three-way choice is:

**MIT OR Apache-2.0 OR GPL-3.0-only**

The options are intentionally listed in that order. **Choose one:** MIT and Apache 2.0 are permissive options; GPLv3 is a copyleft option. Choosing MIT does *not* require GPLv3 source-sharing obligations. See [`LICENSE`](LICENSE) and the complete texts in [`LICENSES/`](LICENSES/). Third-party components and genealogy data are not automatically covered.

Before publishing this licensing declaration, the maintainer should confirm ownership of the affected source and compatibility with all incorporated third-party code, including any external libraries.

## Project links

- **Source repository:** https://github.com/we6jbo/AncesTale
- **Development blog:** https://j03.page/2026/11/12/secured-roots-developing-the-ancestale-web-game/

## Project philosophy

**Build openly. Verify carefully. Keep people and sources at the center of the story.**

## v0.7.3 recovery

See [release notes](RELEASE-073.md) for the alpha fixes, fallback schedule, tests and limitations. The fallback is prewritten and cannot replace arbitrary AI research. Original music recordings, private credentials, player data and runtime logs are not included in the public release.


## v0.7.4 Continued Research
Native Qt tab reads the private AncesTaleextended JSON queue, refreshes every second, supports search, pending/resolved filtering, evidence review, manual addition, resolution/reopening and copyable Vibe prompts. See workflow/CONTINUED-RESEARCH.md. The JSON is not bundled or published.


## v0.7.5 — Extended integration
Private read-only collection of AncesTaleextended research, family groups, music metadata and screenshot inventory; guided local review, tab arrows, per-tab text size. Vibe prepares reviewed Pi and publication outputs under existing rules. No automatic public upload.

## v0.7.6 — Narrated adventure
Browser-local narration controller, larger adjustable text, independent speech controls, music ducking and narrated recovery preview. Alpha Test 2 is documented in workflow/alpha2-20261114.md; live Pi integration and voice availability must be tested on the player browser. See RELEASE-076.md.

### v0.7.7 media staging
Run the release kit setup-media.py to prepare /home/we6jbo/1/; review readme.md there. Movies / Voices tab scans the index with ffprobe. Hosted narration and cinema helpers require actual reviewed downloads, Piper installation and verified Pi deployment. Long-session content and asynchronous branch request integration are Vibe requirements, not a completed dynamic game engine.
