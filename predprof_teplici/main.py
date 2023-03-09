import asyncio
import threading

from __init__ import create_app 
import collector


def app(first, second):
    # print(f'{first=}\n\n{second=}')
# if __name__ == '__main__':
    app = create_app()

    t = threading.Thread(target=asyncio.run, args=(collector.infinite_collect(),))
    t.start()

    app.run(port=8081)

    print("flask ended")

    collector.end_working = True
