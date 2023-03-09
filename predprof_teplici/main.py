import asyncio
import threading

from __init__ import create_app 


def app(first, second):
    print(f'{first=}\n\n{second=}')
    app = create_app()

    t = threading.Thread(target=asyncio.run)
    t.start()

    app.run(port=5000)

    print("flask ended")    
