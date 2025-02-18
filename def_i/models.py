from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from taggit.managers import TaggableManager
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from django.shortcuts import resolve_url
from def_init.secret_settings import *
import requests

User = get_user_model()

class Course(models.Model): #lesson
    title = models.CharField(max_length=30)
    course_num = models.PositiveSmallIntegerField(default=0)
    is_clear = models.BooleanField(default=False) #is_clear

    def __str__(self):
        return str(self.title)

class Lesson(models.Model):
    title = models.CharField(max_length=30)
    contents = models.TextField(max_length=1000, null=True)
    lesson_num = models.PositiveSmallIntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lesson") #lesson
    clear = models.BooleanField(default=False)


    def __str__(self):
        return str(self.title)


class Article(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_article")
    article_at = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="lesson_article")
    title = models.CharField(max_length=30)
    content = MarkdownxField()
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    tags = TaggableManager(blank=True)
    # 画像を添付する場合
    # article_image = models.ImageField(upload_to="def_i/img",null=True)
    # article_image_resize = ImageSpecField(source='user_image',
    # processors=[ResizeToFill(250,250)],
    # format='JPEG',
    # options={'quality':60})
    # def __str__(self):
    #     return self.title

    def formatted_markdown(self):
        return markdownify(self.content)

class Question(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_question")
    question_at = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="lesson_question")
    title = models.CharField(max_length=30)
    # content = models.TextField(null=True)
    content = MarkdownxField()
    if_answered = models.BooleanField(default=False) #->is_answered
    created_at = models.DateTimeField(default=timezone.now)
    tags = TaggableManager(blank=True)

    # def __str__(self):
    #     return str(self.title)+" by "+str(self.poster)

    def browser_push(self,request):
        data = {
            'app_id':'ea35df03-ba32-4c85-9f7e-383106fb1d24',
            'safari_web_id': "web.onesignal.auto.47a2f439-afd3-4bb7-8cdd-92cc4f5ee46c",
            'included_segments': ['All'],
            'contents': {'en': self.title},
            'headings': {'en': '新しい質問が投稿されました！質問に答えましょう．'},
            'url': resolve_url('question_feed_new'),
        }
        requests.post(
            "https://onesignal.com/api/v1/notifications",
            headers={'Authorization': ONESIGNAL_SECRET_KEY},
            json=data,
        )

    def formatted_markdown(self):
        return markdownify(self.content)

class Like(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

CATEGORY_CHOICE = (
    ('記事','記事'),
    ('質問','質問'),
)

class Talk(models.Model):
    msg = models.TextField(max_length=1000)
    msg_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_form")
    msg_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_to")
    time = models.DateTimeField(auto_now_add=True)
    # def __str__(self):
    #     return "{}から{}へのメッセージ".format(self.msg_from,self.msg_to)

class TalkAtArticle(Talk):
    msg_at = models.ForeignKey(Article, on_delete=models.CASCADE)
    category = models.CharField(max_length=10,
        choices=CATEGORY_CHOICE, default='記事')

    # def __str__(self):
    #     return "FROM '{}' TO '{}' AT '{}'".format(self.msg_from,self.msg_to,self.msg_at)

    # initがUnion時に走ってしまうため，使えない
    # def __init__(self,*args,**kwargs):
    #     super(TalkAtArticle,self).__init__(*args,**kwargs)
    #     self.category = '記事'

class TalkAtQuestion(Talk):
    msg_at = models.ForeignKey(Question, on_delete=models.CASCADE)
    category = models.CharField(max_length=10,
        choices=CATEGORY_CHOICE, default='質問')

    def __str__(self):
        return "FROM '{}' TO '{}' AT '{}'".format(self.msg_from,self.msg_to,self.msg_at)

    # def __init__(self,*args,**kwargs):
    #     super(TalkAtQuestion,self).__init__(*args,**kwargs)
    #     self.category = '質問'

class Memo(models.Model):
    relate_lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="lesson_memo", null=True)
    relate_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_memo", null=True)
    contents = models.TextField(null=True)
