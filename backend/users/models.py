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
    password = models.CharField('Пароль', max_length=LENGTH, blank=True)
    email = models.EmailField('Почта', unique=True)
    first_name = models.CharField('Имя', max_length=LENGTH)
    last_name = models.CharField('Фамилия', max_length=LENGTH)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> models.CharField:
        return self.username


class Subscribers(models.Model):
    user = models.ForeignKey(
        User,
        related_name='subscriptions',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='subscribers',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = [['user', 'author']]
