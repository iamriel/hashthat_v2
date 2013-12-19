from django.contrib.auth.models import User
from django.db import models

from autoslug import AutoSlugField


class Comment(models.Model):
    comment = models.TextField()
    author = models.ForeignKey(User)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.comment

    @property
    def owner_name(self):
        return self.author.username
    

class Hashtag(models.Model):
    tag = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(User)
    comments = models.ManyToManyField(Comment, blank=True, null=True)

    up_vote = models.ManyToManyField(User, related_name='up_votes', blank=True, null=True)
    down_vote = models.ManyToManyField(User, related_name='down_votes', blank=True, null=True)

    slug = AutoSlugField(populate_from=lambda instance: instance.tag,
        unique_with=['tag'],
        slugify=lambda value: value.replace(' ','-'))

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'#%s' % self.tag

    @property
    def owner_name(self):
        return self.author.username

    @property
    def comment_count(self):
        return self.comments.all().count()

    @property
    def votes(self):
        up_votes = self.up_vote.all().count()
        down_votes = self.down_vote.all().count()
        return up_votes - down_votes


