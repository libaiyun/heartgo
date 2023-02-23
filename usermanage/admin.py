from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

ADDITIONAL_FIELDSETS = ((None, {"fields": ("nickname", "phone")}),)


@admin.register(get_user_model())
class MyUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ADDITIONAL_FIELDSETS
    add_fieldsets = UserAdmin.add_fieldsets + ADDITIONAL_FIELDSETS
