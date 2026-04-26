"""Test TikTok-Api locally — run directly on host machine (not Docker)."""

import asyncio
import os

from TikTokApi import TikTokApi

ms_token = os.environ.get("TIKTOK_MS_TOKEN", None)


async def test_trending() -> None:
    print(f"ms_token: {'set' if ms_token else 'None (Playwright will self-generate)'}")

    async with TikTokApi() as api:
        print("Creating session...")
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            sleep_after=5,
            headless=True,
        )

        print("Fetching trending videos...")
        count = 0
        async for video in api.trending.videos(count=10):
            data = video.as_dict
            music = data.get("music", {})
            print(f"  #{count + 1}: {music.get('title', 'N/A')} - {music.get('authorName', 'N/A')}")
            count += 1

        print(f"\nTotal videos fetched: {count}")


if __name__ == "__main__":
    asyncio.run(test_trending())
