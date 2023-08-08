import asyncio

async def fetch_data(url):
    print("Start fetching data")
    # 模拟网络请求的延迟
    await asyncio.sleep(2)
    print("Data fetched")
    return "Fetched data"

async def process_data(data):
    print("Start processing data")
    await asyncio.sleep(1)
    print("Data processed:", data.upper())

async def main():
    data = await fetch_data("https://example.com")
    await process_data(data)

asyncio.run(main())
