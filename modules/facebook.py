import sys
from pathlib import Path
import yt_dlp

from modules.utils import clear_missed_file, remove_url_from_input

VALID_RESOLUTIONS = (144, 240, 360, 480, 720, 1080, 1440, 2160)
VALID_BROWSERS = ("safari", "chrome", "firefox", "edge", "brave", "chromium")


def build_opts(output_dir: Path, resolution: int, browser: str) -> dict:
    # Facebook reels are portrait (e.g. 720x900), so height > width.
    # Filter by height OR width so portrait videos aren't skipped.
    fmt = (
        f"bestvideo[height<={resolution}][ext=mp4]+bestaudio[ext=m4a]"
        f"/bestvideo[width<={resolution}][ext=mp4]+bestaudio[ext=m4a]"
        f"/bestvideo[ext=mp4]+bestaudio[ext=m4a]"
        f"/best[height<={resolution}][ext=mp4]"
        f"/best[width<={resolution}][ext=mp4]"
        f"/best[ext=mp4]"
        f"/best"
    )
    return {
        "format": fmt,
        "merge_output_format": "mp4",
        "outtmpl": str(output_dir / "%(title).80B [%(id)s].%(ext)s"),
        "quiet": False,
        "noplaylist": True,
        # Use browser cookies so Facebook doesn't treat yt-dlp as a bot.
        "cookiesfrombrowser": (browser,),
        "socket_timeout": 30,
        "retries": 5,
        "fragment_retries": 5,
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
                err = str(e)
                if "Operation not permitted" in err and "Cookies" in err:
                    print(
                        "   [!] Cannot read browser cookies (macOS permission denied).\n"
                        "       Fix: System Settings → Privacy & Security → Full Disk Access → add Terminal.\n"
                        "       Or rerun with --browser=chrome if you use Chrome.\n"
                        "       Retrying without cookies...",
                        file=sys.stderr,
                    )
                    no_cookie_opts = {k: v for k, v in opts.items() if k != "cookiesfrombrowser"}
                    try:
                        with yt_dlp.YoutubeDL(no_cookie_opts) as ydl2:
                            ydl2.download([url])
                        remove_url_from_input(url, input_file)
                    except yt_dlp.utils.DownloadError as e2:
                        print(f"   ERROR (no-cookie retry): {e2}", file=sys.stderr)
                        missed.append(url)
                        remove_url_from_input(url, input_file)
                else:
                    print(f"   ERROR: {e}", file=sys.stderr)
                    missed.append(url)
                    remove_url_from_input(url, input_file)
    return missed


def parse_flags(flags: list[str]) -> tuple[int, str]:
    resolution = 720
    browser = "chrome"
    for flag in flags:
        if flag.startswith("--video="):
            raw = flag.split("=", 1)[1]
            if raw.isdigit() and int(raw) in VALID_RESOLUTIONS:
                resolution = int(raw)
            else:
                res_list = ", ".join(str(r) for r in VALID_RESOLUTIONS)
                print(f"Invalid resolution '{raw}'. Choose from: {res_list}", file=sys.stderr)
                sys.exit(1)
        elif flag.startswith("--browser="):
            raw = flag.split("=", 1)[1]
            if raw in VALID_BROWSERS:
                browser = raw
            else:
                b_list = ", ".join(VALID_BROWSERS)
                print(f"Invalid browser '{raw}'. Choose from: {b_list}", file=sys.stderr)
                sys.exit(1)
    return resolution, browser


def write_missed(missed: list[str], output_dir: Path) -> None:
    if not missed:
        return
    missed_file = output_dir / "facebook_missed.txt"
    with open(missed_file, "w") as f:
        f.write("\n".join(missed) + "\n")
    print(f"\n  [!] {len(missed)} URL(s) failed — saved to: {missed_file}")


def run(urls: list[str], output_dir: Path, input_file: Path, extra_flags: list[str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    clear_missed_file(output_dir / "facebook_missed.txt")

    resolution, browser = parse_flags(extra_flags)
    opts = build_opts(output_dir, resolution, browser)
    label = f"{resolution}p MP4 (cookies from {browser})"

    print(f"\nFound {len(urls)} URL(s). Mode: {label}. Saving to: {output_dir}")
    missed = download_urls(urls, opts, input_file)
    write_missed(missed, output_dir)
    print("\nDone.")
