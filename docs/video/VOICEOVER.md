# Mux Kalyan Dhar’s voiceover

The cloud product video is **picture + captions**. His voice was recorded on a Windows PC that was powering off:

`C:\Users\kdhar\Documents\Sound recordings\Recording (4).m4a`

That file was **not** in the GitHub worktree (`docs/video/` had no `.m4a` / `.wav`). The cloud agent could not clone his voice.

Do **not** commit the m4a to the public repo.

## Align to the picture

1. Read [SCRIPT.md](SCRIPT.md). Section clocks are the edit.
2. If the m4a is a single take that already follows this order, mux it.
3. If he paused, split the m4a on silence and lay the pieces on the section clocks (0:08, 0:52, 1:35, 2:20, 4:00, 4:52).
4. Keep [captions.srt](captions.srt). Re-time only if his read drifts more than ~0.4 s.

## Process the voice (requested chain)

High-pass, compress, presence, loudnorm about **-14 LUFS**, limiter, no clip.

From the repo root, with the m4a copied next to the silent master (do not git-add it):

```bash
MASTER=docs/video/neural_path_finder_product.mp4
VO="docs/video/local/Recording (4).m4a"

ffmpeg -y -i "$MASTER" -i "$VO" -filter_complex "\
[1:a]highpass=f=80,\
acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=4,\
equalizer=f=3500:t=h:width_type=h:width=1800:g=3.5,\
equalizer=f=220:t=h:width_type=h:width=100:g=-2,\
loudnorm=I=-14:TP=-1.5:LRA=9,\
alimiter=limit=0.97:attack=5:release=50[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -shortest -movflags +faststart \
  docs/video/neural_path_finder_with_vo.mp4
```

Check true peak after the first pass (`TP` should stay under **-1.5 dBTP`). If the take starts late, add `-itsoffset 0.08` before `-i "$VO"` and raise it until “This is Neural Path Finder” hits **0:08**.

Optional two-pass loudnorm: run once with `loudnorm=…:print_format=json`, then a second pass with the measured `measured_I` / `measured_TP` / `measured_LRA` / `measured_thresh` / `offset`.

## What not to do

- Do not put generic TTS on the timeline and credit **Kalyan Dhar**.
- Do not force-push.
- Do not commit a huge mp4 or the private voice file to `origin/main`.
