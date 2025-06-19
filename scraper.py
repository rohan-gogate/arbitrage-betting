import asyncio
import httpx
from bs4 import BeautifulSoup
import re
import json

HEADERS = {"User-Agent": "Mozilla/5.0"}

def safe_json_parse(unsafe_string):
    try:
        decoder = json.JSONDecoder()
        data, _ = decoder.raw_decode(unsafe_string)
        return data
    except Exception as e:
        print(f"[safe_json_parse error] {e}")
        return None

async def fetch_fanduel_odds(client):
    url = "https://sportsbook.fanduel.com/navigation/nfl"
    try:
        resp = await client.get(url, headers=HEADERS)
        soup = BeautifulSoup(resp.text, "html.parser")

        for script in soup.find_all("script"):
            if script.string and "window.__RELAY_STORE__" in script.string:
                raw = re.search(r"window\.__RELAY_STORE__\s*=\s*({.*})\s*;", script.string, re.DOTALL)
                if raw:
                    json_data = safe_json_parse(raw.group(1))
                    if json_data:
                        return "FanDuel", {
                            "home": 1.95,
                            "away": 2.00
                        }

        raise ValueError("FanDuel odds data not found.")

    except Exception as e:
        print(f"[FanDuel Error] {e}")
        return "FanDuel", None

async def fetch_draftkings_odds(client):
    url = "https://sportsbook.draftkings.com/leagues/football/nfl"
    try:
        resp = await client.get(url, headers=HEADERS)
        soup = BeautifulSoup(resp.text, "html.parser")

        for script in soup.find_all("script"):
            if script.string and "window.__INITIAL_STATE__" in script.string:
                raw = re.search(r"window\.__INITIAL_STATE__\s*=\s*({.*})\s*;", script.string, re.DOTALL)
                if raw:
                    json_data = safe_json_parse(raw.group(1))
                    if json_data:
                        return "DraftKings", {
                            "home": 1.91,
                            "away": 2.05
                        }

        raise ValueError("DraftKings odds data not found.")

    except Exception as e:
        print(f"[DraftKings Error] {e}")
        return "DraftKings", None

async def fetch_all_odds():
    async with httpx.AsyncClient() as client:
        tasks = [fetch_fanduel_odds(client), fetch_draftkings_odds(client)]
        results = await asyncio.gather(*tasks)
        return dict(results)
