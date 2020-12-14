import json
import time
import random
import aiohttp
import asyncio
import pandas as pd
from tqdm import tqdm
from fake_useragent import UserAgent
from selectolax.parser import HTMLParser


import threading
from queue import Queue
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class SearchThread(Thread):

  def __init__(self):
    pass

  def run(self):

    pass

class SearchFaceBookScraper:
  def __init__(self, input_file, output_file, use_proxy, concurrency):
    self.input_file = input_file
    self.output_file = output_file
    self.result = []
    self.size = concurrency
    self.proxies = self._get_proxies()
    self.use_proxy = use_proxy

  
  def _get_proxies(self):
    with open("proxies") as f:
      return list(set([x for x in f.read().split("\n") if x != ""]))

  async def process(self, keyword):
    proxy = 'http://' + random.choice(self.proxies) if self.use_proxy else None
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=%s' % proxy)
    chrome = webdriver.Chrome(chrome_options=chrome_options)
    url = "https://www.social-searcher.com/facebook-search" + "/?q=" + keyword
    chrome.get(url)

  async def main(self, keywords):
    pass

  def run(self):
    loop = asyncio.get_event_loop()

    with open(self.input_file) as input_file:
      keywords = [x for x in input_file.read().split("\n") if x != ""]

    for chunk in tqdm(
      [keywords[x: x + self.size] for x in range(0, len(keywords), self.size)]
    ):
      try:
        loop.run_until_complete(self.main(chunk))
      except Exception:
        print("chunk failed")

    print("total FB results found: ", len(self.result))

if __name__ == "__main__":
    SearchFaceBookScraper(
      input_file="keyword.txt",
      output_file="fbsearchresult.txt",
      use_proxy=False,
      concurrency=20,
    ).run()