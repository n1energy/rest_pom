from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import  IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from store.models import Book
from store.permissions import IsMasterOrReadOnly
from store.serializers import BooksSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
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

class UserBookRelationView(
    
):