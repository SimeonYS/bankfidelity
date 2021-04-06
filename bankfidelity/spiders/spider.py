import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BbankfidelityItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class BbankfidelitySpider(scrapy.Spider):
	name = 'bankfidelity'
	start_urls = ['https://www.bankfidelity.bank/media-events/blog']

	def parse(self, response):
		post_links = response.xpath('//div[@class="links_area_item"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[contains(text(),">")]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//div[@id="page_copy"]/p/em/text() | //div[@id="page_copy"]/p/text()').get()
		date = re.findall(r'\w+\s\d+\,\s\d+', date)
		title = response.xpath('//h3/text()').get() + response.xpath('//h1/text()').get()
		content = response.xpath('//div[@id="page_copy"]//text()[not (ancestor::p/em)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BbankfidelityItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
