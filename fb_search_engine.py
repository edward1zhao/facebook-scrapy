import json
import time
import random
import aiohttp
import asyncio
import pandas as pd
from collections import defaultdict as dd
from tqdm import tqdm
from fake_useragent import UserAgent
from selectolax.parser import HTMLParser


import threading
from queue import Queue
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class SearchThread(Thread):

  def __init__(self):
    pass

  def run(self):

    pass

class SearchFaceBookScraper:
  def __init__(self, input_file, output_file, use_proxy, concurrency):
    self.input_file = input_file
    self.output_file = output_file
    self.result = {}
    self.exam = []
    self.size = concurrency
    self.proxies = self._get_proxies()
    self.use_proxy = use_proxy

  
  def _get_proxies(self):
    with open("proxies") as f:
      return list(set([x for x in f.read().split("\n") if x != ""]))
  
  async def process(self, keyword):
    proxy = 'http://' + random.choice(self.proxies) if self.use_proxy else None
    chrome_options = webdriver.ChromeOptions()
    if self.use_proxy:
      chrome_options.add_argument('--proxy-server=%s' % proxy)

    chrome = webdriver.Chrome(executable_path="./chromedriver", options=chrome_options)
    chrome.implicitly_wait(2)
    url = "https://www.social-searcher.com/facebook-search" + "/?q=" + keyword
    chrome.get(url)

    chrome.execute_script("window.scrollTo(0, 200)")

    actions = ActionChains(chrome)
    print(chrome.find_element_by_css_selector('div.gsc-selected-option-container.gsc-inline-block div.gsc-selected-option').text)
    select_element = chrome.find_element_by_css_selector('div.gsc-selected-option-container.gsc-inline-block')

    actions.click(select_element)
    actions.perform()

    select_element_in = chrome.find_element_by_css_selector('div.gsc-option-menu :nth-child(2) div.gsc-option')
    select_element_in.click()

    print(chrome.find_element_by_css_selector('div.gsc-selected-option-container.gsc-inline-block div.gsc-selected-option').text)
    html = chrome.page_source

    result = set()
    def parse_html(html_source):
      for link in HTMLParser(html_source).css("a"):
        attrs = dd(lambda: None, link.attributes)
        if (
          attrs["href"]
          and "http" in attrs["href"]
          and not "?" in attrs["href"]
        ):
          result.add(attrs["href"])
          self.exam.append(attrs["href"])
    
    def set_page_number(number):
      chrome.execute_script("window.scrollTo(0, document.body.scrollHeight - 2200)")
      element = chrome.find_element_by_xpath("//div[@aria-label='Page " + str(number) + "']")
      element.click()
      return chrome.page_source

    self.result.update({keyword: result})

    for i in range(10):
      if i != 0:
        parse_html(set_page_number(i + 1))
      else:
        parse_html(html)
    chrome.close()

  async def main(self, keywords):
    print(keywords)
    await asyncio.wait([self.process(item) for item in keywords])

  def run(self):
    loop = asyncio.get_event_loop()

    with open(self.input_file) as input_file:
      keywords = [x for x in input_file.read().split("\n") if x != ""]

    for chunk in tqdm(
      [keywords[x: x + self.size] for x in range(0, len(keywords), self.size)]
    ):
      # try:
        loop.run_until_complete(self.main(chunk))
      # except Exception:
      #   print("one failed")

    len_result = sum([len(item) for item in self.result.values()])
    print("total FB results found: ", len_result)

    with open(self.output_file, 'w') as output_file:
      for key in self.result:
        for item in self.result[key]:
          output_file.write(key + '<---->' + item + '\n')

if __name__ == "__main__":
    SearchFaceBookScraper(
      input_file="keyword.txt",
      output_file="fbsearchresult.txt",
      use_proxy=False,
      concurrency=2,
    ).run()