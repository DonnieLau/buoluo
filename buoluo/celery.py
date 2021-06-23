from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
# 只要是想在自己的脚本中访问Django的数据库等文件就必须配置Django的环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'buoluo.settings')
# app名字
app = Celery('buoluo')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.CELERYD_CONCURRENCY = 16


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
