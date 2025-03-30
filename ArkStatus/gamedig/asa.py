# gamedig/asa.py
import time
import opengsq
import asyncio

class ASAQuery:
    """
    ASAQuery class to query ASA servers using the OpenGSQL API."
    """


    pre_query_required = True
    name = "asa"

    _client_id = "xyza7891muomRmynIIHaJB9COBKkwj6n"
    _client_secret = "PP5UGxysEieNfSrEicaD1N2Bb3TdXuD7xHYcsdUHZ7s"
    _deployment_id = "ad9a8feffb3b4b2ca315546f038c3ae2"
    _grant_type = "client_credentials"
    _external_auth_type = ""
    _external_auth_token = ""
    _access_token = ""

    @staticmethod
    async def pre_query(self):
        ASAQuery._access_token = await opengsq.EOS.get_access_token(
            client_id=self._client_id,
            client_secret=self._client_secret,
            deployment_id=self._deployment_id,
            grant_type=self._grant_type,
            external_auth_type=self._external_auth_type,
            external_auth_token=self._external_auth_token,
        )
    @staticmethod
    async def query(host: str, port: int, timeout: int = 5) -> dict:
        if not ASAQuery._access_token:
            await ASAQuery.pre_query(ASAQuery)

        host, port = str(ASAQuery.kv["host"]), int(str(ASAQuery.kv["port"]))
        eos = opengsq.EOS(
            host, port, ASAQuery._deployment_id, ASAQuery._access_token, timeout
        )
        start = time.time()
        info = await eos.get_info()
        ping = int((time.time() - start) * 1000)

        # Credits: @dkoz https://github.com/DiscordGSM/GameServerMonitor/pull/54/files
        attributes = dict(info.get("attributes", {}))
        settings = dict(info.get("settings", {}))

        result = {
            "name": attributes.get("CUSTOMSERVERNAME_s", ""),
            "map": attributes.get("MAPNAME_s", ""),
            "password": attributes.get("SERVERPASSWORD_b", False),
            "numplayers": info.get("totalPlayers", 0),
            "numbots": 0,
            "maxplayers": settings.get("maxPublicPlayers", 0),
            "players": None,
            "bots": None,
            "connect": f"{host}:{port}",
            "ping": ping,
            "raw": info,
        }

        return result