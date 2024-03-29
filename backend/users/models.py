from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


class User(AbstractUser):
    """User model."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
        null=False,
        max_length=254,
    )

    username = models.CharField(
        max_length=150,
        verbose_name='Логин',
        unique=True,
        null=False,
    )

    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        blank=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-id']
        constraints = [
            UniqueConstraint(
                fields=['email', 'username'],
                name='unique_user',
            )
        ]


class Subscribe(models.Model):
    """Model for subscribe."""
    user = models.ForeignKey(
        User,
        related_name='subscriber',
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='subscribing',
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'Пользователь {self.user} подписался на {self.author}'

    class Meta:
        ordering = ['-id']
        constraints = [
            UniqueConstraint(fields=['user', 'author'], name='unique_sub')
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
