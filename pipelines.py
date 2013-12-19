import os
from urllib2 import urlopen, HTTPError

from django.conf import settings
from django.template.defaultfilters import slugify

from social_auth.backends.facebook import FacebookBackend
from social_auth.backends.google import GoogleOAuth2Backend

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile


def get_user_avatar(backend, details, response, social_user, uid,\
					user, *args, **kwargs):
	url = None
	if backend.__class__ == FacebookBackend:
		url = "http://graph.facebook.com/%s/picture?type=large" % response['id']

	if url:
		try:
			profile = user.profile
			filename = slugify(user.username + " social") + '.jpg'
			img_temp = NamedTemporaryFile(delete=True)
			img_temp.write(urlopen(url).read())
			img_temp.flush()

			profile.profile_photo.save(filename, File(img_temp))
			profile.save()
		except HTTPError:
			print 'pasmo'
			pass