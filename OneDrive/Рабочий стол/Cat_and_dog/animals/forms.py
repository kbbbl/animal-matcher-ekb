from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import AdoptionApplication, UserProfile


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
        widget=forms.TextInput(
            attrs={'placeholder': 'Введите кличку...'}
        )
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
            raise forms.ValidationError(
                "Введите корректный номер телефона"
            )
        return phone


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.ru'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Логин'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ['user', 'created_at', 'updated_at']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67'
            }),
            'home_type': forms.Select(attrs={'class': 'form-select'}),
            'children_age': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '5 лет, 10 и 12 лет'
            }),
            'other_pets_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Кот, 3 года, спокойный'
            }),
            'pref_child_friendly': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
            'pref_pet_friendly': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
            'pref_activity_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
            'pref_size': forms.Select(attrs={'class': 'form-select'}),
            'daily_walk_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'work_schedule': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '5/2, удаленная работа'
            }),
        }
        labels = {
            'pref_child_friendly': 'Важность дружелюбия к детям',
            'pref_pet_friendly': 'Важность дружелюбия к животным',
            'pref_activity_level': 'Предпочитаемая активность',
        }
        help_texts = {
            'pref_child_friendly': '1 - не важно, 10 - очень важно',
            'pref_pet_friendly': '1 - не важно, 10 - очень важно',
            'pref_activity_level': '1 - спокойный, 10 - очень активный',
        }