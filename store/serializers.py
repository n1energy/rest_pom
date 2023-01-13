from rest_framework import serializers

from store.models import Book, RelationUserBook
from rest_framework.serializers import ModelSerializer


class BooksSerializer(ModelSerializer):
    like_count = serializers.SerializerMethodField()
    annotated_likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'price', 'author', 'like_count', 'annotated_likes',
                  'rating')

    def get_like_count(self, instance):
        return RelationUserBook.objects.filter(book=instance, like=True).count()


class RelationUserBookSerializer(ModelSerializer):
    class Meta:
        model = RelationUserBook
        fields = ('book', 'like', 'bookmark', 'rating', 'review')
