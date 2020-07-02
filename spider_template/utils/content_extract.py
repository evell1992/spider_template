import json
import re
from ast import literal_eval

import jsonpath
from scrapy.http import Response


class HtmlParse(object):

    @classmethod
    def parse_nav_page(cls, response: Response, selector: dict):
        items = list()
        for k, v in selector.items():
            data = []
            values = response.xpath(v).extract()
            for value in values:
                if k == 'infor_url':
                    value = response.urljoin(value.strip())
                data.append({k: value.strip()})
            items.append(data)
        for item in zip(*items):
            temp_d = dict()
            for i in item:
                temp_d.update(i)
            yield temp_d

    @classmethod
    def parse_detail_page(cls, response: Response, selector: dict):
        items = dict()
        for k, v in selector.items():
            values = response.xpath(v).extract_first()
            items[k] = values.strip() if values else ''
        return items

    @classmethod
    def parse_increment(cls, response: Response, selector: str):
        return response.urljoin(response.xpath(selector).extract_first())


class JsonParse(object):

    @classmethod
    def extract_base_data(cls, response: Response, selector):
        if selector:
            body = re.findall(re.compile(selector, re.S | re.M), response.text)
            if not body:
                raise Exception('数据提取失败')
            return body[0]
        else:
            return response.text

    @classmethod
    def parse_nav_page(cls, response: Response, selector: dict):
        base_regex = selector.pop('base_regex')
        data_regex = selector.pop('data_regex')
        data = cls.extract_base_data(response, base_regex)
        try:
            data_chunk = jsonpath.jsonpath(json.loads(data), data_regex)
        except Exception as e:
            data_chunk = literal_eval(data)
            data_chunk = jsonpath.jsonpath(data_chunk, data_regex)

        if not data_chunk:
            raise Exception('解析失败')

        nav_data = list()
        for d in data_chunk[0]:
            tmp = {}
            for k, v in selector.items():
                fil = re.findall(r'{(.*)}', v)
                if fil:
                    tmp[k] = v.format(**{i: d.get(i) for i in fil})
                else:
                    tmp[k] = d.get(v)
            nav_data.append(tmp)
        return nav_data

    @classmethod
    def parse_increment(cls, response: Response, selector: str):
        k, v = selector.split(':')
        start, end = v.split('-')
        return k, start, end


def get_parser(page_type):
    if page_type == "HTML":
        return HtmlParse
    elif page_type == "JSON":
        return JsonParse
    else:
        raise Exception('页面类型错误')


if __name__ == "__main__":
    json_path = get_parser('json')
