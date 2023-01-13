from django.db.models import Count, When, Case, Avg
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from store.models import Book, RelationUserBook
from store.permissions import IsMasterOrReadOnly
from store.serializers import BooksSerializer, RelationUserBookSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all().annotate(
            annotated_likes=(Count(Case(When(relationuserbook__like=True, then=1)))),
            rating=Avg('relationuserbook__rating')).order_by('id')
    serializer_class = BooksSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsMasterOrReadOnly]
    search_fields = ['author', 'name', 'price']
    filterset_fields = ('price',)
    ordering_fields = ['price', 'author']

    def perform_create(self, serializer):
        serializer.validated_data['master'] = self.request.user
        serializer.save()


def auth(request):
    return render(request, 'oauth.html')


class UserBookRelationView(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = RelationUserBook.objects.all()
    serializer_class = RelationUserBookSerializer
    lookup_field = 'book'

    def get_object(self):
        obj, _ = RelationUserBook.objects.get_or_create(user=self.request.user, book_id=self.kwargs['book'])
        return obj
