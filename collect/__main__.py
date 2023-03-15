import collector
from asyncio import run

if __name__ == '__main__':
    run(collector.infinite_collect())
