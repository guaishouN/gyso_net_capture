import asyncio
from concurrent.futures import ThreadPoolExecutor


async def producer(queue):
    for i in range(5):
        await asyncio.sleep(1)  # Simulate some async operation
        item = f"Item {i}"
        await queue.put(item)
        print(f"Producer: Put {item} into the queue")

    # Signal the consumer that no more items will be produced
    await queue.put(None)
    print("Producer: Done producing items")


async def consumer(queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"Consumer: Got {item} from the queue")
        queue.task_done()

    print("Consumer: Done consuming items")


async def main():
    queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor()

    # Start the producer in a separate thread
    await loop.run_in_executor(executor, producer, queue)

    # Start the consumer in the current thread
    await consumer(queue)

    # Wait for all tasks in the queue to be done
    await queue.join()


if __name__ == "__main__":
    asyncio.run(main())
