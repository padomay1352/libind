from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Boards)
admin.site.register(BoardCategories)
admin.site.register(BoardReplies)
admin.site.register(BoardLikes)
