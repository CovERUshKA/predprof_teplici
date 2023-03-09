import collector
from asyncio import run


async def start():
    await collector.infinite_collect()


if __name__ == '__main__':
    run(start())