from asyncio import run
from discord import Intents
from discord.ext.commands import Bot
from dotenv import load_dotenv
from os import getenv

load_dotenv()
TOKEN: str = str(getenv("SPOTBOT_TOKEN"))

async def load_cogs(bot: Bot) -> None:
    await bot.load_extension("spotbot")
    return

async def main() -> None:
    intents: Intents = Intents.default()
    intents.message_content = True
    bot: Bot = Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready() -> None:
        print("Bot running.")
        await bot.tree.sync()

    await load_cogs(bot)
    await bot.start(TOKEN)

if __name__ == "__main__":
    run(main())

