# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2016


from django.conf import settings
from django.conf.urls import include
from django.urls import path, re_path
from django.contrib import admin
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(r"^static/(?P<path>.*)$", serve, kwargs=dict(document_root=settings.STATIC_ROOT)),
    path("", include("modules.diary.urls")),
]

admin.site.site_header = "Calendar & Contacts"
admin.site.site_title = "Calendar & Contacts"
