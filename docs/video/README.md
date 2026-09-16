# Neural Path Finder — product video

~5 minute exhibit film: live Azure demo + architecture walk + captions for Kalyan Dhar’s voiceover.

| File | Role |
| --- | --- |
| [SCRIPT.md](SCRIPT.md) | Timed narration (~5:08), section by section |
| [captions.srt](captions.srt) | Burned-in captions (same words as the script) |
| [captions.ass](captions.ass) | 1080p-styled captions used by the rebuild tool |
| [VOICEOVER.md](VOICEOVER.md) | How to mux `Recording (4).m4a` at about −14 LUFS |
| [tools/build_product_video.py](tools/build_product_video.py) | Re-record live site + GitHub, rebuild the mp4 |
| `neural_path_finder_product.mp4` | Picture + captions; **local artifact, not in git** |

## Voice status

**Not included.** Searched `docs/video/**` and the worktree for `.m4a` / `.wav` / voice takes. Kalyan’s recording stayed on the Windows PC that was shutting down. The mp4 must not be labeled as if he already spoke on it.

## Cloud build (this run)

| | |
| --- | --- |
| Master (local, gitignored) | `docs/video/neural_path_finder_product.mp4` |
| Duration | **5:08** (308 s) |
| Picture | Live https://fruitfly-poc.azurewebsites.net/ plus GitHub `ARCHITECTURE.md` / README + mermaid stills |
| Audio | Silent AAC bed only — **not** Kalyan Dhar |
| Size | ~33 MB (do not commit to the public repo) |

## Rebuild (cloud or laptop)

Python 3.12+, Playwright Chromium, ffmpeg.

```bash
python3 -m pip install playwright pillow
python3 -m playwright install chromium
python3 docs/video/tools/build_product_video.py
```

Writes `docs/video/neural_path_finder_product.mp4` (gitignored).

Live origin used for the demo: https://fruitfly-poc.azurewebsites.net/  
Architecture origin: https://github.com/kalyandhar84/fruitfly/blob/main/docs/ARCHITECTURE.md
