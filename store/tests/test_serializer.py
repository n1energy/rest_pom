import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg, Max, Min, F
from django.test import TestCase

from store.models import Book, RelationUserBook
from store.serializers import BooksSerializer


class SerializersTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='jeronimo',
                                        first_name='Mike',
                                        last_name='Tyson'
                                        )
        self.user_2 = User.objects.create(username='jeronimo_2',
                                          first_name='Tyler',
                                          last_name='Jones'
                                          )
        self.user_3 = User.objects.create(username='jeronimo_3',
                                          first_name='Matt',
                                          last_name='Groening'
                                          )
        self.book_1 = Book.objects.create(name='Test_book1', price=800, discount=100,
                                          author='Author_1', master=self.user_3)
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
            annotated_bookmarks=(Count(Case(When(relationuserbook__bookmark=True, then=1)))),
            annotated_likes=(Count(Case(When(relationuserbook__like=True, then=1)))),
            rating=Avg('relationuserbook__rating'),
            min_rating=Min('relationuserbook__rating'),
            max_rating=Max('relationuserbook__rating'),
            price_after_discount=F('price') - F('discount'),
            master_name=F('master__username'),
            ).order_by('id')
        data = BooksSerializer(books, many=True).data
        expected_data = [
            {
                'id': self.book_1.id,
                'name': 'Test_book1',
                'price': '800.00',
                'price_after_discount': '700.00',
                'author': 'Author_1',
                'annotated_likes': 3,
                'annotated_bookmarks': 0,
                'rating': '4.00',
                'max_rating': 5,
                'min_rating': 3,
                'master_name': 'jeronimo_3',
                'readers': [
                    {
                        'first_name': 'Mike',
                        'last_name': 'Tyson',
                    },
                    {
                        'first_name': 'Tyler',
                        'last_name': 'Jones',
                    },
                    {
                        'first_name': 'Matt',
                        'last_name': 'Groening',
                    },
                ]
            },
            {
                'id': self.book_2.id,
                'name': 'Test_book2',
                'price': '200.00',
                'price_after_discount': '200.00',
                'author': 'Author_5',
                'annotated_likes': 0,
                'annotated_bookmarks': 0,
                'rating': None,
                'max_rating': None,
                'min_rating': None,
                'master_name': None,
                'readers': [],
            },
            {
                'id': self.book_3.id,
                'name': 'Test_book3',
                'price': '200.00',
                'price_after_discount': '200.00',
                'author': 'Author_2',
                'annotated_likes': 0,
                'annotated_bookmarks': 0,
                'rating': None,
                'max_rating': None,
                'min_rating': None,
                'master_name': None,
                'readers': [],
            }
        ]
        self.assertEqual(data, expected_data)
