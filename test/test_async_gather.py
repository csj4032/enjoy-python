import asyncio
import threading

import pytest

from async_gather import async_gather


@pytest.mark.asyncio
def test_async_gather():
    asyncio.run(async_gather())
