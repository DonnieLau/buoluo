from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
# 只要是想在自己的脚本中访问Django的数据库等文件就必须配置Django的环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'buoluo.settings')
# 实例化
app = Celery('buoluo')

# 在Django配置文件中对Celery进行配置
app.config_from_object('django.conf:settings')
# 自动从Django的已注册app中发现任务
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
# 并发数
app.conf.CELERYD_CONCURRENCY = 6


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
