from django.contrib import admin
from .models import Shelter, Animal, AdoptionApplication

admin.site.register(Shelter)
admin.site.register(Animal)
admin.site.register(AdoptionApplication)