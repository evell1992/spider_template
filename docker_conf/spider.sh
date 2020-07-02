#!/bin/bash
/usr/bin/supervisord -c /etc/supervisor/supervisord.conf
supervisorctl start all
/usr/bin/supervisord -c /etc/supervisor/supervisor.conf