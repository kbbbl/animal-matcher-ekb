from django import forms

class AnimalSearchForm(forms.Form):
    # Форма поиска и фильтрации животных
    SPECIES_CHOICES = [
        ('', 'Все виды'),
        ('cat', 'Кошки'),
        ('dog', 'Собаки'),
    ]
    
    SIZE_CHOICES = [
        ('', 'Любой размер'),
        ('small', 'Маленький'),
        ('medium', 'Средний'),
        ('large', 'Крупный'),
    ]
    
    SORT_CHOICES = [
        ('name', 'По имени'),
        ('age', 'По возрасту'),
        ('child_friendly', 'По дружелюбию к детям'),
    ]
    
    species = forms.ChoiceField(
        choices=SPECIES_CHOICES,
        required=False,
        label='Вид животного'
    )
    
    size = forms.ChoiceField(
        choices=SIZE_CHOICES,
        required=False,
        label='Размер'
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        label='Сортировать по'
    )
    
    search = forms.CharField(
        required=False,
        label='Поиск по кличке',
        widget=forms.TextInput(attrs={'placeholder': 'Введите кличку...'})
    )