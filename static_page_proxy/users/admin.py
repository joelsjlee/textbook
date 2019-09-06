from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from static_page_proxy.users.forms import UserChangeForm, UserCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (("User", {"fields": ("name", "is_student")}),) + auth_admin.UserAdmin.fieldsets
    list_display = ["username", "name", "is_superuser", "is_student"]
    search_fields = ["name"]
