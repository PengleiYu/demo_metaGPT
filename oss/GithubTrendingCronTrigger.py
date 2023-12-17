import asyncio
from datetime import datetime
from typing import Optional

from aiocron import crontab
from metagpt.schema import Message
from pytz import BaseTzInfo


class GithubTrendingCronTrigger():

    def __init__(self, spec: str, tz: Optional[BaseTzInfo] = None, url: str = "https://github.com/trending") -> None:
        self.crontab = crontab(spec, tz=tz)
        self.url = url

    def __aiter__(self):
        return self

    async def __anext__(self):
        print("before wait")
        await self.crontab.next()
        print("after wait")
        return Message(self.url)


async def github_trending_cron_trigger(spec: str, tz: Optional[BaseTzInfo] = None,
                                       url: str = "https://github.com/trending"):
    print('github_trending_cron_trigger')
    c = crontab(spec, tz=tz)
    await c.next()
    print('crontab.next()')
    yield Message(url)



class IterCrontab:

    def __init__(self) -> None:
        super().__init__()
        spec: str = "* * * * *"
        self.crontab = crontab(spec)

    def __aiter__(self):
        return self

    async def __anext__(self):
        print('before next')
        await self.crontab.next()
        print('after next')
        return 0


async def main2():
    c = IterCrontab()
    async for i in c:
        print(i)


async def main():
    async for i in iter_crontab():
        print(i)


async def iter_crontab():
    spec: str = "* * * * *"
    print('github_trending_cron_trigger')
    c = crontab(spec, tz=None)
    await c.next()
    print('crontab.next()')
    # 仅获取当前的时间
    current_time_only = datetime.now().time()
    # 打印当前时间，默认格式为 HH:MM:SS.ffffff
    yield current_time_only


if __name__ == '__main__':
    asyncio.run(main())
