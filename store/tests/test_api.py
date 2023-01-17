import json

from django.contrib.auth.models import User
from django.db.models import Count, When, Case, Avg, Max, Min, F
from django.test.utils import CaptureQueriesContext
from django.db import connection
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from rest_framework.views import status

from rest_framework.viewsets import reverse

from store.models import Book, RelationUserBook
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username="jeronimo")
        self.book_1 = Book.objects.create(name='Test_book1', price=800,
                                          author='Author_1', master=self.user)
        self.book_2 = Book.objects.create(name='Test_book2', price=200,
                                          author='Author_5')
        self.book_3 = Book.objects.create(name='Test_book3', price=300,
                                          author='Author_1')
        RelationUserBook.objects.create(user=self.user, book=self.book_1, like=True, rating=5)

    def test_get(self):
        url = reverse('book-list')
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            self.assertEqual(2, len(queries))
        books = Book.objects.all().annotate(
            annotated_bookmarks=(Count(Case(When(relationuserbook__bookmark=True, then=1)))),
            annotated_likes=(Count(Case(When(relationuserbook__like=True, then=1)))),
            rating=Avg('relationuserbook__rating'),
            min_rating=Min('relationuserbook__rating'),
            max_rating=Max('relationuserbook__rating'),
            price_after_discount=F('price') - F('discount'),
        ).order_by('id')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data[0]['rating'], '5.00')
        self.assertEqual(serializer_data[0]['annotated_likes'], 1)
        self.assertEqual(serializer_data[0]['annotated_bookmarks'], 0)

    def test_get_pk(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        response = self.client.get(url)
        books = Book.objects.filter(id__in=[self.book_1.id]).annotate(
            annotated_bookmarks=(Count(Case(When(relationuserbook__bookmark=True, then=1)))),
            annotated_likes=(Count(Case(When(relationuserbook__like=True, then=1)))),
            rating=Avg('relationuserbook__rating'),
            min_rating=Min('relationuserbook__rating'),
            max_rating=Max('relationuserbook__rating'),
            price_after_discount=F('price') - F('discount'),
        ).order_by('id')
        serializer_data = BooksSerializer(books, many=True).data[0]
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_search(self):
        url = reverse('book-list')
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_3.id]).annotate(
            annotated_bookmarks=(Count(Case(When(relationuserbook__bookmark=True, then=1)))),
            annotated_likes=(Count(Case(When(relationuserbook__like=True, then=1)))),
            rating=Avg('relationuserbook__rating'),
            min_rating=Min('relationuserbook__rating'),
            max_rating=Max('relationuserbook__rating'),
            price_after_discount=F('price') - F('discount'),
        ).order_by('id')
        response = self.client.get(url, data={'search': 'Author_1'})
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_filter(self):
        url = reverse('book-list')
        books = Book.objects.filter(id=self.book_2.id).annotate(
            annotated_bookmarks=(Count(Case(When(relationuserbook__bookmark=True, then=1)))),
            annotated_likes=(Count(Case(When(relationuserbook__like=True, then=1)))),
            rating=Avg('relationuserbook__rating'),
            min_rating=Min('relationuserbook__rating'),
            max_rating=Max('relationuserbook__rating'),
            price_after_discount=F('price') - F('discount'),
        ).order_by('id')
        response = self.client.get(url, data={'price': 200})
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_ordering(self):
        url = reverse('book-list')
        books = Book.objects.all().annotate(
            annotated_bookmarks=(Count(Case(When(relationuserbook__bookmark=True, then=1)))),
            annotated_likes=(Count(Case(When(relationuserbook__like=True, then=1)))),
            rating=Avg('relationuserbook__rating'),
            min_rating=Min('relationuserbook__rating'),
            max_rating=Max('relationuserbook__rating'),
            price_after_discount=F('price') - F('discount'),
        ).order_by('price')
        response = self.client.get(url, data={'ordering': 'price'})
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            "name": "Python 3",
            "price": 150,
            "author": "Mark Summerfield"
        }
        self.client.force_login(self.user)
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(Book.objects.last().master, self.user)

    def test_update_not_master_but_staff(self):
        self.user2 = User.objects.create(username='test_username2', is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 400,
            "author": self.book_1.author
        }
        self.client.force_login(self.user2)
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(400, self.book_1.price)

    def test_update_not_master(self):
        self.user2 = User.objects.create(username='test_username2', )
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 400,
            "author": self.book_1.author
        }
        self.client.force_login(self.user2)
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')},
                         response.data)
        self.book_1.refresh_from_db()
        self.assertEqual(800, self.book_1.price)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 400,
            "author": self.book_1.author
        }
        self.client.force_login(self.user)
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(400, self.book_1.price)

    def test_delete(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url, content_type='application/json')
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Book.objects.all().count())


class RelationBookTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username="jeronimo")
        self.user2 = User.objects.create(username="test_username2")
        self.book_1 = Book.objects.create(name='Test_book1', price=800,
                                          author='Author_1', master=self.user)
        self.book_2 = Book.objects.create(name='Test_book2', price=200,
                                          author='Author_5')

    def test_like(self):
        url = reverse('relationuserbook-detail', args=(self.book_1.id,))
        data = {
            "like": True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = RelationUserBook.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.like)

        data = {
            "bookmark": True,
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = RelationUserBook.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.bookmark)

    def test_rating(self):
        url = reverse('relationuserbook-detail', args=(self.book_1.id,))
        data = {
            "rating": 5,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = RelationUserBook.objects.get(user=self.user, book=self.book_1.id)
        print(relation)
        self.assertEqual(5, relation.rating)

    def test_rating_wrong(self):
        url = reverse('relationuserbook-detail', args=(self.book_1.id,))
        data = {
            "rating": 8,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)

    def test_review(self):
        url = reverse('relationuserbook-detail', args=(self.book_1.id,))
        data = {
            'review': 'very cool book bro, must read it',
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = RelationUserBook.objects.get(user=self.user, book=self.book_1)
        self.assertIsNotNone(relation.review)
