from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.http.response import HttpResponse
from .models import *
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.db.models import Q
from .fortify_run import push, git_api
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from .info import information
import hashlib
import pymysql
from celery.decorators import task
from lib.config_json import *


@permission_required("audit.display_projects")
def display_project(request):
    keyword = request.GET.get("keyword")
    try:
        page = int(request.GET.get("page")) or 1
    except:
        page = 1
    try:
        limit = int(request.GET.get("limit")) or 10
    except:
        limit = 10

    start = (page - 1) * limit
    end = page * limit
    if keyword == None:
        results = proj_info.objects.all()[start:end]
        project_count = proj_info.objects.all().count()
    else:
        results = proj_info.objects.filter(name__icontains=keyword)[start:end]
        project_count = proj_info.objects.filter(name__icontains=keyword).count()
    return render(request, "audit/projects.html", locals())


@permission_required("audit.display_info")
def project_info(request):
    token = request.GET.get("token")
    id = request.GET.get('id')
    proj = proj_info.objects.get(token=token)
    risks = vul_info.objects.filter(proj_id=id).values('risk').annotate(Count('risk'))
    low_risk = 0
    Medium_risk = 0
    High_risk = 0
    Critical_risk = 0
    for i in range(len(risks)):
        if risks[i]['risk'] == 'Low':
            low_risk = risks[i]['risk__count']
        if risks[i]['risk'] == 'Medium':
            Medium_risk = risks[i]['risk__count']
        if risks[i]['risk'] == 'High':
            High_risk = risks[i]['risk__count']
        if risks[i]['risk'] == 'Critical':
            Critical_risk = risks[i]['risk__count']
    vuls = vul_info.objects.values('title').annotate(Count('title'))  # 所有漏洞标题
    critical_title = vul_info.objects.filter(proj_id=id).filter(Q(risk='Critical') | Q(risk='High')).values(
        'title').annotate(Count('title'))  # 严重和高危漏洞标题
    # vul_title = vul_info.objects.filter(proj_id=id).values('title').annotate(Count('title'))  # 所有漏洞标题
    return render(request, "audit/info.html", locals())


