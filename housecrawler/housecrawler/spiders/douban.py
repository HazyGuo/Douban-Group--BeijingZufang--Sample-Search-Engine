# -*- coding: utf-8 -*-
import time, random
import scrapy
import urllib.request
from lxml import html
from scrapy.http import Request,FormRequest
from housecrawler.items import HousecrawlerItem


class DoubanSpider(scrapy.Spider):
    name = 'douban'
    #allowed_domains = ['douban.com']
    #start_urls = ['http://www.douban.com/group/beijingzufang/discussion?start=0/']

    def start_requests(self):
        url = 'https://www.douban.com/accounts/login'
        return [Request(url=url, meta={"cookiejar": 1}, callback=self.login)]

    def login(self, response):
        captcha = response.xpath('//*[@id="captcha_image"]/@src').extract()  # 获取验证码图片的链接
        if len(captcha) > 0:
            # 人工输入验证码
            print('有验证码', captcha[0])
            urllib.request.urlretrieve(captcha[0], filename="captcha.png")
            captcha_value = input('查看captcha.png,有验证码请输入:')

            # 用快若打码平台处理验证码--------验证码是任意长度字母，成功率较低
            # captcha_value = ruokuai.get_captcha(captcha[0])
            # reg = r'<Result>(.*?)</Result>'
            # reg = re.compile(reg)
            # captcha_value = re.findall(reg, captcha_value)[0]
            print('验证码为：', captcha_value)

            data = {
                'source': 'group',
                'redir': 'https://www.douban.com/group/beijingzufang',
                'form_email': '18810769259',
                'form_password': '1qaz2wsxE',
                'remember': 'on',
                'login': '登录',
                "captcha-solution": captcha_value,
            }
        else:
            print('无验证码')
            data = {
                'source': 'group',
                'redir': 'https://www.douban.com/group/beijingzufang',
                'form_email': '18810769259',
                'form_password': '1qaz2wsxE',
                'remember': 'on',
                'login': '登录'
            }
        print('正在登陆中......')
        ####FormRequest.from_response()进行登陆
        return [
            FormRequest.from_response(
                response,
                meta={"cookiejar": response.meta["cookiejar"]},
                formdata=data,
                callback=self.verify_login,
            )
        ]

    def verify_login(self, response):
        title = response.xpath('//title/text()').extract()[0]
        if '登录豆瓣' in title:
            print('登录失败，请重试！')
        else:
            print('登录成功')
            '''data = {
                'q': '北京租房',
            }'''
            return [
                FormRequest.from_response(
                    response,
                    url='https://www.douban.com/group/beijingzufang/discussion?start=0',
                    meta={"cookiejar": response.meta["cookiejar"]},
                    callback=self.get_url,
                )
            ]

    def get_url(self, response):
        print(response.url)
        urls = response.xpath('//table[@class="olt"]/tr[@class=""]/td[@class="title"]/a/@href').extract()
        for url in urls:
            time.sleep(random.randrange(0, 100) % 5)
            yield Request(
                url,
                meta={"cookiejar": response.meta["cookiejar"]},
                callback=self.parse
            )
        nextpage = response.xpath('//span[@class="next"]/a/@href')
        if nextpage:
            time.sleep(random.randrange(0, 100) % 5)
            yield Request(
                nextpage.extract()[0],
                meta={"cookiejar": response.meta["cookiejar"]},
                callback=self.get_url
            )

    def parse(self, response):
        item = HousecrawlerItem()
        item['url'] = response.url
        selector = html.fromstring(response.text)
        item['title'] = selector.xpath('//title/text()')[0].strip()
        item['time'] = selector.xpath('//div[@id="content"]/div/div/div/div[@class="topic-doc"]/h3/span[last()]/text()')[0]
        item['content'] = ''.join(
            selector.xpath('//div[@id="content"]/div/div/div/div/div/div[@class="topic-content"]/p/text()')).replace('\r', '').replace('\n', '').replace(' ', '')
        yield item