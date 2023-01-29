import asyncio
import threading

from predprof_teplici import create_app, collector

if __name__ == "__main__":
    app = create_app()

    t = threading.Thread(target=asyncio.run, args=(collector.infinite_collect(),))
    t.start()

    app.run(debug=False,  port=80, host="0.0.0.0")

    print("flask ended")

    collector.end_working = True
