from django.contrib import admin
from user.models import *


class UserAdmin(admin.ModelAdmin):
    pass

admin.site.register(AuthUser, UserAdmin)
