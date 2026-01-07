from django.db import models


class Shelter(models.Model):
    """Модель приюта."""

    name = models.CharField(
        "Название приюта",
        max_length=200
    )
    address = models.TextField("Адрес")
    phone = models.CharField(
        "Телефон",
        max_length=20
    )

    def __str__(self):
        return self.name


class Animal(models.Model):
    """Модель животного."""

    SPECIES_CHOICES = [
        ('cat', 'Кошка'),
        ('dog', 'Собака'),
    ]

    SIZE_CHOICES = [
        ('small', 'Маленький'),
        ('medium', 'Средний'),
        ('large', 'Крупный'),
    ]

    name = models.CharField(
        "Кличка",
        max_length=100,
        blank=True,  # Может быть пустым
        help_text="Если клички нет - оставьте пустым"
    )
    shelter = models.ForeignKey(
        Shelter,
        on_delete=models.CASCADE,
        verbose_name="Приют"
    )
    species = models.CharField(
        "Вид",
        max_length=10,
        choices=SPECIES_CHOICES
    )
    breed = models.CharField(
        "Порода",
        max_length=100,
        blank=True,  # Может быть пустым
        help_text="Не обязательно"
    )
    age = models.IntegerField(
        "Возраст (лет)",
        help_text="Примерный возраст"
    )
    description = models.TextField(
        "Описание",
        blank=True
    )

    # Параметры для алгоритма совместимости
    child_friendly = models.IntegerField(
        "Дружелюбие к детям",
        default=5,
        help_text="От 1 (агрессивен) до 10 (очень дружелюбен)"
    )
    other_pet_friendly = models.IntegerField(
        "Отношение к другим животным",
        default=5,
        help_text="1 (не терпит других животных) - 10 (отлично ладит)"
    )
    activity_level = models.IntegerField(
        "Уровень активности",
        default=5,
        help_text="От 1 (спокойный) до 10 (очень активный)"
    )
    size_category = models.CharField(
        "Размер",
        max_length=10,
        choices=SIZE_CHOICES,
        default='medium'
    )
    arrival_date = models.DateField(
        "Дата поступления",
        auto_now_add=True
    )
    is_available = models.BooleanField(
        "Ищет дом",
        default=True
    )

    def __str__(self):
        if self.name:
            return f"{self.name} ({self.get_species_display()})"
        return f"Безымянный {self.get_species_display()}"


class AdoptionApplication(models.Model):
    """Заявка на усыновление."""

    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
    ]

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        verbose_name="Животное"
    )
    full_name = models.CharField(
        "ФИО",
        max_length=150
    )
    email = models.EmailField("Email")
    phone = models.CharField("Телефон", max_length=20)
    message = models.TextField(
        "Сообщение",
        blank=True,
        help_text="Расскажите о себе и условиях содержания"
    )
    compatibility_score = models.FloatField(
        "Процент совместимости",
        default=0.0
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(
        "Дата заявки",
        auto_now_add=True
    )

    def __str__(self):
        animal_name = self.animal.name or "безымянному"
        return f"Заявка на {animal_name} от {self.full_name}"


    class AdoptionApplication(models.Model):
        animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
        applicant_name = models.CharField(max_length=100)
        applicant_phone = models.CharField(max_length=20)
        applicant_email = models.EmailField()
        message = models.TextField(blank=True, verbose_name="Сообщение")  # ← ДОБАВЬТЕ ЭТО
        compatibility_score = models.IntegerField(default=0)
        status = models.CharField(max_length=20, default='new')
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f'Заявка на {self.animal.name} от {self.applicant_name}'