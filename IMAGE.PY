#!/usr/bin/env python3
"""
fetch_image.py

Prompt for an image URL, download it using requests, and save it into ./Fetched_Images/.
Handles HTTP errors, non-image responses, filename extraction (or generation), and common network problems.
"""

import os
import re
import sys
import uuid
from datetime import datetime
from urllib.parse import urlparse, unquote
import mimetypes

import requests
from requests.exceptions import RequestException

DEST_DIR = "Fetched_Images"
CHUNK_SIZE = 8192
TIMEOUT = 15  # seconds


def sanitize_filename(name: str) -> str | None:
    if not name:
        return None
    name = unquote(name)
    # remove dangerous chars and control chars
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
    name = name.strip()
    return name or None


def ext_from_content_type(content_type: str | None) -> str | None:
    if not content_type:
        return None
    c = content_type.split(';', 1)[0].strip().lower()
    ext = mimetypes.guess_extension(c)
    # normalize some odd returned extensions
    if ext == ".jpe":
        ext = ".jpg"
    return ext


def choose_filename(url: str, response: requests.Response | None) -> str:
    # Prefer the final URL after redirects (response.url). Fallback to provided url.
    final_url = (response.url if response is not None else url) if url else url
    parsed = urlparse(final_url)
    basename = os.path.basename(parsed.path)
    basename = sanitize_filename(basename)

    content_type = response.headers.get("Content-Type") if response is not None else None
    ext = ext_from_content_type(content_type) or ""

    if basename:
        # if basename already has an extension, respect it
        name, current_ext = os.path.splitext(basename)
        if current_ext:
            return basename
        else:
            return f"{basename}{ext}"
    # no usable basename -> generate one with timestamp + uuid
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_id = uuid.uuid4().hex[:8]
    return f"image_{timestamp}_{short_id}{ext or '.img'}"


def download_image(url: str) -> tuple[bool, str]:
    os.makedirs(DEST_DIR, exist_ok=True)

    parsed = urlparse(url)
    if not parsed.scheme:
        # try to be user friendly: assume http if user omitted scheme
        url = "http://" + url

    try:
        with requests.get(url, stream=True, timeout=TIMEOUT) as resp:
            try:
                resp.raise_for_status()
            except requests.HTTPError as e:
                return False, f"HTTP error: {e} (status code {resp.status_code})"

            content_type = (resp.headers.get("Content-Type") or "").lower()
            if not content_type.startswith("image/"):
                return False, f"URL returned Content-Type '{content_type}', which is not an image."

            filename = choose_filename(url, resp)
            filepath = os.path.join(DEST_DIR, filename)

            # avoid overwriting existing file by adding a small counter if needed
            base, ext = os.path.splitext(filepath)
            counter = 1
            while os.path.exists(filepath):
                filepath = f"{base}_{counter}{ext}"
                counter += 1

            # write binary in chunks
            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(CHUNK_SIZE):
                    if chunk:  # filter keep-alive chunks
                        f.write(chunk)

            return True, filepath

    except RequestException as e:
        return False, f"Network error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def main():
    try:
        url = input("Enter image URL: ").strip()
        if not url:
            print("No URL provided — exiting.")
            sys.exit(1)

        ok, msg = download_image(url)
        if ok:
            print(f"Success — image saved to: {msg}")
        else:
            print(f"Failed to download image: {msg}")

    except KeyboardInterrupt:
        print("\nCancelled by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()
