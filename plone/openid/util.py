from plone.openid import django_random


def GenerateSecret(length=16):
	return django_random.get_random_string(length)
