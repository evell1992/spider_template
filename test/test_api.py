import json
from pprint import pprint

import requests


def nav_page():
    """导航页测试"""
    data = {
        "url": "https://zfcg.wzzbtb.com/wzcms/gcjsbzjtf/index.htm#add",
        "headers": """'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
    """,
        "pipeline": {
            "page_type": "html",
            "method": "GET",
            "params": '{}',
            "data": """{
                "infor_url": "//div[@class='List-Li FloatL']/ul/li/a/@href",
                "title": "//div[@class='List-Li FloatL']/ul/li/a/@title",
                "date": "//div[@class='List-Li FloatL']/ul/li/span/text()",
                "next_page": "//div[@class='Zy-Page FloatL']/div/a[3]/@href"
            }"""
        }
    }
    resp = requests.post('http://0.0.0.0:12345/verify/nav_test', data=json.dumps(data))
    pprint(resp.json())


def detail_page():
    """详情页测试"""
    data = {
        "url": "https://zfcg.wzzbtb.com/wzcms/gcjsbzjtf/index.htm#add",
        "headers": '',
        "default_values": """{
            "province": "浙江省",
            "city": "温州市",
            "county": "",
            "type_name": "交易信息",
            "dns_name": "wzzbtb",
            "source_name": "温州市公共资源交易网"
        }""",
        "pipeline": [
            {
                "page_type": "html",
                "method": "GET",
                "params": '{}',
                "data": """{
                    "infor_url": "//div[@class='List-Li FloatL']/ul/li/a/@href",
                    "title": "//div[@class='List-Li FloatL']/ul/li/a/@title",
                    "date": "//div[@class='List-Li FloatL']/ul/li/span/text()",
                    "next_page": "//div[@class='Zy-Page FloatL']/div/a[3]/@href"
                }"""
            },
            {
                "page_type": "html",
                "method": "GET",
                "params": '{}',
                "data": """{
                    "html_code": "//div[@class='Main-p']"
                }"""
            }
        ]
    }
    resp = requests.post('http://0.0.0.0:12345/verify/detail_test', data=json.dumps(data))
    pprint(resp.json())


def template_info_get():
    """单个模板信息获取"""
    resp = requests.get('http://0.0.0.0:12345/template/5ed6143be09675b43d35c623')
    pprint(resp.json())


def template_info_post():
    """单个模板信息修改"""
    data = {
        "url": 'https://zfcg.wzzbtb.com/wzcms/gcjsbzjtf/index.htm#add',
        'task_name': '温州市公共资源交易网',
        "author": "曹爱栋",
        'job_interval': 40,
        'increment': 'false',
        'default_values': '',
        "headers": """Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
            Accept-Language: en
            User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36
        """,
        "pipeline": [
            {'data': """{'date': "//div[@class='List-Li FloatL']/ul/li/span/text()",
                      'infor_url': "//div[@class='List-Li FloatL']/ul/li/a/@href",
                      'next_page': "//div[@class='Zy-Page FloatL']/div/a[3]/@href",
                      'title': "//div[@class='List-Li FloatL']/ul/li/a/@title"}""",
             'method': 'GET',
             'page_type': 'html',
             'params': '{}'
             },
            {'data': """{'html_code': "//div[@class='Main-p']"}""",
             'method': 'GET',
             'page_type': 'html',
             'params': ''
             }
        ],
    }
    resp = requests.post('http://0.0.0.0:12345/template/5ed6143be09675b43d35c623', data=json.dumps(data))
    pprint(resp.json())


def get_template_list():
    """获取 模板 列表 """
    resp = requests.get('http://0.0.0.0:12345/template')
    pprint(resp.json())


def add_new_template():
    """添加新模板"""
    data = {
        "url": 'http://www.qzggzy.com/jyxx/002001/002001005/trade.html',
        'task_name': '衢州市公共资源交易网',
        "author": "曹爱栋",
        'job_interval': 40,
        'increment': 'false',
        'default_values': '',
        "headers": '',
        "pipeline": [
            {'data': """{'date': "//ul[@class='ewb-col-item news-list-items']/li/span/text()",
                      'infor_url': "//ul[@class='ewb-col-item news-list-items']//a/@href",
                      'next_page': "//ul[@class='m-pagination-page']/li[last()]/a/@data-page-index",
                      'title': "//ul[@class='ewb-col-item news-list-items']/li/div/a/text()"}""",
             'method': 'GET',
             'page_type': 'html',
             'params': '{}'
             },
            {'data': """{'html_code': "//div[@class='ewb-content']"}""",
             'method': 'GET',
             'page_type': 'html',
             'params': ''
             }
        ],
    }
    resp = requests.post('http://0.0.0.0:12345/template', data=json.dumps(data))
    pprint(resp.json())


def test_switch_state():
    data = {
        '_id': '5ed9a841e09675b43d35c624',
        'state': 'true'
    }
    resp = requests.post('http://0.0.0.0:12345/template/switch_state', data=json.dumps(data))
    pprint(resp.json())


if __name__ == "__main__":
    # detail_page()
    # nav_page()
    # template_info_get()
    # template_info_post()
    # get_template_list()
    # add_new_template()
    test_switch_state()
