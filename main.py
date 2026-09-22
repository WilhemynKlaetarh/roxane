import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

class RoxaneBot(commands.Bot):

    async def setup_hook(self):

        user = await bot.fetch_user(int(os.environ['ID_WILHEMYN']))

        self.description = f"""
Oui, je t’ai trompé ; j’ai séduit tes eunuques ; je me suis jouée de ta jalousie ; et j’ai su, de ton affreux sérail, faire un lieu de délices et de plaisirs.

Made by {user.display_name}.
"""

        await bot.load_extension('parc')
        await bot.load_extension('rcon')
        await bot.load_extension('reddit')
        await bot.load_extension('anniversaire')

bot = RoxaneBot(
        command_prefix="rox ",
        descruption="",
        intents=intents
)

@bot.listen('on_ready')
async def login() :
    print('-------o-------')
    print(bot.user.name)
    print(bot.user.id)
    print('-------o-------')

bot.run(os.environ['ROXANE_TOKEN'])
