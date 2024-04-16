from django.contrib import admin

from .models import Subscribers, User


class UserAdmin(admin.ModelAdmin):
    """Отображение модели User в админ части сайта."""

    list_display = (
        'email',
        'first_name',
        'username',
        'is_staff'
    )
    exclude = ['password']
    search_fields = ('username', 'email', 'first_name')
    list_filter = ('is_superuser', 'is_staff', 'email', 'username',)


class SubscribersAdmin(admin.ModelAdmin):

    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')


admin.site.register(Subscribers, SubscribersAdmin)
admin.site.register(User, UserAdmin)
