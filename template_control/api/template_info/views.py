import copy
import traceback
from ast import literal_eval
from datetime import datetime

from bson.objectid import ObjectId
from flask import jsonify, request

from spider_template.items import TemplateItem
from template_control.api import template as tdb
from . import template_blu
import json
from template_control.utils.template_verify import verify_template


@template_blu.route("", methods=["GET", "POST"])
def templates():
    if request.method == "GET":
        _filters = request.args.get('filter', None)
        count = request.args.get('count', 10)
        page = request.args.get('page', 1)
        filters = dict()
        offset = 0
        try:
            if _filters:
                filters['$or'] = [{"task_name": {'$regex': _filters}}, {"author": {'$regex': _filters}},
                                  {"url": {'$regex': _filters}}]
            if page:
                try:
                    search = int(page)
                    if search >= 1:
                        count = int(count)
                        offset = (search - 1) * count
                except Exception as e:
                    raise Exception('page or count parameter error')
        except Exception as e:
            return jsonify(status=300, message=str(e))

        try:
            data = [dict(_id=str(i.get('_id')),
                         task_name=i.get('task_name'),
                         author=i.get('author'),
                         url=i.get('url'),
                         is_run=i.get('is_run'),
                         last_update_time=i.get('last_update_time').strftime("%Y-%m-%d %H:%M:%S") if i.get(
                             'last_update_time') else '',
                         job_next_time=i.get('job_next_time').strftime("%Y-%m-%d %H:%M:%S") if i.get(
                             'job_next_time') else '',
                         last_fetch_time=i.get('last_fetch_time').strftime("%Y-%m-%d %H:%M:%S") if i.get(
                             'last_fetch_time') else '')
                    for i in tdb.find('template', filters).skip(offset).limit(count)]
            count = tdb.count('template', filters)
            status = 200
            message = 'success'
        except Exception as e:
            status = 300
            message = str(e)
            data = []
            count = 0
        return jsonify(data=data, status=status, message=message, total_count=count)
    else:
        try:
            config = request.get_data()
            config = json.loads(config)
            url = config.get('url')
            if not url:
                raise Exception('not url')
            task_name = config.get('task_name')
            if not task_name:
                raise Exception('not task_name')
            author = config.get('author')
            if not author:
                raise Exception('not author')
            job_interval = int(config.get('job_interval'))
            increment = config.get('increment')
            if increment not in [True, False]:
                raise Exception('increment must be bool')
            headers = config.get('headers', {})
            print(headers)
            if not isinstance(headers, dict):
                headers = {i.split(':')[0].strip(): i.split(':')[1].strip() for i in headers.split('\n') if
                           i.strip() != ''}
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
            tmp = dict(_id='new_task',
                       url=url,
                       task_name=task_name,
                       author=author,
                       headers=headers,
                       pipeline=pipelines,
                       job_interval=job_interval,
                       is_run=False,
                       is_proxy=False,
                       status="正常",
                       stage=0,
                       increment=increment,
                       default_values=default_values,
                       create_time=datetime.now(),
                       last_update_time=datetime.now()
                       )
            template = TemplateItem(**tmp)
        except Exception as e:
            traceback.print_exc()
            return jsonify(msg='template config error : {}'.format(e), status=302, data=[])
        try:
            verify_result = verify_template(template)
            if verify_result:
                tmp.pop('_id')
                tdb.insert('template', tmp)
                return jsonify(status=200, msg='template add success')
            else:
                return jsonify(status=300, msg='template add failed please check template')
        except Exception as e:
            return jsonify(status=300, msg='template add failed: {}'.format(e))


@template_blu.route("/<string:_id>", methods=["GET", "POST"])
def template_info(_id):
    if request.method == "GET":
        try:
            template_id = ObjectId(_id)
            data = tdb.find_one('template', {'_id': template_id})
            data.update({'_id': _id})
            data.pop('is_run')
            data.pop('status')
            data.pop('stage')
            if data.get('job_next_time'):
                data.pop('job_next_time')
            if data.get('last_fetch_time'):
                data.pop('last_fetch_time')
            data['headers'] = ''.join(['{}:{}\n'.format(k, v) for k, v in data.get('headers', None)]) if data.get(
                'headers') else None
            status = 200
            message = 'success'
        except Exception as e:
            traceback.print_exc()
            status = 300
            message = 'error: {}'.format(str(e))
            data = {}
        return jsonify(data=data, status=status, message=message)
    else:
        try:
            template_id = ObjectId(_id)
            old_template = tdb.find_one('template', {'_id': template_id})
            if not old_template:
                raise Exception('template is not exist')
        except Exception as e:
            return jsonify(status=400, msg='search failed: {}'.format(e))
        try:
            config = request.get_data()
            config = json.loads(config)
            url = config.get('url')
            if not url:
                raise Exception('not url')
            task_name = config.get('task_name')
            if not task_name:
                raise Exception('not task_name')
            author = config.get('author')
            if not author:
                raise Exception('not author')
            job_interval = int(config.get('job_interval'))
            increment = config.get('increment')
            if increment not in [True, False]:
                raise Exception('increment must be bool')
            headers = config.get('headers', {})
            if not isinstance(headers, dict):
                headers = {i.split(':')[0].strip(): i.split(':')[1].strip() for i in headers.split('\n') if
                           i.strip() != ''}
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
            tmp = dict(_id=template_id,
                       url=url,
                       task_name=task_name,
                       author=author,
                       headers=headers,
                       pipeline=pipelines,
                       job_interval=job_interval,
                       is_run=False,
                       is_proxy=False,
                       status="正常",
                       stage=0,
                       increment=increment,
                       default_values=default_values,
                       )
            old_template.update(tmp)
            update_items = copy.deepcopy(old_template)
            template = TemplateItem(**old_template)
        except Exception as e:
            traceback.print_exc()
            return jsonify(msg='template config error : {}'.format(e), status=302, data=[])
        try:
            verify_result = verify_template(template)
            if verify_result:
                update_items["last_update_time"] = datetime.now()
                update_items["_id"] = template_id
                tdb.save('template', update_items)
                return jsonify(status=200, msg='template update success')
            else:
                return jsonify(status=300, msg='template verify failed please check template')
        except Exception as e:
            traceback.print_exc()
            return jsonify(status=300, msg='template verify failed: {}'.format(e))


@template_blu.route("/switch_state", methods=["POST"])
def switch_state():
    params = request.get_data()
    params = json.loads(params)
    _id = params.get('_id')
    state = params.get('state', False)
    if not _id or (state not in (True, False)):
        return jsonify(status=300, msg='prams error')
    try:
        template_id = ObjectId(_id)
        tdb.update_one('template', {'_id': template_id}, {'$set': {'is_run': state}})
        msg = 'success'
        status = 200
    except Exception as e:
        status = 400
        msg = 'state switch failed：{}'.format(e)
    return jsonify(status=status, msg=msg)
