# -*- coding: utf-8 -*-
import copy
import hashlib
import pickle
import time
import scrapy
from datetime import datetime

from scrapy_redis.spiders import RedisSpider
from spider_template.settings import REDIS_KEY
from spider_template.items import FailedItem, DetailPageItem
from spider_template.utils.etl.news_etl import NewsETL
from spider_template.utils.content_extract import get_parser


class SpiderTemplate(RedisSpider):
    name = 'spider_template'
    redis_key = REDIS_KEY

    def make_request_from_data(self, data):
        """
        根据redis中读取的分类信息的二进制数据, 构建请求
        :param data: 分类信息的二进制数据
        :return: 根据小分类URL, 构建的请求对象
        """
        # 把分类信息的二进制数据 转换为字典
        template = pickle.loads(data)
        pipeline = template.pipeline[template.stage]
        method = pipeline.get('method')
        params = pipeline.get('params')
        is_js = pipeline.get('is_js')
        if method == "GET":
            return scrapy.Request(url=template.url, callback=self.nav_parse, meta={'template': template})
        elif method == "POST":
            return scrapy.FormRequest(url=template.url, method=method, formdata=params,
                                      callback=self.nav_parse, meta={'template': template})

    def nav_parse(self, response):
        """
        导航页处理
        :param response:
        :return:
        """
        template = response.meta.get('template')
        code = template.code
        if code != 200:
            yield FailedItem(
                task_name=template.task_name,
                create_time=datetime.now(),
                url=template.url,
                code=template.code,
                msg=template.msg)
        else:
            pipeline = template.pipeline[template.stage]
            stage = template.stage
            selector = copy.deepcopy(pipeline.get('data'))
            increment = template.increment
            increment_selector = selector.pop('next_page') if selector.get('next_page') else None
            page_type = pipeline.get('page_type')
            is_js = pipeline.get('is_js')
            parser = get_parser(page_type)
            results = parser.parse_nav_page(response, selector)
            for result in results:
                next_url = result.get('infor_url')
                if next_url and stage <= len(template.pipeline) - 2:
                    # 处理下一个pipeline、
                    next_url = response.urljoin(next_url)
                    try:
                        if stage < len(template.pipeline) - 2:
                            # 如果有下一个url,并且下一个不是详情页
                            # 导航页抓取
                            nav_template = copy.deepcopy(template)
                            nav_template.url = next_url
                            nav_template.stage = stage + 1
                            result.update({'infor_url': next_url})
                            nav_template.default_values.update(result)
                            method = nav_template.pipeline[nav_template.stage].get('method')
                            params = nav_template.pipeline[nav_template.stage].get('params')
                            if method == "GET":
                                yield scrapy.Request(url=nav_template.url,
                                                     callback=self.nav_parse,
                                                     meta={'template': nav_template})
                            elif method == "POST":
                                yield scrapy.FormRequest(url=nav_template.url,
                                                         method=method,
                                                         formdata=params,
                                                         callback=self.nav_parse,
                                                         meta={'template': nav_template})
                        if stage == len(template.pipeline) - 2:
                            # 详情页抓取
                            detail_template = copy.deepcopy(template)
                            detail_template.url = next_url
                            detail_template.stage = stage + 1
                            result.update({'infor_url': next_url})
                            detail_template.default_values.update(result)
                            method = detail_template.pipeline[detail_template.stage].get('method')
                            params = detail_template.pipeline[detail_template.stage].get('params')
                            if method == "GET":
                                yield scrapy.Request(url=detail_template.url,
                                                     callback=self.detail_parse,
                                                     meta={'template': detail_template})
                            elif method == "POST":
                                yield scrapy.FormRequest(url=detail_template.url,
                                                         method=method,
                                                         formdata=params,
                                                         callback=self.detail_parse,
                                                         meta={'template': detail_template})
                    except Exception as e:
                        yield FailedItem(
                            task_name=template.task_name,
                            create_time=datetime.now(),
                            url=next_url,
                            code=501,
                            msg='列表页解析异常:{}'.format(e))
                else:
                    # 详情页数据处理
                    for res in self.detail_parse(response=response):
                        yield res
            if increment and increment_selector:
                # 增量数据爬取
                try:
                    next_page = parser.parse_increment(response, increment_selector)
                    if next_page:
                        in_template = copy.deepcopy(template)
                        pipeline = in_template.pipeline[in_template.stage]
                        method = pipeline.get('method')
                        params = pipeline.get('params')
                        is_js = pipeline.get('is_js')
                        if method == "GET":
                            in_template.url = response.urljoin(next_page)
                            yield scrapy.Request(url=in_template.url, callback=self.nav_parse,
                                                 meta={'template': in_template})
                        elif method == "POST":
                            in_template.increment = False
                            k, start, end = next_page
                            for i in range(int(start), int(end)):
                                new_params = copy.deepcopy(params)
                                new_params.update({k: str(int(params.get(k)) + i)})
                                yield scrapy.FormRequest(url=in_template.url, method=method, formdata=new_params,
                                                         callback=self.nav_parse, meta={'template': in_template})
                except Exception as e:
                    yield FailedItem(
                        task_name=template.task_name,
                        create_time=datetime.now(),
                        url=template.url,
                        code=502,
                        msg='增量任务解析异常:{}'.format(e))

    def detail_parse(self, response):
        """
        详情页处理
        :param response:
        :return:
        """
        template = copy.deepcopy(response.meta.get('template'))
        code = template.code
        try:
            if code != 200:
                yield FailedItem(
                    task_name=template.task_name,
                    create_time=datetime.now(),
                    url=template.url,
                    code=template.code,
                    msg=template.msg)
            else:
                stage = template.stage
                pipeline = copy.deepcopy(template.pipeline[stage])
                selector = pipeline.get('data')
                page_type = pipeline.get('page_type')
                content_clean = pipeline.get('content_clean')
                parser = get_parser(page_type)
                detail = parser.parse_detail_page(response, selector)
                if not detail['html_code']:
                    raise Exception('详情页未提取到内容')
                if content_clean:
                    detail['html_code'] = NewsETL.clean_content(detail['html_code'])
                else:
                    detail['html_code'] = NewsETL.fill_content(detail['html_code'])
                result = template.default_values
                detail.update({'file_name': self.get_file_name(template.url),
                               "create_time": datetime.now()})
                result.update(detail)
                yield DetailPageItem(result=result)
        except Exception as e:
            yield FailedItem(
                task_name=template.task_name,
                create_time=datetime.now(),
                url=template.url,
                code=503,
                msg='详情页解析异常:{}'.format(e))

    @staticmethod
    def get_file_name(url):
        month_day = time.strftime('%Y%m%d', time.localtime(time.time()))
        return month_day + hashlib.md5(url.encode("utf-8")).hexdigest()
