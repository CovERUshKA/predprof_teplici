import asyncio
import threading

from __init__ import create_app 
import collector.collector


def app(first, second):
    print(f'{first=}\n\n{second=}')
    app = create_app()

    t = threading.Thread(target=asyncio.run, args=(collector.infinite_collect(),))
    t.start()

    app.run(port=5000)

    print("flask ended")

    collector.end_working = True
