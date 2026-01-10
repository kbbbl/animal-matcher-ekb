from django import forms
from .models import AdoptionApplication


class AnimalSearchForm(forms.Form):
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


class AdoptionApplicationForm(forms.ModelForm):
    class Meta:
        model = AdoptionApplication
        fields = ['full_name', 'email', 'phone', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов Иван Иванович'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@mail.ru'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Расскажите о себе...'
            }),
        }
        labels = {
            'full_name': 'ФИО',
            'email': 'Email',
            'phone': 'Телефон',
            'message': 'Сообщение',
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not any(char.isdigit() for char in phone):
            raise forms.ValidationError("Введите корректный номер телефона")
        return phone