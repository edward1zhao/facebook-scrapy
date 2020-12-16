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


input_file = "keyword.txt"
output_file = "fb_search_result.txt"
use_proxy = False
concurrency = 2
result = {}
proxies = _get_proxies()
use_proxy = False

executor = ThreadPoolExecutor(concurrency)


def scrape(url, *, loop):
    loop.run_in_executor(executor, scraper, url)


def scraper(keyword):
    global result
    proxy = 'http://' + random.choice(proxies) if use_proxy else None
    chrome_options = webdriver.ChromeOptions()
    if use_proxy:
        chrome_options.add_argument('--proxy-server=%s' % proxy)

    chrome = webdriver.Chrome(
        executable_path="./chromedriver", options=chrome_options)
    chrome.implicitly_wait(2)
    url = "https://www.social-searcher.com/facebook-search" + "/?q=" + keyword
    chrome.get(url)

    chrome.execute_script("window.scrollTo(0, 200)")

    actions = ActionChains(chrome)
    print(chrome.find_element_by_css_selector(
        'div.gsc-selected-option-container.gsc-inline-block div.gsc-selected-option').text)
    select_element = chrome.find_element_by_css_selector(
        'div.gsc-selected-option-container.gsc-inline-block')

    actions.click(select_element)
    actions.perform()

    select_element_in = chrome.find_element_by_css_selector(
        'div.gsc-option-menu :nth-child(2) div.gsc-option')
    select_element_in.click()

    print(chrome.find_element_by_css_selector(
        'div.gsc-selected-option-container.gsc-inline-block div.gsc-selected-option').text)
    html = chrome.page_source

    result_set = set()

    def parse_html(html_source):
        for link in HTMLParser(html_source).css("a"):
            attrs = dd(lambda: None, link.attributes)
            if (
                attrs["href"]
                and "http" in attrs["href"]
                and not "?" in attrs["href"]
            ):
                result_set.add(attrs["href"])

    def set_page_number(number):
        chrome.execute_script(
            "window.scrollTo(0, document.body.scrollHeight - 2000)")
        element = chrome.find_element_by_xpath(
            "//div[@aria-label='Page " + str(number) + "']")
        element.click()
        return chrome.page_source

    result.update({keyword: result_set})

    for i in range(10):
        if i != 0:
            parse_html(set_page_number(i + 1))
        else:
            parse_html(html)

    chrome.close()


def last_process():

    len_result = sum([len(item) for item in result.values()])
    print("total FB results found: ", len_result)

    with open(output_file, 'w') as out_file:
        for key in result:
            for item in result[key]:
                out_file.write(key + '<--->' + item + '\n')


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    with open(input_file) as f:
        keywords = [x for x in f.read().split("\n") if x != ""]

    for chunk in tqdm(
        [keywords[x: x + concurrency]
            for x in range(0, len(keywords), concurrency)]
    ):
        try:
            for keyword in chunk:
                scrape(keyword, loop=loop)

        except Exception:
            print("one failed")

    loop.run_in_executor(executor, last_process)
    loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop)))
