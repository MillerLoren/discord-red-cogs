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
        self.config.register_global(servers={}, interval=5, channel=None, messages={})
        self.status_loop.start()

    def cog_unload(self):
        self.status_loop.cancel()

    @tasks.loop(minutes=5)
    async def status_loop(self):
        interval = await self.config.interval()
        self.status_loop.change_interval(minutes=interval)

        servers = await self.config.servers()
        cached_servers = dict(servers)
        channel_id = await self.config.channel()
        message_ids = await self.config.messages()

        if not channel_id:
            return

        channel = self.bot.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel) or not channel.permissions_for(channel.guild.me).send_messages:
            return

        for key, data in cached_servers.items():
            ip, port = data["ip"], data["port"]
            try:
                result = await ASAQuery.query(ip, port)
                embed = default_style(result)

                msg_id = message_ids.get(key)
                if msg_id:
                    try:
                        msg = await channel.fetch_message(msg_id)
                        await msg.edit(embed=embed)
                        continue
                    except discord.NotFound:
                        pass  # Message was deleted

                new_msg = await channel.send(embed=embed)
                message_ids[key] = new_msg.id
            except Exception as e:
                print(f"Failed to query {ip}:{port} - {e}")

        await self.config.messages.set(message_ids)

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
        message_ids = await self.config.messages()
        if name in servers:
            del servers[name]
            if name in message_ids:
                del message_ids[name]
            await self.config.servers.set(servers)
            await self.config.messages.set(message_ids)
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

    @arkstatus.command()
    async def setchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel for status messages."""
        await self.config.channel().set(channel.id)
        await ctx.send(f"Status messages will now be sent to {channel.mention}.")
