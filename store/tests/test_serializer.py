from django.contrib.auth.models import User
from django.test import TestCase

from store.models import Book
from store.serializers import BooksSerializer


class SerializersTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="jeronimo")
        self.book_1 = Book.objects.create(name='Test_book1', price=800,
                                          author='Author_1', master=self.user)
        self.book_2 = Book.objects.create(name='Test_book2', price=200,
                                          author='Author_5')
        self.book_3 = Book.objects.create(name='Test_book2 Author_1', price=200,
                                          author='Author_2')
    def test_book_serializer(self):
        data = BooksSerializer([self.book_1, self.book_2], many=True).data
        print(data)
        expected_data = [
            {
                'id': self.book_1.id,
                'name': 'Test_book1',
                'price': '800.00',
                'author': '',
                'master': self.book_1.master.id
            },
            {
                'id': self.book_2.id,
                'name': 'Test_book2',
                'price': '200.00',
                'author': '',
                'master': self.book_2.master.id
            }
        ]
        self.assertEqual(expected_data, data)