@permission_required("audit.vullist")
@csrf_exempt
def vullist(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        results = vul_info.objects.filter(proj_id=id)
        r = vul_info.objects.values('title').distinct()
        rule_filter = []
        for i in r:
            rule_filter.append(i['title'])
        vul_information = []
        for vul in results:
            vul_information.append({
                'line_number': vul.LineStart,
                'file_path': vul.FilePath,
                'level': vul.risk,
                'rule_name': vul.title,
                'language': vul.extend,
                'describe': information(vul.title)['describe'],
                'Recommendation': information(vul.title)['Recommendation'],
            })

        return JsonResponse({
            'code': 1001,
            'result': {
                'scan_data': {'extension': 21,
                              'language': 'php',
                              'trigger_rules': 12,
                              'vulnerabilities': vul_information,
                              'target_directory': '',
                              'push_rules': 12,
                              'framework': 'unkonw',
                              'file': 213
                              },
                'rule_filter': rule_filter,
            }}, safe=False)
    else:
        return HttpResponse('must be post method ')


@permission_required("audit.vuldetail")
@csrf_exempt
def vuldetail(request):
    id = request.POST.get('id')
    vid = request.POST.get('vid')
    code = vul_info.objects.filter(proj_id=id).get(vid=vid).full_code
    extend = vul_info.objects.filter(proj_id=id).get(vid=vid).extend
    return JsonResponse({
        'code': 1001,
        'result': {
            'file_content': code,
            'extension': extend,
        }
    })


@permission_required("audit.delelte_project")
@csrf_exempt
def api_proj_del(request):
    ids = request.POST.getlist('ids')
    for id in ids:
        vul_info.objects.filter(proj_id=id).delete()
        proj_info.objects.filter(id=id).delete()

    return JsonResponse({
        'code': 1001,
        'msg': '删除成功'
    })


@csrf_exempt
@permission_required('audit.upload_code_and_scan')
def scan(request):
    if request.method == 'POST':
        t = request.POST.get('type')
        if (t == "1"):
            gitaddress = request.POST.get("git_address")
            gitbranch = request.POST.get("git_branch")
            gitaccount = request.POST.get("git_username")
            gitpwd = request.POST.get("git_password")
            if "@" in gitaccount:
                atNum = gitaccount.find("@")
                gitaccount = gitaccount[0:atNum]
            if len(gitaddress.strip()) == 0 or len(gitbranch.strip()) == 0:
                return JsonResponse({"status": 0, "msg": "请输入地址和分支！"})
            elif len(gitaccount.strip()) == 0 or len(gitpwd.strip()) == 0:
                return JsonResponse({"status": 0, "msg": "请输入账号和密码！"})
            else:
                if ('.git' not in gitaddress):
                    gitaddress += '.git'

                if "https://" in gitaddress:
                    tmp = "https://" + gitaccount.replace("@", "%40") + ":" + gitpwd.replace("@", "%40") + "@"
                    address = gitaddress.replace("https://", tmp)
                    push.delay(gitaddress=address, gitbranch=gitbranch)
                    return JsonResponse({"code": 1000, "msg": "开始扫描"})
                elif "http://" in gitaddress:
                    tmp = "http://" + gitaccount.replace("@", "%40") + ":" + gitpwd.replace("@", "%40") + "@"
                    address = gitaddress.replace('http://', tmp)
                    push.delay(gitaddress=address, gitbranch=gitbranch)
                    return JsonResponse({"code": 1000, "msg": "开始扫描"})
                else:
                    return JsonResponse({"status": 0, "msg": "信息有误！"})
        else:
            return JsonResponse({"status": 0, "msg": "参数类型错误"})
    else:
        address = GIT_ADDRESS
        p = GIT_PARM
        choice = GIT_API_CHOICE
        filepath = GIT_PATH
        return render(request, "audit/scan.html", locals())


@permission_required("audit.restart_scan")
@csrf_exempt
def restart(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        try:
            type = proj_info.objects.get(id=id).type
            if type == 1:
                git = proj_info.objects.get(id=id).git
                push.delay(gitaddress=git)

            elif type == 3:
                svn = proj_info.objects.get(id=id).svn
                push.delay(svnaddress=svn)
            elif type == 4:
                return JsonResponse({"code": 8888, "msg": "该项目是压缩上传，请重新上传压缩文件进行扫描"})
            else:
                return JsonResponse({"code": 9999, "msg": "项目类型未知，无法重新扫描。"})

        except:
            return JsonResponse({"code": 1000, "msg": "内容错误！"})
        return JsonResponse({"code": 1001, "msg": "开始扫描！"})
    else:
        return JsonResponse({"code": 1111, "msg": "请求方式必须为POST！"})


@permission_required("audit.filter_vul")
def filter_vul(request):
    results = vul_info.objects.all()
    for i in results:
        # if i.risk =='Critical':
        # if any(t  in i.title for t in filter_title):
        m = i.title.replace('\n', '') + i.FileName.replace('\n', '') + i.LineStart.replace('\n',
                                                                                           '') + i.FilePath.replace(
            '\n', '')  # md5的明文
        md5 = hashlib.md5()
        md5.update(m.encode("utf8"))
        md5 = md5.hexdigest()
        vul_name = i.title
        FilePath = i.FilePath
        Abstract = i.Abstract
        FileName = i.FileName
        LineStart = i.LineStart
        info = information(vul_name)
        describe = info['describe']
        Recommendation = info['Recommendation']
        proj_name = proj_info.objects.get(id=i.proj_id.id).name
        if len(chandao_data.objects.filter(md5=md5)) == 0:
            chandao_data.objects.create(
                md5=md5,
                vul_name=vul_name,
                FilePath=FilePath,
                Abstract=Abstract,
                FileName=FileName,
                describe=describe,
                Recommendation=Recommendation,
                LineStart=LineStart,
                proj_name=proj_name,
            )
    return JsonResponse({"code": 1001, "msg": "过滤漏洞成功"})
