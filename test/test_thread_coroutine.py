import asyncio
import datetime
import logging
import threading
import time

import pytest

from async_gather import async_gather

foo_event_loop = asyncio.new_event_loop()
boo_event_loop = asyncio.new_event_loop()


def run_forever(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


async def foo_task():
    current_thread = threading.current_thread()
    logging.info(f"foo_task current thread: {current_thread.name}, id: {current_thread.ident}")
    await asyncio.sleep(1)


async def boo_task():
    start = time.time()
    logging.info(f"start: {start}")
    current_thread = threading.current_thread()
    logging.info(f"boo_task current thread: {current_thread.name}, id: {current_thread.ident}")
    await boo_sub1_task()
    # await boo_sub2_task()
    # await boo_sub3_task()

    boo_sub_event_loop = asyncio.new_event_loop()
    boo_sub_thread = threading.Thread(target=run_forever, args=(boo_sub_event_loop,))
    boo_sub_thread.start()

    future2 = asyncio.run_coroutine_threadsafe(boo_sub2_task(), boo_sub_event_loop)
    future3 = asyncio.run_coroutine_threadsafe(boo_sub3_task(), boo_sub_event_loop)

    logging.info(f"boo_group2_sub1_task result: {future2.result()}")
    logging.info(f"boo_group2_sub1_task result: {future3.result()}")

    boo_sub_event_loop.call_soon_threadsafe(boo_sub_event_loop.stop)
    boo_sub_thread.join()
    boo_sub_event_loop.close()

    end = time.time()
    logging.info(f"start: {start}, end: {end}, elapsed: {end - start}")
    await asyncio.sleep(1)


async def boo_sub1_task():
    current_thread = threading.current_thread()
    logging.info(f"boo_sub1_task current thread: {current_thread.name}, id: {current_thread.ident}")
    await asyncio.sleep(1)


async def boo_sub2_task():
    current_thread = threading.current_thread()
    logging.info(f"boo_sub2_task current thread: {current_thread.name}, id: {current_thread.ident}")
    await asyncio.sleep(2)


async def boo_sub3_task():
    current_thread = threading.current_thread()
    logging.info(f"boo_sub3_task current thread: {current_thread.name}, id: {current_thread.ident}")
    await asyncio.sleep(2)


@pytest.mark.asyncio
def test_thread_coroutine():
    try:
        foo_thread = threading.Thread(target=run_forever, args=(foo_event_loop,))
        boo_thread = threading.Thread(target=run_forever, args=(boo_event_loop,))

        foo_thread.start()
        boo_thread.start()

        future_foo = asyncio.run_coroutine_threadsafe(foo_task(), foo_event_loop)
        future_boo = asyncio.run_coroutine_threadsafe(boo_task(), boo_event_loop)

        # 작업 완료 대기
        future_foo.result()
        future_boo.result()

        foo_thread.join()
        boo_thread.join()

    finally:
        foo_event_loop.call_soon_threadsafe(foo_event_loop.stop)
        boo_event_loop.call_soon_threadsafe(boo_event_loop.stop)
        foo_event_loop.close()
        boo_event_loop.close()

    assert True
