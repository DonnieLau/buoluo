from django.urls import path

from .views import *

urlpatterns = [
    path('overview/', overview, name='index_overview'),
    path('', base, name='index_base'),
    path('login/', login, name='index_login'),
    path('register_action/', register_action),  # 注册行为
    path('logout/', logout, name='index_logout'),
]

handler403 = permission_denied
