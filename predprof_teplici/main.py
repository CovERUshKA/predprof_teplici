import asyncio
import threading

from __init__ import create_app 


if __name__ == '__main__':
    app = create_app()

    # t = threading.Thread(target=asyncio.run)
    # t.start()

    app.run()
