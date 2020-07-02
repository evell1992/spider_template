from ast import literal_eval
import copy
import traceback
from flask import jsonify, request
from . import verify_blu
import json
from spider_template.items import TemplateItem
from template_control.utils.template_verify import verify_nav_page, verify_detail_page


@verify_blu.route("/nav_test", methods=["POST"])
def nav_test():
    try:
        config = request.get_data()
        config = json.loads(config)
        url = config.get('url')
        if not url:
            raise Exception('not url')
        headers = config.get('headers', {})
        if not isinstance(headers, dict):
            headers = {i.split(':')[0].strip(): i.split(':')[1].strip() for i in headers.split('\n') if i.strip() != ''}
        pipeline = config.get('pipeline')
        if not isinstance(pipeline, dict):
            raise Exception('pipeline must be dict')
        page_type = pipeline.get('page_type')
        if page_type not in ['HTML', 'JSON']:
            raise Exception('page_type must be HTML or JSON')
        method = pipeline.get('method')
        if method not in ['GET', 'POST']:
            raise Exception('method must be GET or POST')
        params = literal_eval(pipeline.get('params'))
        if not isinstance(params, dict):
            raise Exception('params must be dict')
        data = literal_eval(pipeline.get('data'))
        if not isinstance(data, dict):
            raise Exception('data must be dict')
        pipeline.update({'params': params, 'data': data})
        tmp = dict(_id='nav_test',
                   url=url,
                   headers=headers,
                   pipeline=[pipeline],
                   task_name='nav_test',
                   author='nav_test',
                   job_interval=60,
                   is_run=True,
                   is_proxy=False,
                   status="正常",
                   stage=0,
                   increment=True,
                   default_values={},
                   )
        template = TemplateItem(**tmp)
    except Exception as e:
        traceback.print_exc()
        return jsonify(msg='template config error : {}'.format(e), status=302, data=[])
    try:
        results = verify_nav_page(template)
        return jsonify(msg='success', status=200, data=results[0], next_page=results[1])
    except Exception as e:
        traceback.print_exc()
        return jsonify(msg='nav page test error : {}'.format(e), status=502, data=[])


@verify_blu.route("/detail_test", methods=["POST", "GET"])
def detail_test():
    try:
        config = request.get_data()
        config = json.loads(config)
        url = config.get('url')
        if not url:
            raise Exception('not url')
        headers = config.get('headers', {})
        if not isinstance(headers, dict):
            headers = {i.split(':')[0].strip(): i.split(':')[1].strip() for i in headers.split('\n') if i.strip() != ''}
        default_values = literal_eval(config.get('default_values') if config.get('default_values') else '{}')
        if not isinstance(default_values, dict):
            raise Exception('pipeline must be dict')
        pipelines = config.get('pipeline')
        if not isinstance(pipelines, list):
            raise Exception('pipeline must be list')
        for pipeline in pipelines:
            if not isinstance(pipeline, dict):
                raise Exception('pipeline must be dict')
            page_type = pipeline.get('page_type')
            if page_type not in ['HTML', 'JSON']:
                raise Exception('page_type must be HTML or JSON')
            method = pipeline.get('method')
            if method not in ['GET', 'POST']:
                raise Exception('method must be GET or POST')
            params = literal_eval(pipeline.get('params') if pipeline.get('params') else '{}')
            if not isinstance(params, dict):
                raise Exception('params must be dict')
            data = eval(pipeline.get('data'))
            if not isinstance(data, dict):
                raise Exception('data must be dict')
            pipeline.update({'params': params, 'data': data})
        tmp = dict(_id='nav_test',
                   url=url,
                   headers=headers,
                   pipeline=pipelines,
                   task_name='nav_test',
                   author='nav_test',
                   job_interval=60,
                   is_run=True,
                   is_proxy=False,
                   status="正常",
                   stage=0,
                   increment=True,
                   default_values=default_values,
                   )
        template = TemplateItem(**tmp)
    except Exception as e:
        traceback.print_exc()
        return jsonify(msg='template config error : {}'.format(e), status=302, data=[])
    try:
        data = list()
        for detail_res in verify_nav_page(template)[0]:
            d_template = copy.deepcopy(template)
            d_template.url = detail_res['infor_url']
            d_template.stage = 1
            temp_res = copy.deepcopy(template.default_values)
            temp_res.update(detail_res)
            temp_res.update(verify_detail_page(d_template))
            data.append(temp_res)
        return jsonify(msg='success', status=200, data=data)
    except Exception as e:
        traceback.print_exc()
        return jsonify(msg='detail page test failed : {}'.format(e), status=502, data=[])
