import asyncio


async def task(name, t):
    print(f'Task {name} started {t}')
    await asyncio.sleep(t)  # 模拟耗时操作
    print(f'Task {name} completed{t}')
    yield f'result {name}'

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    print(f'begin sync task')
    asyncio.ensure_future(task("C", 8))
    print(f'done sync task')

    print(f'begin async task')
    tasks = asyncio.gather(task('A', 10), task('B', 5))
    print(f'done task')
    loop.run_until_complete(tasks)
    loop.close()
    print(f'finish process')
