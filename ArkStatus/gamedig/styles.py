# gamedig/styles.py
import discord

def default_style(data: dict) -> discord.Embed:
    name = data.get("name", "Unknown Server")
    map_ = data.get("map", "Unknown Map")
    players = data.get("players", 0)
    maxplayers = data.get("maxplayers", 0)
    folder = data.get("folder", "Unknown")
    game = data.get("game", "Game")

    embed = discord.Embed(title=name, color=discord.Color.blue())
    embed.add_field(name="Game", value=game, inline=True)
    embed.add_field(name="Map", value=map_, inline=True)
    embed.add_field(name="Players", value=f"{players}/{maxplayers}", inline=True)
    embed.set_footer(text=f"Engine: {folder}")

    return embed
