from django.test import TestCase
import subprocess
from lib.config_json import *

gitaddress = "https://gitlab.emotibot.com/honeycomb/emotion-engine-dal"
gitbranch = "master"
gitaccount = "lingyingliu"
gitpwd = "Aa785412369"
gitaddname = ''

if ('.git' in gitaddress):
    gitaddname = gitaddress.replace('.git', '')
else:
    gitaddress += '.git'

print(gitaddname,gitaddress)
