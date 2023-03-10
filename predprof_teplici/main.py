import asyncio
import threading

from __init__ import create_app 


def app(first, second):
    print(f'\n\n\nstart\n\n\n')
    print(f'{first=}\n\n{second=}')
    app = create_app()

    # t = threading.Thread(target=asyncio.run)
    # t.start()

    app.run(host='0.0.0.0', port=4444)

    print("flask ended")    
