# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2016


from django.urls import re_path

from .views import DiaryView

app_name = "diary"


urlpatterns = [
    re_path(r"^(?P<url>.*)$", DiaryView.as_view(), name="application"),
]
