# Maharaj katha for children

One authorized excerpt of HH Radha Govind Das Goswami Maharaj becomes a short illustrated film. His recording is the narration. The pictures are stills with a slow camera. A separate eight-second test shows image-to-video on one frame.

The lecture hearing in `work/vatsalya-lila` is a different job. This folder does not transcribe, and it does not touch part 12.

## This computer

Checked 29 Oct 2026.

| Item | What is here |
|---|---|
| System | Windows 11 Pro, 64-bit |
| CPU | Intel Core i7-10750H, 6 cores |
| Memory | 32 GB, about 15 GB free at the time |
| GPU | NVIDIA Quadro T2000, 4 GB, plus Intel UHD |
| Disk | 125 GB free on C: |
| Python | 3.12 in this project, via uv. A system 3.13 is also installed. |
| Node | 22 |
| FFmpeg on the PATH | not installed |
| ComfyUI | not installed |
| Encoder used | PyAV's libx264, on the CPU, so the GPU stays with the hearing |

A current image-to-video model that looks like the reference film wants about 8 GB for Wan 2.2's 5B model and 12 GB or more for a comfortable LTX or Hunyuan run. Four gigabytes cannot hold those weights. Quantized builds that claim to squeeze in are slow, and they fight the hearing, which was using the GPU at about 97 percent. No video model was installed.

## Three ways to make the pictures move

| | This laptop, stills | Stills here, motion in the cloud | Mostly cloud |
|---|---|---|---|
| Hardware | What is already on the desk | Same, plus an account | A browser |
| Install | Already done. `alaya-katha` is in this repo. | A named image-to-video service | Kling, Runway, Luma, or a similar editor |
| Picture | The ten frames in episode 01 | Same frames, sent out for motion | Generated off the machine |
| Time for one episode | Minutes to cut and render the camera moves | Often one to five minutes per shot, so a few hours for forty shots | Similar, and the queue is theirs |
| Money | No extra subscription for this pilot | Roughly a few dollars to about twenty dollars for forty short clips, depending on the service. Not purchased. | A monthly plan. Not purchased. |
| License | The stills and the one motion test were made in this Cursor session. Confirm the plan's output terms before a public upload. | Each service has its own commercial rule. Read it before a children's channel uses it. | Same |

ChatGPT, Claude, Google, Gamma, and Google Flow were not called.

## What was chosen

Śrīmad-Bhāgavatam 10.11.11, the woman who brought pilu and whose basket filled with jewels. Two people. One lane and a forest path. No fight and no crowd.

The contiguous telling, from “अब भीलनी की कथा” through “सोने से, हीरे से,” is 5 minutes 30 seconds. Stopping earlier would cut his sentence. Continuing would enter the kitchen story, which has a knife and blood and is a poor first film for children. The 5:30 cut is the whole pastime up to the jewels.

Other windows, not built:

- Part 1, Krishna feeds his reflection. About two minutes, and he runs at the end.
- Part 1, from waking to Mother's lap. About four minutes. A good second episode: only Yashoda and Krishna, inside one room.

## Repeat an episode

```powershell
.\.venv\Scripts\python.exe -m katha_video.cli assemble work/katha-video/01-bhilni-fruit
.\.venv\Scripts\python.exe -m katha_video.cli qc work/katha-video/01-bhilni-fruit
```

`uv sync` could not install the `alaya-katha` command while part 12 is being heard, because that hearing has `alaya-lecture.exe` open. After the hearing finishes, `uv sync` registers the shorter command `uv run alaya-katha`.

The command reads `03_storyboard/storyboard.json`, cuts `01_source_audio`, writes `07_audio_mix/narration.m4a`, `08_edit_project/picture.mp4`, and `09_final_exports/bhilni-katha-pilot.mp4`.

New episode: copy the folder shape, point `source_audio` at an authorized file, set `audio_start` and `audio_end` on a sentence boundary, and make one 16:9 still per shot from the locked sheets in `prompts/STYLE.md`. Then run the same command.

## Publishing

Say in the description that the pictures are illustrated and the voice is Maharaj's own lecture. Suggested line: “Pictures illustrated for children. Voice: HH Radha Govind Das Goswami Maharaj, unedited, from Vatsalya Lila.” No channel name or watermark is burned in, because none was supplied. Hindi captions are `02_transcript/hindi.srt`.

## Still needed from you

- Is this Krishna, this woman, and this lane the lock for later episodes?
- Is the small red bindi acceptable on the fruit seller?
- A channel name and a watermark, if the film should carry one.
- Whether a later pass may use a paid image-to-video service. This 4 GB GPU cannot match the reference film's motion locally.
- Part 12 is still being heard. Say when that GPU may be used for something else.
