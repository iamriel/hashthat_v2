from django.contrib import admin

from .models import Hashtag, Comment

admin.site.register(Comment)
admin.site.register(Hashtag)
