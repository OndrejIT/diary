# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2016-2017

# https://github.com/kyokenn/djradicale/blob/master/djradicale/views.py


import logging

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from radicale import Application, config


class ApplicationResponse(HttpResponse):
	def start_response(self, status, headers):
		self.status_code = int(status.split(' ')[0])
		for k, v in dict(headers).items():
			self[k] = v


class RadicaleView(Application, View):
	http_method_names = [
		"delete",
		"get",
		"head",
		"mkcalendar",
		"mkcol",
		"move",
		"options",
		"propfind",
		"proppatch",
		"put",
		"report",
	]

	def __init__(self, **kwargs):

		configuration = config.load(extra_config=settings.RADICALE_CONFIG)
		logger = logging.getLogger("diary")

		super(RadicaleView, self).__init__(configuration, logger)
		super(View, self).__init__(**kwargs)

	def _read_raw_content(self, environ):
		return environ["_body"]

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		environ = request.META
		environ["_body"] = request.body
		if not request.method.lower() in self.http_method_names:
			return self.http_method_not_allowed(request, *args, **kwargs)
		response = ApplicationResponse()
		answer = self(environ, response.start_response)
		for i in answer:
			response.write(i)
		return response
