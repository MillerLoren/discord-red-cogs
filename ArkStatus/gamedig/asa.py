# gamedig/asa.py
import asyncio
import struct
import socket

class ASAQuery:
    @staticmethod
    async def query(ip: str, port: int):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, ASAQuery._sync_query, ip, port)

    @staticmethod
    def _sync_query(ip: str, port: int):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(3.0)
            s.sendto(b'\xFF\xFF\xFF\xFF\x54Source Engine Query\x00', (ip, port))
            data, _ = s.recvfrom(4096)

        if not data.startswith(b'\xFF\xFF\xFF\xFF\x49'):
            raise Exception("Invalid response from server")

        offset = 6
        def read_string():
            nonlocal offset
            end = data.index(b'\x00', offset)
            val = data[offset:end].decode('utf-8')
            offset = end + 1
            return val

        server_info = {
            "name": read_string(),
            "map": read_string(),
            "folder": read_string(),
            "game": read_string(),
            "id": struct.unpack_from('<h', data, offset)[0],
            "players": data[offset + 2],
            "maxplayers": data[offset + 3],
            "bots": data[offset + 4],
        }

        return server_info
