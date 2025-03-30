# gamedig/protocol.py
import abc

class Protocol(abc.ABC):
    @abc.abstractmethod
    async def query(cls, ip: str, port: int):
        pass
