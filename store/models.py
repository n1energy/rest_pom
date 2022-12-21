from django.contrib.auth.models import User
from django.db import models

from store.choices import RATING_COICES


class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author = models.CharField(max_length=255, default='')
    master = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='slave_books')
    readers = models.ManyToManyField(User, through='RelationUserBook', related_name='reader_books')

    def __str__(self):
        return f'Id{self.id} {self.name}'

class RelationUserBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True)
    like = models.BooleanField(default=False)
    bookmark = models.BooleanField(default=False)
    rating = models.PositiveSmallIntegerField(choices=RATING_COICES, null=True)
    review = models.CharField(max_length=256, default=False, null=True)

    def __str__(self):
        return f'{self.user.username}: {self.book.name}, Rate:{self.rating}'
