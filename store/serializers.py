from store.models import Book
from rest_framework.serializers import ModelSerializer

class BooksSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
