import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import RaiffeisenatItem
from itemloaders.processors import TakeFirst
import requests

url = "https://rwm.prd.pi.r-itservices.at/api/rwm-search/search-ui-services/rest/newssearch/contents"

payload="{\"type\":\"NEWSSUCHE\",\"size\":99,\"offset\":1,\"path\":\"/content/rbg/stmk/rlb/website/de\",\"tagFilters\":[],\"predefinedTagFilters\":[\"/content/cq:tags/rbg/presse-news/bankengruppe\",\"/content/cq:tags/rbg/presse-news/landesbank\",\"/content/cq:tags/rbg/presse-news/jahr-2021\", \"/content/cq:tags/rbg/presse-news/jahr-2020\"],\"maxAge\":2000,\"from\":null,\"to\":null,\"query\":null}"
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'Accept': 'application/json, text/plain, */*',
  'Authorization': 'Bearer 0019gTy9LkhCw4gNtzlig3um7P3zNQoOBxtxVlPLl7Ig36EfmRm0uCPa7qll',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
  'Content-Type': 'application/json;charset=UTF-8',
  'Origin': 'https://www.raiffeisen.at',
  'Sec-Fetch-Site': 'cross-site',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.raiffeisen.at/',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': 'd7ab8cdf683c611d64a813547e7047f6=0b356087ea1f72cfa8abe5d92dc78b63'
}


class RaiffeisenatSpider(scrapy.Spider):
	name = 'raiffeisenat'
	start_urls = ['https://www.raiffeisen.at/stmk/rlb/de/meine-bank/raiffeisen-bankengruppe/presseaussendungen.html']

	def parse(self, response):
		data = requests.request("POST", url, headers=headers, data=payload)
		raw_data = json.loads(data.text)
		for post in raw_data['documents']:
			link = post['detail']['url']
			date = post['detail']['newsDate']
			title = post['detail']['title']
			yield response.follow(link, self.parse_post, cb_kwargs={'date': date, 'title': title})

	def parse_post(self, response, date, title):
		description = response.xpath('//div[@class="component-text rte "]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=RaiffeisenatItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
