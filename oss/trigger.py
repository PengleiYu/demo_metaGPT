import asyncio

from datetime import datetime, timedelta
from metagpt.schema import Message


async def oss_trigger(hour: int, minute: int, second: int = 0, url: str = "https://github.com/trending"):
    while True:
        now = datetime.now()
        next_time = datetime(now.year, now.month, now.day, hour, minute, second)
        if next_time < now:
            next_time = next_time + timedelta(1)
        wait = next_time - now
        print(wait.total_seconds())
        await asyncio.sleep(wait.total_seconds())
        yield Message(url)
