from unittest import TestCase
from django.contrib.auth.models import User

from store.models import Book, RelationUserBook
from store.utils import set_rating


class UtilsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='jeronimo_a',
                                        first_name='Mike',
                                        last_name='Tyson'
                                        )
        self.user_2 = User.objects.create(username='jeronimo_b',
                                          first_name='Tyler',
                                          last_name='Jones'
                                          )
        self.user_3 = User.objects.create(username='jeronimo_c',
                                          first_name='Matt',
                                          last_name='Groening'
                                          )
        self.book_1 = Book.objects.create(name='Test_book1', price=800, discount=100,
                                          author='Author_1', master=self.user_3)

        RelationUserBook.objects.create(user=self.user, book=self.book_1, like=True, rating=5)
        RelationUserBook.objects.create(user=self.user_2, book=self.book_1, like=True, rating=5)
        RelationUserBook.objects.create(user=self.user_3, book=self.book_1, like=True, rating=4)

    def test_set_rating(self):
        set_rating(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual('4.67', str(self.book_1.rate))
