#!/bin/bash
import pickle
from itertools import chain
from datetime import datetime
from spider_template.items import TemplateItem
from spider_template.db_actions.redis_action import RedisAction
from spider_template.db_actions.mongo_action import TemplateInfo
from spider_template.settings import REDIS_KEY


class Rules(object):

    @staticmethod
    def is_run(record: TemplateItem) -> bool:
        return record.is_run

    @staticmethod
    def job_need_run(record: TemplateItem) -> bool:
        return record.job_next_time <= datetime.now()


class BaseSource(object):
    query = {}

    def __init__(self, db_action):
        self.db_action = db_action

    def get_jobs(self):
        filter_rules = [Rules.is_run, Rules.job_need_run]
        for d in self.db_action.find('template', self.query):
            template = TemplateItem(**d)
            if all(r(template) for r in filter_rules):
                yield template


class Scheduler(object):

    def __init__(self):
        self.mongo_action = TemplateInfo()
        self.redis_action = RedisAction()

    @property
    def jobs(self):
        return chain(BaseSource(self.mongo_action).get_jobs(), )

    def start(self):
        job_num = 0
        for job_num, job in enumerate(self.jobs, start=1):
            task = pickle.dumps(job)
            self.redis_action.push(REDIS_KEY, task)
            set_values = {"job_next_time": job.compute_job_next_time(),
                          "last_fetch_time": datetime.now()}
            if job.increment:
                set_values.update({'increment': False})
            self.mongo_action.update_one('template', {"_id": job._id},
                                         {"$set": set_values})
        print("{}--process template num: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), job_num))


if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.start()
