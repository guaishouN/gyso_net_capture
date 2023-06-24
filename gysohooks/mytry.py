import asyncio
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template
from flask_cors import CORS, cross_origin

app = Flask(__name__)
queue = asyncio.Queue()


@app.route("/", methods=("GET", "POST"))
@cross_origin()  # Allow cross-origin access to this route
def index():
    return render_template("data.html")


@app.route('/data')
async def data():
    await queue.put("data1111")
    await queue.put("data22222")
    return "dsjkfl"


def run_flask():
    app.run()


async def flask_queue_emit():
    print("flask_queue_emit begin running")
    while True:
        package = await queue.get()
        print("flask_queue_emit --- queue data:", str(package))
        # Perform other processing operations
        queue.task_done()
        print("flask_queue_emit #########")


if __name__ == '__main__':
    executor = ThreadPoolExecutor(max_workers=4)
    flask_future = executor.submit(run_flask)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(flask_queue_emit())
    except KeyboardInterrupt:
        pass
    finally:
        flask_future.cancel()
        executor.shutdown(wait=False)
