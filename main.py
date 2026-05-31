"""
Usage:
  python main.py facebook  [--video[=<res>]]
  python main.py twitter
  python main.py youtube   [--video[=<res>] | --audio]

Each platform reads its URL list from inputs/<platform>.txt and writes
downloads to downloads/<folder>/.

  facebook  → inputs/facebook.txt  → downloads/facebook/
  twitter   → inputs/twitter.txt   → downloads/x/
  youtube   → inputs/youtube.txt   → downloads/youtube/
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent

PLATFORMS = {
    "facebook": {
        "input_file": BASE_DIR / "inputs" / "facebook.txt",
        "output_dir": BASE_DIR / "downloads" / "facebook",
    },
    "twitter": {
        "input_file": BASE_DIR / "inputs" / "twitter.txt",
        "output_dir": BASE_DIR / "downloads" / "x",
    },
    "youtube": {
        "input_file": BASE_DIR / "inputs" / "youtube.txt",
        "output_dir": BASE_DIR / "downloads" / "youtube",
    },
}


def read_urls(filepath: Path) -> list[str]:
    if not filepath.exists():
        print(f"ERROR: Input file not found: {filepath}", file=sys.stderr)
        print(f"       Create the file and add one URL per line.", file=sys.stderr)
        sys.exit(1)
    lines = filepath.read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1].lower() not in PLATFORMS:
        print("Usage: python main.py <platform> [options]")
        print()
        print("Platforms:")
        print("  facebook   Download Facebook videos   [--video[=<res>]]")
        print("  twitter    Download Twitter/X videos")
        print("  youtube    Download YouTube videos    [--video[=<res>] | --audio]")
        print()
        print("Options (youtube / facebook):")
        print("  --video          Video+Audio at 720p (default)")
        print("  --video=1080     Video+Audio at specified resolution")
        print("  --audio          Audio only as MP3 (youtube only)")
        print()
        print("Valid resolutions: 144, 240, 360, 480, 720, 1080, 1440, 2160")
        sys.exit(1 if len(sys.argv) < 2 else 0)

    platform = sys.argv[1].lower()
    extra_flags = [a.lower() for a in sys.argv[2:]]
    config = PLATFORMS[platform]

    urls = read_urls(config["input_file"])
    if not urls:
        print(f"No URLs found in {config['input_file']}. Add one URL per line and retry.")
        sys.exit(0)

    input_file: Path = config["input_file"]
    output_dir: Path = config["output_dir"]

    if platform == "youtube":
        from modules.youtube import run
        run(urls, output_dir, input_file, extra_flags)

    elif platform == "twitter":
        from modules.twitter import run
        run(urls, output_dir, input_file)

    elif platform == "facebook":
        from modules.facebook import run
        run(urls, output_dir, input_file, extra_flags)


if __name__ == "__main__":
    main()
