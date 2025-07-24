import asyncio
import logging
from datetime import datetime


async def task0() -> None:
    logging.info(f"작업 0 시작: {datetime.now()}")
    await asyncio.sleep(5)
    logging.info(f"작업 0 완료: {datetime.now()}")


async def task1() -> None:
    logging.info(f"작업 1 시작: {datetime.now()}")
    await asyncio.sleep(2)
    logging.info(f"작업 1 완료: {datetime.now()}")


async def task2() -> None:
    logging.info(f"작업 2 시작: {datetime.now()}")
    await asyncio.sleep(1)
    logging.info(f"작업 2 완료: {datetime.now()}")


async def task3() -> None:
    logging.info(f"작업 3 시작: {datetime.now()}")
    await asyncio.sleep(5)
    logging.info(f"작업 3 완료: {datetime.now()}")


async def task4() -> None:
    logging.info(f"작업 4 시작: {datetime.now()}")
    await asyncio.sleep(1)
    logging.info(f"작업 4 완료: {datetime.now()}")


async def async_gather() -> None:
    await task0()
    await asyncio.gather(task1(), task2(), task3())
    await task4()
