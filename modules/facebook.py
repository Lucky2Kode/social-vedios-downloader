import sys
from pathlib import Path
import yt_dlp

from modules.utils import clear_folder, clear_missed_file, remove_url_from_input

VALID_RESOLUTIONS = (144, 240, 360, 480, 720, 1080, 1440, 2160)


def build_opts(output_dir: Path, resolution: int) -> dict:
    fmt = (
        f"bestvideo[height<={resolution}][ext=mp4]+bestaudio[ext=m4a]"
        f"/best[height<={resolution}][ext=mp4]"
        f"/best[height<={resolution}]"
    )
    return {
        "format": fmt,
        "merge_output_format": "mp4",
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "quiet": False,
        "noplaylist": True,
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
    return missed


def parse_flags(flags: list[str]) -> int:
    for flag in flags:
        if flag.startswith("--video="):
            raw = flag.split("=", 1)[1]
            if raw.isdigit() and int(raw) in VALID_RESOLUTIONS:
                return int(raw)
            res_list = ", ".join(str(r) for r in VALID_RESOLUTIONS)
            print(f"Invalid resolution '{raw}'. Choose from: {res_list}", file=sys.stderr)
            sys.exit(1)
    return 720


def write_missed(missed: list[str], output_dir: Path) -> None:
    if not missed:
        return
    missed_file = output_dir / "facebook_missed.txt"
    with open(missed_file, "w") as f:
        f.write("\n".join(missed) + "\n")
    print(f"\n  [!] {len(missed)} URL(s) failed — saved to: {missed_file}")


def run(urls: list[str], output_dir: Path, input_file: Path, extra_flags: list[str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    print("  [~] Cleaning up before run...")
    clear_folder(output_dir)
    clear_missed_file(output_dir / "facebook_missed.txt")
    print()

    resolution = parse_flags(extra_flags)
    opts = build_opts(output_dir, resolution)
    label = f"{resolution}p MP4"

    print(f"\nFound {len(urls)} URL(s). Mode: {label}. Saving to: {output_dir}")
    missed = download_urls(urls, opts, input_file)
    write_missed(missed, output_dir)
    print("\nDone.")
