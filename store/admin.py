from django.contrib import admin
from django.contrib.admin import ModelAdmin

from store.models import Book, RelationUserBook


# Register your models here.
@admin.register(Book)
class BookAdmin(ModelAdmin):
    pass

@admin.register(RelationUserBook)
class RelationUserBookAdmin(ModelAdmin):
    pass
