import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

from selenium import webdriver
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



def _get_proxies():
    with open("proxies") as f:
      return list(set([x for x in f.read().split("\n") if x != ""]))

input_file="post_keyword.txt"
output_file="fb_post_result.txt"
use_proxy=False
concurrency=2
result = []
proxies = _get_proxies()
use_proxy = False

executor = ThreadPoolExecutor(concurrency)

def _url_encoding(key):
    result = ""
    for character in key:
      if character == '"':
        result += '%22'
      elif character == ' ':
        result += '%20'
      else:
        result += character
    return result

def scrape(url, *, loop):
  loop.run_in_executor(executor, scraper, url)


def scraper(keyword):
    global result
    proxy = 'http://' + random.choice(proxies) if use_proxy else None
    chrome_options = webdriver.ChromeOptions()
    if use_proxy:
      chrome_options.add_argument('--proxy-server=%s' % proxy)

    chrome = webdriver.Chrome(executable_path="./chromedriver", options=chrome_options)
    chrome.implicitly_wait(2)
    encoded_keyword = _url_encoding(keyword)
    url = "https://www.facebook.com/public?query=" + encoded_keyword + "&type=posts"
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
          result.append({"keyword": keyword, "url": attrs["href"]})
    
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

def last_process():

  print("total FB results found: ", len(result))

  with open(output_file, 'w', encoding="utf-8") as output:
    for line in result:
      output.write(line['keyword'] + '<--->' + line['url'] + '\n')

if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  with open(input_file) as f:
    keywords = [x for x in f.read().split("\n") if x != ""]

  for chunk in tqdm(
    [keywords[x: x + concurrency] for x in range(0, len(keywords), concurrency)]
  ):
      try:
        for keyword in chunk:
          scrape(keyword, loop=loop)
        
      except Exception:
        print("one failed")
  loop.run_in_executor(executor, last_process)
  loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop)))



