#!/usr/bin/env python
# coding=utf-8
# pip install -I -U service_identity
# pip install pika==0.10.0
# import traceback
import sys
import logging
import time
import threading
import pika

'''
如果用了basicConfig那么所有模块的日志都会打印
logging.basicConfig(
    level = logging.INFO,
    #format = "%(asctime)s [%(levelname)-8s] %(message)s"
    format = "%(asctime)s [%(levelname)s] %(message)s"
)
'''

logger = logging.getLogger(__name__)
'''
logger.setLevel(level = logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(name)s] [%(levelname)s] %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)
'''


class RabbitMQClient(object):

    def __init__(self, sv_addr, sv_port, username, passwd):

        self.credentials = pika.PlainCredentials(username, passwd)
        self.sv_addr = sv_addr
        self.sv_port = int(sv_port)
        self.consume_info = {}
        self.consume_state = False

    def connect(self):
        try:
            self.conn = pika.BlockingConnection(
                pika.ConnectionParameters(self.sv_addr, self.sv_port,
                                          '/', self.credentials, heartbeat_interval=0))
            self.ch = self.conn.channel()
            t = threading.Thread(target=self.connect_check)
            t.start()
        except:
            '''
            这种方法比用logger的exc_info=True,多了exception类所在的代码路径
            ex_type, ex_val, ex_stack = sys.exc_info()
            logger.error("ex_type: %s" %ex_type)
            logger.error("ex_val: %s" %ex_val)
            for ex_stack_info in traceback.extract_tb(ex_stack):
                logger.error("stack_info: %s" %str(ex_stack_info))
            '''
            logger.error("connect rabbitmq failed:%s:%s, stop starting" % (self.sv_addr, self.sv_port))
            logger.error("Exception:", exc_info=True)
            while True:
                time.sleep(1)
                logger.error("connect rabbitmq failed:%s:%s, stop starting" % (self.sv_addr, self.sv_port))

    def reconnect(self):
        try:
            logger.error("reconnect rabbitmq: %s:%s" % (self.sv_addr, self.sv_port))
            self.conn = pika.BlockingConnection(
                pika.ConnectionParameters(self.sv_addr,
                                          self.sv_port, '/', self.credentials))
            self.ch = self.conn.channel()
        except:
            logger.error("reconect failed, after 1s will reconnect")
            # logger.error("Exception:", exc_info=True)

    def connect_check(self):
        while True:
            try:
                time.sleep(5)
                logger.debug("connection state: %d" % int(self.conn.is_open))
                if not self.conn.is_open:
                    self.reconnect()
            except:
                logger.error("connect_check error!!!.")
                # logger.error("Exception:", exc_info=True)

    def publish(self, queue_name, queue_body):
        try:
            self.ch.basic_publish(exchange="", routing_key=queue_name, body=queue_body)
            logger.info("publish:%s" % queue_body)

        except:
            logger.error("publish error:")
            logger.error("Exception:", exc_info=True)

    def consume(self, queue_name, callback):
        try:
            if queue_name not in self.consume_info:
                self.consume_info[queue_name] = callback
        except:
            logger.error("Exception:", exc_info=True)

    def restart_consuming(self):
        for queue_name in self.consume_info:
            self.ch.queue_declare(queue=queue_name)
            self.ch.basic_consume(self.consume_info[queue_name], queue=queue_name, no_ack=True)
        logger.info("consume_info is %s" % str(self.consume_info))
        self.ch.connection.process_data_events(time_limit=1)
        self.ch.start_consuming()

    def start_consuming(self, noargs):
        while True:
            try:
                self.restart_consuming()
                time.sleep(1)
            except:
                logger.error("consuming failed, after 1s start_consuming again!")
                logger.error("Exception:", exc_info=True)
                time.sleep(1)

    def replace(self, old_queue, new_queue, callback):
        """
        @summary: 会停止所有consumer,重新订阅consume_info列表
        @param old_queue: str类型
        @param new_queue: str类型
        """
        try:
            del self.consume_info[old_queue]
            self.consume_info[new_queue] = callback
            self.ch.stop_consuming()
            for queue_name in self.consume_info:
                self.ch.queue_declare(queue=queue_name)
                self.ch.basic_consume(self.consume_info[queue_name], queue=queue_name, no_ack=True)
        except:
            logger.error("Exception:", exc_info=True)


if __name__ == "__main__":
    '''
    测试用例
    '''


    def callback(ch, method, properties, body):
        try:
            logger.info("Received: %r" % body)
        except:
            logger.error("callback failed")
            logger.error("Exception:", exc_info=True)


    rbclient = RabbitMQClient("192.168.1.87", 5673, "mq", "123456")
    rbclient.connect()
    rbclient_1 = RabbitMQClient("192.168.1.87", 5673, "mq", "123456")
    rbclient_1.connect()
    rbclient.consume("hello", callback)
    t = threading.Thread(target=rbclient.start_consuming, args=("noargs"))
    t.start()
    t1 = time.time()
    rbclient_1.publish("hello", "hello world!")
    rbclient_1.publish("hello", "hello world!")
    rbclient_1.publish("hello", "hello world!")
    time.sleep(10)
    print("--------relace------")
    rbclient.replace("hello", "hello1", callback)
    print("--------relace end------")
    while True:
        print("while publish")
        rbclient_1.publish("hello1", "hello1 world1!")
        rbclient_1.publish("hello", "hello world!")
        time.sleep(1)