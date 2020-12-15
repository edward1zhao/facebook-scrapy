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

class SearchFaceBookVideoScraper:
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

  def _url_encoding(self, key):
    result = ""
    for character in key:
      if character == '"':
        result += '%22'
      elif character == ' ':
        result += '%20'
      else:
        result += character
    return result
  
  async def process(self, keyword):
    proxy = 'http://' + random.choice(self.proxies) if self.use_proxy else None
    chrome_options = webdriver.ChromeOptions()
    if self.use_proxy:
      chrome_options.add_argument('--proxy-server=%s' % proxy)

    chrome = webdriver.Chrome(executable_path="./chromedriver", options=chrome_options)
    chrome.implicitly_wait(2)
    encoded_keyword = self._url_encoding(keyword)
    url = "https://www.facebook.com/public?query=" + encoded_keyword + "&type=videos"
    print(url)

    chrome.get(url)

    def parse_html(html_source):
      for link in HTMLParser(html_source).css("a"):
        attrs = dd(lambda: None, link.attributes)
        if (
          attrs["href"]
          and "http" in attrs["href"]
          and not "?" in attrs["href"]
        ):
          self.result.append({"keyword": keyword, "url": attrs["href"]})
    
    while True:
      chrome.execute_script("window.scrollTo(0, document.body.scrollHeight);")
      try:
        Div = chrome.find_element_by_xpath("//div[@id='browse_end_of_results_footer']/div/div//div[@class='phm _64f']").text
      except:
        Div = "more result"
        try:
          if chrome.find_element_by_xpath("//div[@id='u_0_c']/div/div/div/div/div/div/div/div/div").text[:29] == "We couldn't find anything for":
            break
        except:
          pass
        
      print(Div)
      if 'End of Results' == Div:
        print("the end")
        break
      else:
        continue
    
    parse_html(chrome.page_source)

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
      try:
        loop.run_until_complete(self.main(chunk))
      except Exception:
        print("one failed")

    print("total FB results found: ", len(self.result))

    with open(self.output_file, 'w', encoding="utf-8") as output:
      for line in self.result:
        output.write(line['keyword'] + '<--->' + line['url'] + '\n')

if __name__ == "__main__":
    SearchFaceBookVideoScraper(
      input_file="video_keyword.txt",
      output_file="fb_video_result.txt",
      use_proxy=False,
      concurrency=2,
    ).run()