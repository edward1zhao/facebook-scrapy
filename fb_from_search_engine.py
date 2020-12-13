import json
import time
import random
import aiohttp
import asyncio
import pandas as pd
from tqdm import tqdm
from fake_useragent import UserAgent
from selectolax.parser import HTMLParser


class SearchEngineScraper:
    def __init__(self, input_file, output_file, use_proxy, concurrency, search_engine):
        self.result = []
        self.input_file = input_file
        self.output_file = output_file
        self.ua = UserAgent()
        self.proxies = self._get_proxies() + [None]
        self.search_engine = search_engine
        self.size = concurrency
        self.use_proxy = use_proxy

    def _get_proxies(self):
        with open("proxies") as f:
            return list(set([x for x in f.read().split("\n") if x != ""]))

    async def bing(self, session, domain, proxy):
        headers = {
            "authority": "www.bing.com",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "user-agent": self.ua.random,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate",
        }

        proxy = "http://" + proxy if self.use_proxy else None
        q = f'"{domain}" site:facebook.com'

        async with session.get(
            f"https://bing.com/search?q={q}", proxy=proxy, headers=headers
        ) as r:
            html = await r.text()

        try:
            result = HTMLParser(html).css_first(".b_algo > h2 > a").attributes["href"]
            self.result.append({"fb": result, "url": domain})
            print(result)
        except Exception as e:
            result = "not available"
            self.result.append({"fb": result, "url": domain})
            print(e)

    async def duck(self, session, domain, proxy):
        headers = {
            "authority": "duckduckgo.com",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "user-agent": self.ua.random,
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
        }
        proxy = "http://" + proxy if self.use_proxy else None
        q = f'"{domain}" site:facebook.com'
        params = (("q", q), ("t", "h_"), ("ia", "web"))

        async with session.get(
            "https://duckduckgo.com/", params=params, proxy=proxy, headers=headers
        ) as r:
            content = await r.text()

        vqd = content.split("vqd=")[-1].split("&")[0]
        params = (("q", q), ("vqd", vqd))

        async with session.get(
            "https://duckduckgo.com/d.js", params=params, proxy=proxy, headers=headers
        ) as r:
            body = await r.text()

        body = body.split("nrn('d',[")[-1].split("]")[0]
        body = json.loads("[" + body + "]")
        page = body[0]["u"]

        if "google.com/search" in page:
            self.result.append({"fb": "not available", "url": domain})
            return

        self.result.append({"fb": page, "url": domain})

    async def main(self):
        method = {"bing": self.bing, "duck": self.duck}
        with open(self.input_file) as f:
            domains = [x for x in f.read().split("\n") if x != ""]

        domains = [
            domains[i : i + self.size] for i in range(0, len(domains), self.size)
        ]

        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for batch in tqdm(domains):
                random.shuffle(self.proxies)
                batch = zip(batch, self.proxies[: len(batch)])
                await asyncio.wait(
                    [
                        method[self.search_engine](session, domain, proxy)
                        for domain, proxy in batch
                    ]
                )

                df = pd.DataFrame(self.result)
                df.to_csv(self.output_file, index=False)

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main())


if __name__ == "__main__":
    SearchEngineScraper(
        input_file="shopify3001.txt",
        output_file="shopify3001.csv",
        use_proxy=False,
        concurrency=20,
        search_engine="duck",
    ).run()
