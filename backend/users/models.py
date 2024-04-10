from django.contrib.auth.models import AbstractUser
from django.db import models

LENGTH: int = 150


class User(AbstractUser):
    """Модель пользователя."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]
    username = models.CharField('Логин', max_length=LENGTH, unique=True)
    email = models.EmailField('Почта', unique=True, max_length=254)
    first_name = models.CharField('Имя', max_length=LENGTH)
    last_name = models.CharField('Фамилия', max_length=LENGTH)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
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
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        unique_together = [['user', 'author']]
