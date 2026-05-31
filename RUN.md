# RUN — How to Run SocialDownloaders

---

## One-time setup

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate it
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install FFmpeg (needed for YouTube video+audio merge)
brew install ffmpeg              # macOS
sudo apt install ffmpeg          # Ubuntu / Debian
```

---

## General syntax

```bash
python main.py <platform> [options]
```

---

## YouTube

### Step 1 — Add URLs to `inputs/youtube.txt`

```
# inputs/youtube.txt
https://www.youtube.com/watch?v=qCcQy-haZ-8
https://www.youtube.com/watch?v=Bi-PLwxwvy8
https://www.youtube.com/watch?v=lnxbNxdP9oY
```

### Step 2 — Run

**Interactive mode** (prompts you to choose video or audio, then resolution):
```bash
python main.py youtube
```
```
How would you like to download?
  1) Video + Audio (MP4)
  2) Audio only (MP3)
Enter 1 or 2: 1

Available resolutions: 144, 240, 360, 480, 720, 1080, 1440, 2160
Enter resolution (e.g. 720): 1080
```

**Video at default 720p:**
```bash
python main.py youtube --video
```

**Video at a specific resolution:**
```bash
python main.py youtube --video=480
python main.py youtube --video=720
python main.py youtube --video=1080
python main.py youtube --video=1440
python main.py youtube --video=2160
```

**Audio only (MP3):**
```bash
python main.py youtube --audio
```

### Output
```
downloads/
└── youtube/
    ├── Video Title One.mp4
    ├── Video Title Two.mp4
    └── Video Title Three.mp3   ← if --audio was used
```

---

## Twitter / X

### Step 1 — Add URLs to `inputs/twitter.txt`

```
# inputs/twitter.txt
https://x.com/username/status/1983490168326881676
https://x.com/username/status/1974714529469870396
https://x.com/username/status/1974640905228550295
```

### Step 2 — Run

```bash
python main.py twitter
```

> Chrome will open automatically. Each tweet URL is submitted to twittervideodownloader.com
> and the best available quality (1080p > HD > 720p) is downloaded.

**Sample console output:**
```
Found 3 URL(s) to download. Saving to: downloads/x

[1/3] Processing: https://x.com/username/status/1983490168326881676
  [+] Downloading: https://video.twimg.com/ext_tw_video/.../1080x1920.mp4
  [+] Saved: downloads/x/1080x1920.mp4 (12.4 MB)
  [✓] Done

[2/3] Processing: https://x.com/username/status/1974714529469870396
  [+] Downloading: https://video.twimg.com/ext_tw_video/.../720x1280.mp4
  [+] Saved: downloads/x/720x1280.mp4 (8.1 MB)
  [✓] Done

All done.
```

### Output
```
downloads/
└── x/
    ├── 1080x1920.mp4
    └── 720x1280.mp4
```

---

## Facebook

### Step 1 — Add URLs to `inputs/facebook.txt`

```
# inputs/facebook.txt
https://www.facebook.com/watch/?v=1234567890
https://www.facebook.com/reel/9876543210
https://www.facebook.com/username/videos/1122334455
```

### Step 2 — Run

**Default (720p):**
```bash
python main.py facebook
```

**Specific resolution:**
```bash
python main.py facebook --video=480
python main.py facebook --video=720
python main.py facebook --video=1080
```

**Sample console output:**
```
Found 3 URL(s). Mode: 720p MP4. Saving to: downloads/facebook

-> Downloading: https://www.facebook.com/watch/?v=1234567890
[youtube] Extracting URL: https://www.facebook.com/watch/?v=1234567890
[download] Destination: downloads/facebook/Video Title.mp4
[download] 100% of 15.32MiB

-> Downloading: https://www.facebook.com/reel/9876543210
[download] Destination: downloads/facebook/Reel Title.mp4
[download] 100% of  8.74MiB

Done.
```

### Output
```
downloads/
└── facebook/
    ├── Video Title.mp4
    └── Reel Title.mp4
```

---

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| `File not found: inputs/youtube.txt` | Input file missing or empty | Add URLs to the file (one per line) |
| `No URLs found in file` | All lines are blank or comments | Add at least one valid URL |
| `ChromeDriver` error (Twitter) | Chrome not installed or outdated | Install/update Chrome; `webdriver-manager` handles the driver |
| `DownloadError: Unsupported URL` | URL format not recognised by yt-dlp | Check the URL is a direct video link, not a profile or playlist page |
| `Invalid resolution '4K'` | Resolution must be a number | Use `--video=2160` instead of `--video=4k` |
| `ERROR: unable to download video` (Facebook) | Video is private or login-gated | Only public Facebook videos are supported |

---

## Quick reference

```bash
# YouTube
python main.py youtube                  # interactive
python main.py youtube --video          # 720p MP4
python main.py youtube --video=1080     # 1080p MP4
python main.py youtube --audio          # MP3

# Twitter / X
python main.py twitter                  # best quality MP4

# Facebook
python main.py facebook                 # 720p MP4
python main.py facebook --video=1080    # 1080p MP4
```
