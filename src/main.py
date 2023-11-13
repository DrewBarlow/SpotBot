from discord import Client, Intents
from dotenv import load_dotenv
from logging import FileHandler
from os import getenv

load_dotenv()
TOKEN: str = str(getenv("SPOTBOT_TOKEN"))

def main() -> None:
    intents: Intents = Intents.default()
    intents.message_content = True
    client: Client = Client(intents=intents)

    handler: FileHandler = FileHandler(filename="SpotBot.log", encoding="utf-8", mode='a')

    @client.event
    async def on_ready() -> None:
        print("Bot running.")

    client.run(TOKEN, log_handler=handler)

if __name__ == "__main__":
    main() 

