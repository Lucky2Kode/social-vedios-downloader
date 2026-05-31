import sys
from pathlib import Path
import yt_dlp

from modules.utils import clear_missed_file, remove_url_from_input

VALID_RESOLUTIONS = (144, 240, 360, 480, 720, 1080, 1440, 2160)


def build_video_opts(output_dir: Path, resolution: int) -> dict:
    fmt = (
        f"bestvideo[height<={resolution}][ext=mp4]+bestaudio[ext=m4a]"
        f"/best[height<={resolution}][ext=mp4]"
        f"/best[height<={resolution}]"
    )
    return {
        "format": fmt,
        "merge_output_format": "mp4",
        "outtmpl": str(output_dir / "%(title).80B [%(id)s].%(ext)s"),
        "quiet": False,
        "noplaylist": True,
    }


def build_audio_opts(output_dir: Path) -> dict:
    return {
        "format": "bestaudio/best",
        "outtmpl": str(output_dir / "%(title).80B [%(id)s].%(ext)s"),
        "quiet": False,
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }


def download_urls(urls: list[str], opts: dict, input_file: Path) -> list[str]:
    missed: list[str] = []
    with yt_dlp.YoutubeDL(opts) as ydl:
        for url in urls:
            url = url.strip()
            if not url or url.startswith("#"):
                continue
            print(f"\n-> Downloading: {url}")
            try:
                ydl.download([url])
                remove_url_from_input(url, input_file)
            except yt_dlp.utils.DownloadError as e:
                print(f"   ERROR: {e}", file=sys.stderr)
                missed.append(url)
                remove_url_from_input(url, input_file)
    return missed


def parse_flags(flags: list[str]) -> tuple[str, int]:
    if "--audio" in flags:
        return "audio", 0

    for flag in flags:
        if flag.startswith("--video="):
            raw = flag.split("=", 1)[1]
            if raw.isdigit() and int(raw) in VALID_RESOLUTIONS:
                return "video", int(raw)
            res_list = ", ".join(str(r) for r in VALID_RESOLUTIONS)
            print(f"Invalid resolution '{raw}'. Choose from: {res_list}", file=sys.stderr)
            sys.exit(1)

    if "--video" in flags:
        return "video", 720

    return "", 0


def prompt_mode() -> tuple[str, int]:
    print("\nHow would you like to download?")
    print("  1) Video + Audio (MP4)")
    print("  2) Audio only (MP3)")
    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice in ("1", "2"):
            break
        print("Please enter 1 or 2.")

    if choice == "2":
        return "audio", 0

    res_list = ", ".join(str(r) for r in VALID_RESOLUTIONS)
    print(f"\nAvailable resolutions: {res_list}")
    while True:
        raw = input("Enter resolution (e.g. 720): ").strip()
        if raw.isdigit() and int(raw) in VALID_RESOLUTIONS:
            return "video", int(raw)
        print(f"Invalid resolution. Choose from: {res_list}")


def write_missed(missed: list[str], output_dir: Path) -> None:
    if not missed:
        return
    missed_file = output_dir / "youtube_missed.txt"
    with open(missed_file, "w") as f:
        f.write("\n".join(missed) + "\n")
    print(f"\n  [!] {len(missed)} URL(s) failed — saved to: {missed_file}")


def run(urls: list[str], output_dir: Path, input_file: Path, extra_flags: list[str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    clear_missed_file(output_dir / "youtube_missed.txt")

    mode, resolution = parse_flags(extra_flags)
    if not mode:
        mode, resolution = prompt_mode()

    if mode == "audio":
        opts = build_audio_opts(output_dir)
        label = "MP3 (audio only)"
    else:
        opts = build_video_opts(output_dir, resolution)
        label = f"{resolution}p MP4 (video+audio)"

    print(f"\nFound {len(urls)} URL(s). Mode: {label}. Saving to: {output_dir}")
    missed = download_urls(urls, opts, input_file)
    write_missed(missed, output_dir)
    print("\nDone.")
