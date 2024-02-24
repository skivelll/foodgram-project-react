from django.contrib.auth.models import AbstractUser
from django.db import models

USER_ROLES = (
    ('user', 'Пользователь'),
    ('admin', 'Администратор'),
)


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField('Логин', unique=True)
    password = models.CharField('Пароль', max_length=128, blank=True)
    email = models.EmailField('Почта', unique=True)
    first_name = models.CharField('Имя')
    last_name = models.CharField('Фамилия')
    role = models.CharField(
        max_length=50, default='user', choices=USER_ROLES
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self) -> bool:
        return self.role == 'admin'

    def __str__(self) -> str:
        return self.username
