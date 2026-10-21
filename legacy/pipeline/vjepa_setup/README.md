# V-JEPA 2.1 ViT-B/16 (384) - Setup & Test

This folder contains everything needed to test V-JEPA 2.1 on a GPU machine.

## What's in here
- `setup_windows.bat` / `setup_linux.sh` - creates a Python venv and installs dependencies
- `extract_clip.py` - cuts a short clip out of a video (uses OpenCV, no ffmpeg needed)
- `vjepa_embed.py` - loads V-JEPA 2.1 ViT-B/16 (384) and extracts an embedding from a clip
- `sample_rally1.mp4` - a 16s sample badminton rally clip, ready to test with

## 1. Setup

### Windows
```
setup_windows.bat
```

### Linux
```
bash setup_linux.sh
```

This creates a `vjepa_env` virtual environment and installs everything in
`requirements.txt` EXCEPT torch/torchvision (those need a build matching your
specific GPU driver).

## 2. Install PyTorch with CUDA

Activate the environment first:
- Windows: `vjepa_env\Scripts\activate.bat`
- Linux: `source vjepa_env/bin/activate`

Then check your GPU driver's CUDA version:
```
nvidia-smi
```
Look at "CUDA Version: X.Y" in the top right of the output.

Go to https://pytorch.org/get-started/locally/, select your OS + the CUDA
version closest to (but not higher than) what `nvidia-smi` shows, and run the
install command it gives you. For example, for CUDA 12.1:
```
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

## 3. Verify GPU is detected

```
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)"
```

This MUST print `CUDA available: True` before continuing. If it prints
`False`, the torch build doesn't match the driver - go back to step 2 and
try a different CUDA version (e.g. cu118, cu124).

## 4. Run the test

This will download the V-JEPA 2.1 ViT-B/16 (384) weights on first run
(requires internet, ~1-2GB download), then extract an embedding from the
sample clip:

```
python vjepa_embed.py sample_rally1.mp4 --out sample_embedding.npy
```

Expected output: device = cuda, then a series of shapes, ending with
"Saved embedding to sample_embedding.npy".

## 5. Send back the results

Please send back:
- The full console output of step 3 (GPU check)
- The full console output of step 4 (embedding extraction)
- The generated `sample_embedding.npy` file

## Extracting your own clips

To cut a clip from any video (start/end in seconds):
```
python extract_clip.py your_video.mp4 --start 8 --end 24 --out clip.mp4
```

To get an embedding for a time range directly from a full match video
(without a separate cut step):
```
python vjepa_embed.py your_video.mp4 --start 8 --end 24 --out clip_embedding.npy
```

## Building the training dataset (7 videos + ground truth)

1. Put your 7 match videos in `dataset/videos/`, e.g.:
   ```
   dataset/videos/match1.mp4
   dataset/videos/match2.mp4
   ...
   ```

2. Put the matching ground-truth CSV for each video in `dataset/labels/`,
   using the **same base filename** as the video, e.g.:
   ```
   dataset/labels/match1.csv
   dataset/labels/match2.csv
   ...
   ```
   Each CSV needs a start/end column per rally (MM:SS, H:MM:SS, or seconds
   are all fine - e.g. `start_time`/`end_time` or `start`/`end` or
   `Start (sec)`/`End (sec)`), plus your label columns
   (`win_point_player`, `win_reason`, `ball_types`, `lose_reason`,
   `roundscore_A`, `roundscore_B`, etc). Extra columns are kept as-is.

3. Cut all rally clips (runs locally, no GPU needed):
   ```
   python build_clips.py
   ```
   This writes one clip per rally into `dataset/clips/<video_name>/rally_NNN.mp4`
   and an index file `dataset/clips_index.csv` linking each clip to its labels.

4. On the GPU machine, extract embeddings for every clip:
   ```
   python extract_embeddings.py
   ```
   This writes one `.npy` embedding per clip into `dataset/embeddings/` and
   a final `dataset/dataset.csv` mapping each embedding file to its labels -
   this is the file used to train the winner-prediction probe.

If videos are large, you only need to send `dataset/videos/` +
`dataset/labels/` to the GPU machine (or run `build_clips.py` locally first
and just send the much smaller `dataset/clips/` + `clips_index.csv`).
