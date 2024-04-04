from django.contrib import admin

from .models import User, Subscribers


class UserAdmin(admin.ModelAdmin):
    """Отображение модели User в админ части сайта."""

    list_display = (
        'username',
        'is_superuser',
        'is_staff'
    )
    list_editable = (
        'is_staff',
    )
    search_fields = ('username', 'email',)
    list_filter = ('is_superuser', 'is_staff', 'email', 'username',)


class SubscribersAdmin(admin.ModelAdmin):

    list_display = ('user', 'author')


admin.site.register(Subscribers, SubscribersAdmin)
admin.site.register(User, UserAdmin)
