# Lecture builders

`_build_vatsalya_01.py`, `_build_vatsalya_02.py`, `_build_vatsalya_04.py`, and `_build_vatsalya_05.py` are the pattern for a finished part. `_build_p6.py` is the Damodar Lila part 6 builder. Leave that file as it is.

A new part gets `_build_vatsalya_NN.py` with:

- `RANGES`, inclusive raw cue numbers, contiguous from 1 through the last cue
- `GROUPS`, one Hindi paragraph and one English paragraph per range
- `CLIPS`, rows of kind, start cue, end cue, topic, and what he says

Run from the repository root:

```powershell
uv run python transcriptions/_build_vatsalya_NN.py
```

The script writes into `work/vatsalya-lila/part-NN/` once its `ROOT` path points there.
