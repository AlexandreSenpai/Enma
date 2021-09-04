import asyncio
import random
import sys
import os
import time

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from NHentai import NHentai
from NHentai import NHentaiAsync

def test_if_returned_doujin_is_in_cache():
  s = time.time()
  NHentai().get_doujin('320165')
  reference_time_took = time.time() - s

  times = list()

  for _ in range(5):
    s = time.time()
    NHentai().get_doujin('320165')
    times.append(time.time() - s)

  s = time.time()
  NHentai().get_doujin('320164')
  not_cached_time_took = time.time() - s

  for _ in range(5):
    s = time.time()
    NHentai().get_doujin('320164')
    times.append(time.time() - s)

  NHentai().get_doujin('320165')


  assert False not in [reference_time_took > execution_time and not_cached_time_took > execution_time for execution_time in times]

def test_if_cache_max_len_is_working():
  s = time.time()
  NHentai().get_pages(page=1)
  final_first_page = time.time() - s
  s = time.time()
  NHentai().get_pages(1)
  final_first_page_cached = time.time() - s
  NHentai().get_pages(page=2)
  NHentai().get_pages(3)
  NHentai().get_pages(4)
  NHentai().get_pages(5)
  s = time.time()
  NHentai().get_pages(6)
  NHentai().get_pages(1)
  final_second_fetch_of_first_page = time.time() - s

  assert final_first_page > final_first_page_cached and final_second_fetch_of_first_page > final_first_page_cached

@pytest.mark.asyncio
async def test_async_caching_system():
  async def fetch_sleeping(id):
    await asyncio.sleep(random.randint(0, 10))
    return await NHentaiAsync().get_doujin(id)

  dummy = await NHentaiAsync().get_doujin('320164')

  tasks = [fetch_sleeping('320164') for _ in range(5)]

  res = await asyncio.gather(*tasks)

  assert len(res) == 5