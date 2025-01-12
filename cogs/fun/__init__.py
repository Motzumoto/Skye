
from core.bot import SkyeBot

from .fun import fun
from .rb import roblx


class Fun(fun, roblx):
    """Fun Cog"""


async def setup(bot: SkyeBot):
    await bot.add_cog(Fun(bot))
