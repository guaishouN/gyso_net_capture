import asyncio
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template

app = Flask(__name__)
queue = queue.Queue()


@app.route("/", methods=("GET", "POST"))
def index():
    return render_template("data.html")


@app.route('/data')
async def data():
    send_data()
    return "dsjkfl"


def send_data():
    queue.put("data1111")
    queue.put("data22222")


def run_flask():
    print(f"run_flask thread: {threading.current_thread().name} ")
    app.run()


def flask_queue_emit():
    print("flask_queue_emit begin running")
    print(f"flask_queue_emit thread: {threading.current_thread().name} ")
    while True:
        package = queue.get()
        print("flask_queue_emit --- queue data:", str(package))
        # Perform other processing operations
        queue.task_done()
        print("flask_queue_emit #########")


if __name__ == '__main__':
    executor = ThreadPoolExecutor(max_workers=4)
    flask_future = executor.submit(run_flask)
    queue_future = executor.submit(flask_queue_emit)
    try:
        print(f"asyncio thread: {threading.current_thread().name} ")
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        flask_future.cancel()
        queue_future.cancel()
        executor.shutdown(wait=False)
