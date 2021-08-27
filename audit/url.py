from django.urls import path

from .views import *

urlpatterns = [
    path('projects/', display_project, name='audit_display_project'),
    path('info', project_info, name='audit_project_info'),
    path('scan', scan, name='audit_scan'),
    path('filter_vul', filter_vul, name='audit_filter_vul'),
    path('api/proj_del', api_proj_del, name='audit_proj_del'),
    path('api/restart', restart, name='audit_audit_restart'),
    path('api/vullist', vullist, name='audit_vul_list'),
    path('api/vuldetail', vuldetail, name='audit_vul_detail'),

]
