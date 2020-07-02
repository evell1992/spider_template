# -*- coding: utf-8 -*-
import os

# Scrapy settings for spider_template project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'spider_template'

SPIDER_MODULES = ['spider_template.spiders']
NEWSPIDER_MODULE = 'spider_template.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
}
# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'spider_template.middlewares.CustomDownloadMiddleware': 900,
}

SPIDER_MIDDLEWARES = {
    'spider_template.middlewares.CustomSpiderMiddleware': 543,
}

LOG_LEVEL = "INFO"

ITEM_PIPELINES = {
    'spider_template.pipelines.SpiderTemplatePipeline': 300,
}

env = os.environ
# 数据库配置

# mongo 配置
MONGO_URI = env.get('MONGO_URI') if env.get('MONGO_URI') else ''  # mongo 地址
MONGO_DB = env.get('MONGO_DB') if env.get('MONGO_DB') else "spider_template"  # 库名
MONGO_TEMPLATE = env.get('MONGO_TEMPLATE') if env.get('MONGO_TEMPLATE') else "template_info"  # 模板表
MONGO_ORDATA = env.get('MONGO_ORDATA') if env.get('MONGO_ORDATA') else "or_data"  # 原始数据表
MONGO_FAILED = env.get('MONGO_FAILED') if env.get('MONGO_FAILED') else "failed_data"  # 爬取失败信息表
MONGO_DUPEFILTER = env.get('MONGO_DUPEFILTER') if env.get('MONGO_DUPEFILTER') else "dupe_filter"  # 过滤表

# redis 配置
REDIS_HOST = env.get('REDIS_HOST') if env.get('REDIS_HOST') else ''
REDIS_PORT = env.get('REDIS_PORT') if env.get('REDIS_PORT') else 6379
REDIS_DB = env.get('REDIS_DB') if env.get('REDIS_DB') else 0
REDIS_PARAMS = {
    'password': env.get('REDIS_PWD') if env.get('REDIS_PWD') else 'redis',
}
REDIS_KEY = env.get('REDIS_KEY') if env.get('REDIS_KEY') else "spider_template:template_info"

# rabbitmq 配置
MQ_HOST = env.get('MQ_HOST') if env.get('MQ_HOST') else ''
MQ_PORT = env.get('MQ_PORT') if env.get('MQ_PORT') else 0
MQ_VIRTUAL_HOST = env.get('MQ_VIRTUAL_HOST') if env.get('MQ_VIRTUAL_HOST') else ''
MQ_USER = env.get('MQ_USER') if env.get('MQ_USER') else ''
MQ_PWD = env.get('MQ_PWD') if env.get('MQ_PWD') else ''
MQ_EXCHANGE = env.get('MQ_EXCHANGE') if env.get('MQ_EXCHANGE') else ''

# 去重容器类: 重写去重，改为mongo去重
# DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# DUPEFILTER_CLASS = "scrapy_splash.SplashAwareDupeFilter"

DUPEFILTER_CLASS = 'spider_template.utils.dupefilter.MFPDupeFilter'

# 调度器: 用于把待爬请求存储到基于Redis的队列
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
