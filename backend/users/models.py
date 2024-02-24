from django.contrib.auth.models import AbstractUser
from django.db import models

USER_ROLES = (
    ('user', 'Пользователь'),
    ('admin', 'Администратор'),
)

LENGTH: int = 64

class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField('Логин', max_length=LENGTH, unique=True)
    password = models.CharField('Пароль', max_length=128, blank=True)
    email = models.EmailField('Почта', unique=True)
    first_name = models.CharField('Имя', max_length=LENGTH)
    last_name = models.CharField('Фамилия', max_length=LENGTH)
    role = models.CharField(
        max_length=LENGTH,
        default='user',
        choices=USER_ROLES
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self) -> bool:
        return self.role == 'admin'

    def __str__(self) -> models.CharField:
        return self.username
