from asyncio import run
from discord import Intents
from discord.ext.commands import Bot
from dotenv import load_dotenv
from os import getenv, listdir

load_dotenv()
TOKEN: str = str(getenv("SPOTBOT_TOKEN"))

async def main() -> None:
    intents: Intents = Intents.default()
    intents.message_content = True
    bot: Bot = Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready() -> None:
        print("Bot running.")

    async def load_cogs() -> None:
        for fname in listdir("./cogs"):
            if fname.endswith(".py"):
                await bot.load_extension(f"cogs.{fname[:-3]}")

    await bot.start(TOKEN)

if __name__ == "__main__":
    run(main())

