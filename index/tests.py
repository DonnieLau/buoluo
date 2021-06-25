from django.test import TestCase

# Create your tests here.

a = "https://gitlab.emotibot.com/chat/x-chat"
print(a.split('/')[-1].replace('.git', ''))