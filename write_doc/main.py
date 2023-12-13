import asyncio
from metagpt.logs import logger

from write_doc.TutorialAssistant import TutorialAssistant


async def main():
    msg = "Git 教程"
    role = TutorialAssistant()
    logger.info(msg)
    result = await role.run(msg)
    logger.info(result)


if __name__ == '__main__':
    asyncio.run(main())
