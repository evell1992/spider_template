# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

from spider_template.db_actions.rabbitmq_action import RabbitMqAction
from spider_template.items import DetailPageItem, FailedItem, FinishIncrementItem
from spider_template.settings import MONGO_URI, MONGO_DB
from spider_template.spiders.template import SpiderTemplate


class SpiderTemplatePipeline:

    def open_spider(self, spider):
        """当爬虫启动的时候执行"""
        if isinstance(spider, SpiderTemplate):
            # open_spider方法中, 链接 MongoDB数据库, 获取要操作的集合
            self.mongo = pymongo.MongoClient(MONGO_URI)
            self.db = self.mongo[MONGO_DB]
            self.mq = RabbitMqAction()

    def process_item(self, item, spider):
        """结果分类处理"""
        if isinstance(item, DetailPageItem):
            # 数据插入mongo
            result = item.get('result')
            collection = self.db[result.get('dns_name')]
            collection.insert_one(result)

            # # 推送mq
            # message = {
            #     "table_name": result.get('dns_name'),
            #     "infor_url": result.get('infor_url')
            # }
            # try:
            #     self.mq.push_single_msg(message)
            # except Exception as e:
            #     mq_collection = self.db['multiProvince']
            #     mq_collection.insert_one(message)
        if isinstance(item, FailedItem):
            collection = self.db['failed']
            collection.insert_one(dict(item))
        if isinstance(item, FinishIncrementItem):
            # self.item.update_one('template', {'_id': item._id}, {'$set': {''}})
            pass
            # TODO
        return item

    def close_spider(self, spider):
        # close_spider 方法中, 关闭MongoDB的链接
        if isinstance(spider, SpiderTemplate):
            self.mongo.close()
