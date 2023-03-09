import collector
from asyncio import run


def start():
    run(collector.infinite_collect())