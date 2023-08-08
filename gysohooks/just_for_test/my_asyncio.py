import asyncio
from concurrent.futures import ThreadPoolExecutor

queue = asyncio.Queue()


async def task(name, t):
    print(f'Task {name} started {t}')
    await asyncio.sleep(t)  # 模拟耗时操作
    print(f'Task {name} completed{t}')
    await queue.put("queue&&" + name)


def flask_queue_emit():
    async def process_queue():
        print("flask_queue_emit begin running")
        while True:
            package = await queue.get()
            print("flask_queue_emit  --- queue data", str(package))
            # 进行其他处理操作
            queue.task_done()
            print("flask_queue_emit  #########")

    loop_q = asyncio.new_event_loop()
    asyncio.set_event_loop(loop_q)
    loop_q.run_until_complete(process_queue())
    loop_q.close()


if __name__ == '__main__':
    #executor = ThreadPoolExecutor(max_workers=2)
    # 在线程池中运行 mitmproxy
    #mitmdump_future = executor.submit(flask_queue_emit)

    loop_m = asyncio.get_event_loop()
    print(f'begin sync task1')
    asyncio.ensure_future(task("C", 8))
    print(f'done sync task1')

    print(f'begin async task2')
    tasks = asyncio.gather(task('A', 10), task('B', 5))

    print(f'done add tasks2')
    loop_m.run_until_complete(tasks)
    loop_m.close()
    print(f'finish process')
