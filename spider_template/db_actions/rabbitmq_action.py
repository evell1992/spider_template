import pika
import json

from spider_template.settings import MQ_HOST, MQ_PORT, MQ_VIRTUAL_HOST, MQ_USER, MQ_PWD, MQ_EXCHANGE
from spider_template.utils.context import Pool


class RabbitMqAction(object):

    def __init__(self):
        credentials = pika.PlainCredentials(MQ_USER, MQ_PWD)  # mq用户名和密码
        # 虚拟队列需要指定参数 virtual_host，如果是默认的可以不填。
        self.parameters = pika.ConnectionParameters(host=MQ_HOST, port=MQ_PORT, virtual_host=MQ_VIRTUAL_HOST,
                                                    credentials=credentials, heartbeat=0)
        self.connection = self._connection
        self.channel = self.connection.channel()
        # 声明exchange，由exchange指定消息在哪个队列传递，如不存在，则创建。durable = True 代表exchange持久化存储，False 非持久化存储
        self.channel.exchange_declare(exchange=MQ_EXCHANGE, exchange_type='fanout', durable=True)

    @property
    def _connection(self):
        return pika.BlockingConnection(self.parameters)

    @Pool(1)
    def check_connect(self):
        while True:
            pass

    def push_single_msg(self, item):
        message = json.dumps(item)
        # 向队列插入数值 routing_key是队列名。delivery_mode = 2 声明消息在队列中持久化，delivery_mod = 1 消息非持久化。routing_key 不需要配置
        self.channel.basic_publish(exchange=MQ_EXCHANGE, routing_key='', body=message,
                                   properties=pika.BasicProperties(delivery_mode=2, content_type="text/json"))

    def consumer(self, queue):
        self.channel.queue_declare(queue=queue, durable=True)

        # 定义一个回调函数来处理消息队列中的消息，这里是打印出来
        def callback(ch, method, properties, body):
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(body.decode())

        # 告诉rabbitmq，用callback来接收消息
        self.channel.basic_consume(queue, callback)
        # 开始接收信息，并进入阻塞状态，队列里有信息才会调用callback进行处理
        self.channel.start_consuming()

    def __del__(self):
        self.connection.close()


if __name__ == "__main__":
    mq = RabbitMqAction()
    # item = {
    #     "table_name": "test",
    #     "infor_url": "http://xxx.com/xxxx"
    # }
    # mq.push_single_msg(item)
    mq.consumer(MQ_EXCHANGE)
