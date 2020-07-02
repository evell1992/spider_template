import copy
import requests
from scrapy.http import HtmlResponse
from spider_template.utils.content_extract import get_parser
from spider_template.utils.etl.news_etl import NewsETL
import json


def download(template):
    pipeline = template.pipeline[template.stage]
    method = pipeline.get('method')
    params = pipeline.get('params')
    url = template.url
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
    }
    headers.update(template.headers)
    if method == 'GET':
        resp = requests.get(url=url, headers=headers)
    else:
        resp = requests.post(url=url, headers=headers, data=json.dumps(params))
    if resp.status_code != 200:
        raise Exception('download error: {}'.format(resp.status_code))
    html_resp = HtmlResponse(url=url, status=200, headers=headers, body=resp.content,
                             encoding=resp.apparent_encoding)
    return html_resp


def verify_nav_page(template):
    html_resp = download(template)
    pipeline = template.pipeline[template.stage]
    page_type = pipeline.get('page_type')
    selector = pipeline.get('data')
    parser = get_parser(page_type)
    results = parser.parse_nav_page(html_resp, selector)
    next_page = ''
    if selector.get('next_page'):
        next_page_s = selector.pop('next_page')
        if template.increment:
            next_page = parser.parse_increment(html_resp, next_page_s)
    return list(results), next_page


def verify_detail_page(template):
    html_resp = download(template)
    pipeline = template.pipeline[template.stage]
    page_type = pipeline.get('page_type')
    selector = pipeline.get('data')
    clean = pipeline.get('content_clean')
    parser = get_parser(page_type)
    results = parser.parse_detail_page(html_resp, selector)
    if clean:
        results['html_code'] = NewsETL.clean_content(results['html_code'])
    results['html_code'] = NewsETL.fill_content(results['html_code'])
    return results


def verify_template(template):
    detail_task, next_page = verify_nav_page(template)
    if ((not template.increment) and next_page) or (template.increment and (not next_page)):
        return False
    if len(detail_task) == 0:
        return False
    for detail_res in detail_task:
        d_template = copy.deepcopy(template)
        d_template.url = detail_res['infor_url']
        d_template.stage = 1
        verify_detail_page(d_template)
    return True
