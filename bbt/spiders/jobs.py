# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy import Request

from bbt.items import BbtItem

import re


class JobsSpider(Spider):
    name = 'jobs'
    allowed_domains = ['bigbangtrans.wordpress.com']
    start_urls = ['https://bigbangtrans.wordpress.com/']

    def parse(self, response):
        jobs = response.xpath(
            '//ul/li[contains(@class, "page_item page-item-")]')
        for job in jobs:
            official_title = job.xpath('a/text()').extract_first()
            if official_title == 'About':
                continue
            relative_url = job.xpath('a/@href').extract_first()
            absolute_url = response.urljoin(relative_url)
            season = official_title[7:9]
            episode = official_title[18:20]
            title = official_title[23:]
            yield Request(absolute_url, callback=self.parse_page,
                          meta={'Season': season, 'Episode': episode, 'Title': title})

    def parse_page(self, response):
        item = BbtItem()
        item["season"] = response.meta.get('Season')
        item["episode"] = response.meta.get('Episode')
        item["title"] = response.meta.get('Title')
        if (int(item["season"]) == 6 and int(item["episode"])) == 1 or (int(item["season"]) == 7 and 1 <= int(item["episode"]) <= 15) or int(item["season"]) == 10:
            item["content"] = " ".join(response.xpath(
                '//div[@class="entrytext"]/p/span/text()').extract())
        elif (int(item["season"]) >= 2 and int(item["episode"]) >= 2) or int(item["season"]) >= 3:
            item["content"] = " ".join(response.xpath(
                '//div[@class="entrytext"]/p/text()').extract())
        else:
            item["content"] = " ".join(response.xpath(
                '//div[@class="entrytext"]/p/span/text()').extract())

        item["word"] = self.split_content(item["content"])
        yield item

    def replace_special_character(self, string, substitutions):
        substrings = sorted(substitutions, key=len, reverse=True)
        regex = re.compile('|'.join(map(re.escape, substrings)))
        return regex.sub(lambda match: substitutions[match.group(0)], string)

    def split_content(self, content):
        lower_content = content.lower()
        removed_sign = re.sub(re.compile(
            "[\’\–\…\‘\‚\“\„\.,?!-/:-@[-`{-~]"), '', lower_content)
        substitutions = {"ā": "a", "é": "e", "ī": "i", "ō": "o", "ū": "u"}
        replaced_special_character = self.replace_special_character(
            removed_sign, substitutions)
        splited_content = replaced_special_character.split()
        return splited_content
