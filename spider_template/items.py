# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from pprint import pprint
import scrapy
from datetime import datetime, timedelta
from dataclasses import dataclass, field


class DetailPageItem(scrapy.Item):
    """
    详情页数据类型: 用于存详情页信息
    """
    result = scrapy.Field()  # 结果
    # province = scrapy.Field()  # 省份
    # city = scrapy.Field()  # 城市
    # county = scrapy.Field()  # 县区
    # dns_name = scrapy.Field()  # 网站域名 （用于后台标识：www.ccgp.org  ，取ccgp作为标识）
    # source_name = scrapy.Field()  # 来源 （爬取数据的网站的中文名称）
    #
    # title = scrapy.Field()  # 标题（列表数据）
    # date = scrapy.Field()  # 发布时间（列表数据）
    # infor_url = scrapy.Field()  # 网页详情原url
    # file_name = scrapy.Field()  # 文件名 （YYYYMMDD+MD5（getURL） 。 如果是post请求，用URL+请求参数，这样后续清洗保存文件的模块可以和数据库一一对应上）
    # html_code = scrapy.Field()  # 网页详情正文（经过简单清洗和瘦身的body正文）
    # create_time = scrapy.Field()  # 爬取时间


class FailedItem(scrapy.Item):
    """
    请求失败类型
    """
    task_name = scrapy.Field()  # 站点
    create_time = scrapy.Field()  # 创建时间
    url = scrapy.Field()  # 网站地址
    code = scrapy.Field()  # 状态码
    msg = scrapy.Field()  # 失败详情


class FinishIncrementItem(scrapy.Item):
    """
    全量任务完成字段
    """
    _id = scrapy.Field()  # 模板id


@dataclass
class TemplateItem:
    """
    模板校验类
    """
    _id: str  # 模板id
    url: str  # 站点url
    task_name: str  # 任务名字
    author: str  # 模板作者
    job_interval: int  # 任务调度间隔
    is_proxy: bool  # 是否需要代理
    is_run: bool  # 模板开启状态
    status: str  # 模板状态
    stage: int  # 当前任务进度
    pipeline: list  # 网页提取规则
    increment: bool  # 是否增量爬取
    default_values: dict = field(default_factory=dict)  # 默认值
    headers: dict = field(default_factory=dict)  # 请求头
    create_time: datetime = field(default_factory=datetime.now)  # 模板创建时间
    last_update_time: datetime = field(default_factory=datetime.now)  # 模板创建时间
    last_fetch_time: datetime = field(default_factory=datetime.now)  # 最后抓取时间
    job_next_time: datetime = field(default_factory=datetime.now)  # 下次调度时间
    code: int = 200
    msg: str = ''

    def __post_init__(self):
        if not isinstance(self.create_time, datetime):
            self.create_time = datetime.strptime(self.create_time, "%Y-%m-%d %H:%M:%S")
        if not isinstance(self.last_fetch_time, datetime):
            self.last_fetch_time = datetime.strptime(self.last_fetch_time, "%Y-%m-%d %H:%M:%S")
        if not isinstance(self.job_next_time, datetime):
            self.job_next_time = datetime.strptime(self.job_next_time, "%Y-%m-%d %H:%M:%S")

    def compute_job_next_time(self) -> datetime:
        now = datetime.now()
        return now + timedelta(minutes=self.job_interval)

    def get_job_next_time(self) -> datetime:
        now = datetime.now()
        return now + timedelta(minutes=self.job_interval)