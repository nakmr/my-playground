import time
import random
import asyncio


async def waiter(name):
    for _ in range(4):
        time_to_sleep = random.randint(1, 3) / 4
        # time.sleep(time_to_sleep)
        await asyncio.sleep(time_to_sleep)
        print(f"{name} is waiting for {time_to_sleep}.")


async def main():
    await asyncio.gather(waiter("first"), waiter("second"))


if __name__ == "__main__":
    asyncio.run(main())
