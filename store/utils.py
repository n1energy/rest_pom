from django.db.models import Avg

from store.models import RelationUserBook


def set_rating(book):
    rating = RelationUserBook.objects.filter(book=book).aggregate(rating=Avg('rating')).get('rating')
    book.rate = rating
    book.save()
