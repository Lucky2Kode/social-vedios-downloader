# SocialDownloaders

A unified Python tool to download videos from multiple social media platforms — Facebook, Twitter/X, and YouTube — each as an independent module driven by a simple text file of URLs.

---

## What it does

| Platform  | Input file             | Downloads to          | Method                              |
|-----------|------------------------|-----------------------|-------------------------------------|
| Facebook  | `inputs/facebook.txt`  | `downloads/facebook/` | yt-dlp                              |
| Twitter/X | `inputs/twitter.txt`   | `downloads/x/`        | Selenium + twittervideodownloader.com |
| YouTube   | `inputs/youtube.txt`   | `downloads/youtube/`  | yt-dlp (video MP4 or audio MP3)     |

You pick which platform to run as a CLI argument. The tool reads the corresponding input file, downloads every URL in it, and saves the files to the platform's downloads folder.

---

## Project structure

```
SocialDownloaders/
├── main.py                   # Entry point
├── modules/
│   ├── facebook.py           # Facebook downloader module
│   ├── twitter.py            # Twitter/X downloader module
│   └── youtube.py            # YouTube downloader module
├── inputs/
│   ├── facebook.txt          # Add Facebook video URLs here
│   ├── twitter.txt           # Add Twitter/X video URLs here
│   └── youtube.txt           # Add YouTube video URLs here
├── downloads/
│   ├── facebook/             # Downloaded Facebook videos
│   ├── x/                    # Downloaded Twitter/X videos
│   └── youtube/              # Downloaded YouTube videos/audio
└── requirements.txt
```

---

## Tech stack

| Component         | Purpose                                           |
|-------------------|---------------------------------------------------|
| **Python 3.11+**  | Core language                                     |
| **yt-dlp**        | Downloads Facebook and YouTube videos             |
| **Selenium**      | Automates Chrome to use twittervideodownloader.com |
| **webdriver-manager** | Auto-installs the correct ChromeDriver        |
| **requests**      | Streams and saves Twitter video files             |
| **FFmpeg**        | Merges video+audio streams (used by yt-dlp)       |

---

## Setup

**1. Create and activate a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Install FFmpeg** (required for YouTube video+audio merging)

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

---

## Usage

### Add URLs to the input file

Open the input file for the platform you want and add one URL per line. Lines starting with `#` are treated as comments and ignored.

**`inputs/youtube.txt`**
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=abc123
```

**`inputs/twitter.txt`**
```
https://x.com/username/status/1234567890
```

**`inputs/facebook.txt`**
```
https://www.facebook.com/watch/?v=1234567890
```

---

### Run the downloader

```bash
python main.py <platform> [options]
```

#### YouTube

```bash
python main.py youtube                  # Interactive prompt (video or audio, choose resolution)
python main.py youtube --video          # Video + Audio, 720p (default)
python main.py youtube --video=1080     # Video + Audio at 1080p
python main.py youtube --audio          # Audio only, saved as MP3
```

Valid resolutions: `144, 240, 360, 480, 720, 1080, 1440, 2160`

#### Twitter / X

```bash
python main.py twitter                  # Opens Chrome, downloads best quality available
```

> Twitter module opens a visible Chrome window and processes each URL through twittervideodownloader.com. Best available quality (up to 1080p/HD) is selected automatically.

#### Facebook

```bash
python main.py facebook                 # Downloads at 720p (default)
python main.py facebook --video=1080    # Downloads at 1080p
```

> Facebook module works with public video URLs. Private or login-gated videos are not supported.

---

## Notes

- **Twitter**: Chrome must be installed. ChromeDriver is managed automatically by `webdriver-manager`.
- **Facebook**: Only public video URLs are supported. For private/saved videos, refer to the dedicated [FB_Saved_Vedios](../FB_Saved_Vedios) project.
- **YouTube**: Playlists are disabled by default (`noplaylist=True`). Pass individual video URLs.
- Downloads resume safely — if a file already exists, yt-dlp skips it automatically.
