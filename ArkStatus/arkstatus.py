# arkstatus.py
import discord
from discord.ext import tasks
from redbot.core import commands, Config
import asyncio
from .gamedig.asa import ASAQuery
from .gamedig.styles import default_style

class ArkStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)
        self.config.register_global(servers={}, interval=5)
        self.status_loop.start()

    def cog_unload(self):
        self.status_loop.cancel()

    @tasks.loop(minutes=5)
    async def status_loop(self):
        interval = await self.config.interval()
        self.status_loop.change_interval(minutes=interval)

        servers = await self.config.servers()
        cached_servers = dict(servers)  # Cache server data to avoid multiple reads

        for key, data in cached_servers.items():
            ip, port = data["ip"], data["port"]
            try:
                result = await ASAQuery.query(ip, port)
                embed = default_style(result)
                for channel in self.bot.get_all_channels():
                    if isinstance(channel, discord.TextChannel) and channel.permissions_for(channel.guild.me).send_messages:
                        await channel.send(embed=embed)
                        break  # Send to first eligible channel only
            except Exception as e:
                print(f"Failed to query {ip}:{port} - {e}")

    @commands.group()
    async def arkstatus(self, ctx):
        """Manage ARK server monitoring."""
        pass

    @arkstatus.command()
    async def add(self, ctx, name: str, ip: str, port: int):
        servers = await self.config.servers()
        servers[name] = {"ip": ip, "port": port}
        await self.config.servers.set(servers)
        await ctx.send(f"Added server `{name}` at {ip}:{port}.")

    @arkstatus.command()
    async def remove(self, ctx, name: str):
        servers = await self.config.servers()
        if name in servers:
            del servers[name]
            await self.config.servers.set(servers)
            await ctx.send(f"Removed server `{name}`.")
        else:
            await ctx.send("Server not found.")

    @arkstatus.command()
    async def list(self, ctx):
        servers = await self.config.servers()
        if not servers:
            await ctx.send("No servers are currently being monitored.")
            return

        msg = "**Monitored Servers:**\n"
        for name, info in servers.items():
            msg += f"`{name}` - {info['ip']}:{info['port']}\n"
        await ctx.send(msg)

    @arkstatus.command()
    async def setinterval(self, ctx, minutes: int):
        """Set how often the bot checks servers (in minutes)."""
        if minutes < 1:
            await ctx.send("Interval must be at least 1 minute.")
            return

        await self.config.interval.set(minutes)
        self.status_loop.change_interval(minutes=minutes)
        await ctx.send(f"Polling interval set to {minutes} minute(s).")
