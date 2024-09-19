from django.contrib import admin
from .models import Profile, Following, ListName
# Register your models here.

admin.site.register(Profile)
admin.site.register(Following)
admin.site.register(ListName)