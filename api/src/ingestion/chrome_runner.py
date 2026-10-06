"""
Standalone Chrome scraper. Run as a subprocess to isolate ChromeDriver
from the API's thread pool (macOS ChromeDriver crashes in background threads).

Reads JSON payload from stdin, writes JSON results to stdout.
All diagnostic prints are redirected to stderr to keep stdout clean for JSON.
"""
import json
import sys


def main():
    payload = json.loads(sys.stdin.read())
    platform = payload["platform"]

    # Redirect stdout → stderr so that any print() calls inside the scrapers
    # (including webdriver_manager progress lines) don't corrupt the JSON output.
    real_stdout = sys.stdout
    sys.stdout = sys.stderr

    items = []
    try:
        if platform == "twitter":
            from ingestion.twitter_web import (
                scrape_twitter_profile,
                scrape_twitter_hashtag,
                scrape_twitter_post,
            )
            mode = payload["mode"]
            source_id = payload["id"]
            limit = payload["limit"]
            if mode == "profile":
                items = scrape_twitter_profile(source_id, limit=limit)
            elif mode == "hashtag":
                items = scrape_twitter_hashtag(source_id, limit=limit)
            else:
                items = scrape_twitter_post(source_id, limit=limit)

        elif platform == "instagram":
            from ingestion.instagram_web import scrape_instagram_one
            items = scrape_instagram_one(
                payload["username"],
                payload["password"],
                payload["mode"],
                payload["id"],
                limit=payload["limit"],
            )
    finally:
        sys.stdout = real_stdout

    json.dump(items, sys.stdout, ensure_ascii=False, default=str)
    sys.stdout.flush()


if __name__ == "__main__":
    main()
