import asyncio
import concurrent.futures

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


input_file = "post_keyword.txt"
output_file = "fb_post_result.txt"
use_proxy = False
concurrency = 2
result = []
proxies = _get_proxies()


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


def scraper(keyword):
    try:
        global result
        proxy = 'http://' + random.choice(proxies) if use_proxy else None
        driver_options = webdriver.FirefoxOptions()
        if use_proxy:
            driver_options.add_argument('--proxy-server=%s' % proxy)

        driver = webdriver.Firefox(
            executable_path="./geckodriver", options=driver_options)
        driver.implicitly_wait(2)
        encoded_keyword = _url_encoding(keyword)
        url = "https://www.facebook.com/public?query=" + encoded_keyword + "&type=posts"
        print(url)

        driver.get(url)

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
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            try:
                Div = driver.find_element_by_xpath(
                    "//div[@id='browse_end_of_results_footer']/div/div//div[@class='phm _64f']").text
            except:
                Div = "more result"
                try:
                    if driver.find_element_by_xpath("//div[@id='u_0_c']/div/div/div/div/div/div/div/div/div").text[:29] == "We couldn't find anything for":
                        break
                except:
                    pass

            print(Div)
            if 'End of Results' == Div:
                print("the end")
                break
            else:
                continue

        parse_html(driver.page_source)
    except:
        pass
    driver.close()


def last_process():

    print("total FB results found: ", len(result))

    with open(output_file, 'w', encoding="utf-8") as output:
        for line in result:
            # output.write(line['keyword'] + '<--->' + line['url'] + '\n')
            output.write(line['url'] + '\n')


if __name__ == "__main__":
    with open(input_file) as f:
        keywords = [x for x in f.read().split("\n") if x != ""]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for chunk in tqdm(
            [keywords[x: x + concurrency]
             for x in range(0, len(keywords), concurrency)]
        ):
            try:
                loop = []
                for keyword in chunk:
                    loop.append(executor.submit(scraper, keyword))
                [None for thread in concurrent.futures.as_completed(loop)]
            except Exception:
                print("one failed")
    last_process()
