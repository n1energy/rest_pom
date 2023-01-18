from django.contrib.auth.models import User
from rest_framework import serializers

from store.models import Book, RelationUserBook
from rest_framework.serializers import ModelSerializer


class ReadersSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class BooksSerializer(ModelSerializer):
    annotated_likes = serializers.IntegerField(read_only=True)
    annotated_bookmarks = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    max_rating = serializers.IntegerField(read_only=True)
    min_rating = serializers.IntegerField(read_only=True)
    master_name = serializers.CharField(read_only=True)
    readers = ReadersSerializer(many=True, read_only=True)
    price_after_discount = serializers.DecimalField(max_digits=7, decimal_places=2, read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'price', 'price_after_discount', 'author', 'annotated_likes', 'annotated_bookmarks',
                  'rating', 'max_rating', 'min_rating', 'master_name', 'readers')

    # def get_like_count(self, instance):
    #     return RelationUserBook.objects.filter(book=instance, like=True).count()


class RelationUserBookSerializer(ModelSerializer):
    class Meta:
        model = RelationUserBook
        fields = ('book', 'like', 'bookmark', 'rating', 'review')
