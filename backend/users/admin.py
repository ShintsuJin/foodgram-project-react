from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'id',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('email', 'username')
    search_fields = ('username', 'email')


admin.site.register(User, UserAdmin)
