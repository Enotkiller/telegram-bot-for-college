import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), "code"))

from Bot import BotСollege

if __name__ == "__main__":
    asyncio.run(BotСollege().start())
