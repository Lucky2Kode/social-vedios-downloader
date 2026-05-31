from pathlib import Path


def clear_folder(folder: Path) -> None:
    removed = 0
    for f in folder.iterdir():
        if f.is_file():
            f.unlink()
            removed += 1
    print(f"  [~] Cleared {removed} file(s) from: {folder}")


def clear_missed_file(missed_file: Path) -> None:
    if missed_file.exists():
        missed_file.unlink()
        print(f"  [~] Cleared previous missed file: {missed_file}")


def remove_url_from_input(url: str, input_file: Path) -> None:
    lines = input_file.read_text(encoding="utf-8").splitlines(keepends=True)
    updated = [l for l in lines if l.strip() != url]
    input_file.write_text("".join(updated), encoding="utf-8")
