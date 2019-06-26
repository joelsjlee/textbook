from django.urls import path
from django.contrib.auth import views
from django.conf.urls import url

from . import views
app_name = 'proxy'
urlpatterns = [
    path('<path:static_path>/', views.proxy, name='proxy'),
]
