import asyncio
from scraper import fetch_all_odds

if __name__ == "__main__":
    odds = asyncio.run(fetch_all_odds())
    print(odds)