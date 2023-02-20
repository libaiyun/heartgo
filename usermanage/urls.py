from django.urls import re_path

from usermanage import views

urlpatterns = [
    re_path(r"^user/list/$", views.list_users)
]
