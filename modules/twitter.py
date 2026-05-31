import re
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from modules.utils import clear_missed_file, remove_url_from_input

DOWNLOADER_URL = "https://twittervideodownloader.com/en/"
WAIT_TIMEOUT = 20


def build_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def pick_best_download_link(wait: WebDriverWait) -> Optional[str]:
    section = wait.until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="download-section"]'))
    )
    links = section.find_elements(By.TAG_NAME, "a")
    if not links:
        return None

    priority_keywords = ["1080", "hd", "720", "high", "best"]
    for keyword in priority_keywords:
        for link in links:
            label = (link.text + (link.get_attribute("href") or "")).lower()
            if keyword in label:
                return link.get_attribute("href")

    return links[0].get_attribute("href")


def save_file(video_url: str, output_dir: Path) -> None:
    path_part = urlparse(video_url).path
    filename = Path(path_part).name
    filename = re.sub(r"[?&].*", "", filename)
    if not filename.endswith(".mp4"):
        filename += ".mp4"

    stem = Path(filename).stem
    dest = output_dir / filename
    index = 1
    while dest.exists():
        dest = output_dir / f"{stem}_{index}.mp4"
        index += 1
    response = requests.get(video_url, stream=True, timeout=60)
    response.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            f.write(chunk)
    size_mb = dest.stat().st_size / (1024 * 1024)
    print(f"  [+] Saved: {dest} ({size_mb:.1f} MB)")


def download_url(driver: webdriver.Chrome, tweet_url: str, output_dir: Path) -> bool:
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    try:
        driver.get(DOWNLOADER_URL)

        url_input = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="tweetURL"]'))
        )
        driver.execute_script("arguments[0].value = arguments[1];", url_input, tweet_url)

        submit_btn = driver.find_element(By.XPATH, '//*[@id="submitBtn"]')
        driver.execute_script("arguments[0].click();", submit_btn)

        download_href = pick_best_download_link(wait)
        if not download_href:
            print(f"  [!] No download links found for: {tweet_url}")
            return False

        print(f"  [+] Downloading: {download_href}")
        save_file(download_href, output_dir)
        return True

    except Exception as exc:
        print(f"  [!] Failed ({tweet_url}): {exc}")
        return False


def write_missed(missed: list[str], output_dir: Path) -> None:
    if not missed:
        return
    missed_file = output_dir / "x_missed.txt"
    with open(missed_file, "w") as f:
        f.write("\n".join(missed) + "\n")
    print(f"\n  [!] {len(missed)} URL(s) failed — saved to: {missed_file}")


def run(urls: list[str], output_dir: Path, input_file: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    clear_missed_file(output_dir / "x_missed.txt")

    print(f"Found {len(urls)} URL(s) to download. Saving to: {output_dir}\n")

    missed: list[str] = []
    driver = build_driver()
    try:
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] Processing: {url}")
            success = download_url(driver, url, output_dir)
            if success:
                remove_url_from_input(url, input_file)
            else:
                missed.append(url)
                remove_url_from_input(url, input_file)
            print(f"  [{'✓' if success else '✗'}] {'Done' if success else 'Skipped'}\n")
            time.sleep(2)
    finally:
        driver.quit()

    write_missed(missed, output_dir)
    print("All done.")
