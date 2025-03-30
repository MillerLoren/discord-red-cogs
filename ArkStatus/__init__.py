# gamedig/__init__.py
# This file marks the gamedig directory as a Python package.
from .arkstatus import ArkStatus

async def setup(bot):
    await bot.add_cog(ArkStatus(bot))