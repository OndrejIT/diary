# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2016


from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.static import serve

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^static/(?P<path>.*)$", serve, kwargs=dict(document_root=settings.STATIC_ROOT)),
    url(r"^", include("modules.diary.urls")),
]

admin.site.site_header = "Calendar & Contacts"
admin.site.site_title = "Calendar & Contacts"
