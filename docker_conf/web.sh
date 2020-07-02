#!/bin/bash
/usr/bin/supervisord -c /etc/supervisor/supervisord.conf
supervisorctl start all
env >> /etc/default/locale
/etc/init.d/cron start
crontab ./spider_template/docker_conf/cronjob
/usr/bin/supervisord -c /etc/supervisor/supervisor.conf