import asyncio
import threading

from __init__ import create_app 


def app(first, second):
    app = create_app()

    # t = threading.Thread(target=asyncio.run)
    # t.start()

    app.run(host='0.0.0.0', port=5000)

    print("flask ended")    
