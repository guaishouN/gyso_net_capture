import asyncio
import threading

def worker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print(f"Worker thread: {threading.current_thread().name}")
    print(f"Event loop in worker thread: {loop}")

    # 执行协程或其他异步操作
    loop.run_until_complete(my_coroutine())


async def my_coroutine():
    # 协程逻辑
    print("Running coroutine")



async def main():
    # 在另一个线程中执行异步操作
    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()

    # 获取主线程的事件循环
    loop = asyncio.get_running_loop()
    print(f"Main thread: {threading.current_thread().name}")
    print(f"Event loop in main thread: {loop}")


asyncio.run(main())
