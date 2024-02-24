from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    """Отображение модели User в админ части сайта."""

    list_display = (
        'username',
        'first_name',
        'last_name',
        'role',
        'is_superuser',
    )
    list_editable = (
        'role',
    )
    search_fields = ('username',)
    list_filter = ('role', 'is_superuser')


admin.site.register(User, UserAdmin)
