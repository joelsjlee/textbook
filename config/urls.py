'''
###################### NOT BEING USED ######################
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from titlecase import titlecase
import os


# Format the text file name
def format_text_name(text_name):
    text_name = text_name.replace("_", " ")
    text_name = text_name.replace("-", " ")
    return titlecase(text_name)


# Get the text information for display
def get_text_info_list():
    text_info_list = []
    text_dir_names = os.listdir("../app/proxy/templates/proxy/texts")
    for text_dir_name in text_dir_names:
        text_info = []  # holds [{raw file name}, {formatted file name}]
        text_info.append(text_dir_name)
        text_info.append(format_text_name(text_dir_name))
        text_info_list.append(text_info)
    return text_info_list


urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), {'text_info_list': get_text_info_list()}, name="home"),
    # path("", views.home, name="home"),
    path("about/", TemplateView.as_view(template_name="pages/about.html"), name="about"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("static_page_proxy.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path("", include("proxy.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
'''
