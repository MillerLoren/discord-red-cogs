# gamedig/asa.py
from opengsq import Source
import asyncio

class ASAQuery:
    @staticmethod
    async def query(ip: str, port: int) -> dict:
        try:
            source = Source()
            result = await source.info(ip, port)

            server = {
                "name": result.get("name", "Unknown Server"),
                "map": result.get("map", "Unknown"),
                "folder": result.get("folder", "Unknown"),
                "game": result.get("game", "Unknown"),
                "id": result.get("id", 0),
                "players": result.get("players", 0),
                "maxplayers": result.get("max_players", 0),
                "bots": result.get("bots", 0),
            }
            return server

        except Exception as e:
            raise Exception(f"Query failed: {e}")