import asyncio

from metagpt.schema import Message
from metagpt.subscription import SubscriptionRunner

from oss.GithubTrendingCronTrigger import GithubTrendingCronTrigger, github_trending_cron_trigger
from oss.OssWatcher import OssWatcher
from oss.WxPusherClient import WxPusherClient


async def wxpusher_callback(msg: Message):
    client = WxPusherClient()
    await client.send_message(msg.content, content_type=3)


# callback
async def discord_callback(msg: Message):
    pass
    # intents = discord.Intents.default()
    # intents.message_content = True
    # client = discord.Client(intents=intents, proxy=CONFIG.global_proxy)
    # token = os.environ["DISCORD_TOKEN"]
    # channel_id = int(os.environ["DISCORD_CHANNEL_ID"])
    # async with client:
    #     await client.login(token)
    #     channel = await client.fetch_channel(channel_id)
    #     lines = []
    #     for i in msg.content.splitlines():
    #         if i.startswith(("# ", "## ", "### ")):
    #             if lines:
    #                 await channel.send("\n".join(lines))
    #                 lines = []
    #         lines.append(i)
    #
    #     if lines:
    #         await channel.send("\n".join(lines))


# 运行入口，
async def main(spec: str = "* * * * *", discord: bool = False, wxpusher: bool = True):
    callbacks = []
    if discord:
        callbacks.append(discord_callback)

    if wxpusher:
        callbacks.append(wxpusher_callback)

    if not callbacks:
        async def _print(msg: Message):
            print(msg.content)

        callbacks.append(_print)

    async def callback(msg):
        await asyncio.gather(*(call(msg) for call in callbacks))

    runner = SubscriptionRunner()
    await runner.subscribe(OssWatcher(),
                           # 这里的迭代器暂时用类实现
                           GithubTrendingCronTrigger(spec),
                           callback)
    await runner.run()


if __name__ == "__main__":
    import fire

    fire.Fire(main)
