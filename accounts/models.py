import os

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


def profile_photo_path(instance, filename):
	return os.path.join('images', 'profile_photo', str(instance.user.id), filename)


class UserProfile(models.Model):
	user = models.OneToOneField(User)
	middle_name = models.CharField(max_length=255, blank=True, null=True)
	profile_photo = models.ImageField(upload_to=profile_photo_path, blank=True)
	profile_photo_url = models.URLField(blank=True)

	@property
	def profile_picture(self):
		return self.profile_photo if self.profile_photo else settings.DEFAULT_PROFILE_PHOTO

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])