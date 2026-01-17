from django.db import models
from django.contrib import admin
from .models import Shelter, Animal, AdoptionApplication, UserProfile

admin.site.register(Shelter)
admin.site.register(Animal)
admin.site.register(AdoptionApplication)


@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'animal_count')
    search_fields = ('name', 'address', 'phone')
    list_filter = ('name',)

    def animal_count(self, obj):
        return obj.animal_set.count()

    animal_count.short_description = 'Животных в приюте'


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'species_display',
        'breed',
        'age',
        'shelter',
        'is_available',
        'child_friendly',
        'compatibility_score_display'
    )
    list_filter = ('species', 'is_available', 'shelter', 'size_category')
    search_fields = ('name', 'breed', 'description')
    list_editable = ('is_available',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'shelter', 'species', 'breed', 'age', 'description')
        }),
        ('Характеристики', {
            'fields': ('size_category', 'child_friendly',
                       'other_pet_friendly', 'activity_level')
        }),
        ('Системные', {
            'fields': ('is_available', 'arrival_date')
        }),
    )

    def species_display(self, obj):
        return obj.get_species_display()

    species_display.short_description = 'Вид'

    def compatibility_score_display(self, obj):
        avg_score = obj.applications.aggregate(models.Avg('compatibility_score'))
        if avg_score['compatibility_score__avg']:
            return f"{avg_score['compatibility_score__avg']:.1f}%"
        return "—"

    compatibility_score_display.short_description = 'Совместимость'


@admin.register(AdoptionApplication)
class AdoptionApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'animal',
        'status',
        'compatibility_score',
        'created_at',
        'contact_info'
    )
    list_filter = ('status', 'created_at', 'animal__shelter')
    search_fields = ('full_name', 'email', 'phone', 'animal__name')
    list_editable = ('status',)
    date_hierarchy = 'created_at'

    def contact_info(self, obj):
        return f"{obj.email} | {obj.phone}"

    contact_info.short_description = 'Контакты'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'home_type',
        'has_children',
        'has_other_pets',
        'experience_years',
        'created_at'
    )
    list_filter = ('home_type', 'has_children', 'has_other_pets', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')
    fieldsets = (
        ('Пользователь', {
            'fields': ('user', 'phone')
        }),
        ('Условия жизни', {
            'fields': ('home_type', 'has_children', 'children_age',
                       'has_other_pets', 'other_pets_info', 'has_garden')
        }),
        ('Предпочтения', {
            'fields': ('pref_child_friendly', 'pref_pet_friendly',
                       'pref_activity_level', 'pref_size', 'daily_walk_time')
        }),
        ('Опыт', {
            'fields': ('experience_years', 'work_schedule')
        }),
    )