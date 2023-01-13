import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase

from store.models import Book, RelationUserBook
from store.serializers import BooksSerializer


class SerializersTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="jeronimo")
        self.user_2 = User.objects.create(username="jeronimo_2")
        self.user_3 = User.objects.create(username="jeronimo_3")
        self.book_1 = Book.objects.create(name='Test_book1', price=800,
                                          author='Author_1', )
        self.book_2 = Book.objects.create(name='Test_book2', price=200,
                                          author='Author_5')
        self.book_3 = Book.objects.create(name='Test_book3', price=200,
                                          author='Author_2')

        RelationUserBook.objects.create(user=self.user, book=self.book_1, like=True, rating=5)
        RelationUserBook.objects.create(user=self.user_2, book=self.book_1, like=True, rating=3)
        RelationUserBook.objects.create(user=self.user_3, book=self.book_1, like=True)

        # RelationUserBook.objects.create(user=self.user, book=self.book_2, like=True)
        # RelationUserBook.objects.create(user=self.user_2, book=self.book_2, like=True)
        # RelationUserBook.objects.create(user=self.user_3, book=self.book_2, like=False)

    def test_book_serializer(self):
        books = Book.objects.all().annotate(
            annotated_likes=(Count(Case(When(relationuserbook__like=True, then=1)))),
            rating=Avg('relationuserbook__rating')).order_by('id')
        data = BooksSerializer(books, many=True).data
        expected_data = [
            {
                "id": self.book_1.id,
                "name": "Test_book1",
                "price": "800.00",
                "author": "Author_1",
                "like_count": 3,
                "annotated_likes": 3,
                "rating": '4.00',
            },
            {
                "id": self.book_2.id,
                "name": "Test_book2",
                "price": "200.00",
                "author": "Author_5",
                "like_count": 0,
                "annotated_likes": 0,
                "rating": None,
            },
            {
                "id": self.book_3.id,
                "name": "Test_book3",
                "price": "200.00",
                "author": "Author_2",
                "like_count": 0,
                "annotated_likes": 0,
                "rating": None
            }
        ]
        print(data)
        self.assertEqual(data, expected_data)
