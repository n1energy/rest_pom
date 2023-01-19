import typing

from django.contrib.auth.models import User
from django.db import models

from store.choices import RATING_CHOICES


class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    discount = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    author = models.CharField(max_length=255, default='')
    master = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='slave_books')
    readers = models.ManyToManyField(User, through='RelationUserBook', related_name='reader_books')
    rate = models.DecimalField(max_digits=3, decimal_places=2, null=True, default=None)

    def __str__(self):
        return f'Id{self.id} {self.name}'


class RelationUserBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True)
    like = models.BooleanField(default=False)
    bookmark = models.BooleanField(default=False)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, null=True)
    review = models.CharField(max_length=256, default=False, null=True)

    def __str__(self):
        return f'{self.user.username}: {self.book.name}, Rate:{self.rating}'

    def save(self, *args, **kwargs):
        from store.utils import set_rating

        creating= not self.pk
        old_rating = self.rating
        super().save(*args, **kwargs)
        new_rating=self.rating
        if old_rating != new_rating or creating:
            set_rating(self.book)
