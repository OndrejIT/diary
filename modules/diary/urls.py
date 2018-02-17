# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2016


from django.conf.urls import url

from .views import RadicaleView

app_name = "diary"


urlpatterns = [
    url(r"^(?P<url>.*)$", RadicaleView.as_view(), name="application"),
]
