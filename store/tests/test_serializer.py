import json

from django.contrib.auth.models import User
from django.test import TestCase

from store.models import Book, RelationUserBook
from store.serializers import BooksSerializer


class SerializersTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="jeronimo")
        self.user_2 = User.objects.create(username="jeronimo_2")
        self.user_3 = User.objects.create(username="jeronimo_3")
        self.book_1 = Book.objects.create(name='Test_book1', price=800,
                                          author='Author_1',)
        self.book_2 = Book.objects.create(name='Test_book2', price=200,
                                          author='Author_5')
        self.book_3 = Book.objects.create(name='Test_book2 Author_1', price=200,
                                          author='Author_2')

        RelationUserBook.objects.create(user=self.user, book=self.book_1, like=True)
        RelationUserBook.objects.create(user=self.user_2, book=self.book_1, like=True)
        RelationUserBook.objects.create(user=self.user_3, book=self.book_1, like=True)

    def test_book_serializer(self):
        data = BooksSerializer([self.book_1, self.book_2], many=True).data
        expected_data = [
            {
                "id": self.book_1.id,
                "name": "Test_book1",
                "price": "800.00",
                "author": "Author_1",
                "like_count": 3,
            },
            {
                "id": self.book_2.id,
                "name": "Test_book2",
                "price": "200.00",
                "author": "Author_5",
                "like_count": 0,
            }
        ]
        json_data = json.dumps(data)
        print(type(expected_data)
        print(json_data)
        self.assertEqual(json_data, expected_data)
