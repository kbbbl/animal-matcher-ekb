from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

SIZE_CHOICES = [
    ('small', 'Маленький'),
    ('medium', 'Средний'),
    ('large', 'Крупный'),
]


class Shelter(models.Model):
    name = models.CharField(
        "Название приюта",
        max_length=200
    )
    address = models.TextField("Адрес")
    phone = models.CharField(
        "Телефон",
        max_length=20
    )
    email = models.EmailField(
        "Email приюта",
        blank=True
    )
    description = models.TextField(
        "Описание приюта",
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Приют"
        verbose_name_plural = "Приюты"


class Animal(models.Model):
    SPECIES_CHOICES = [
        ('cat', 'Кошка'),
        ('dog', 'Собака'),
    ]

    name = models.CharField(
        "Кличка",
        max_length=100,
        blank=True,
        help_text="Если клички нет - оставьте пустым"
    )
    shelter = models.ForeignKey(
        Shelter,
        on_delete=models.CASCADE,
        verbose_name="Приют",
        related_name='animals'
    )
    species = models.CharField(
        "Вид",
        max_length=10,
        choices=SPECIES_CHOICES
    )
    breed = models.CharField(
        "Порода",
        max_length=100,
        blank=True,
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
    photo = models.ImageField(
        "Фотография",
        upload_to='animals/',
        blank=True,
        null=True
    )

    child_friendly = models.IntegerField(
        "Дружелюбие к детям",
        default=5,
        help_text="От 1 (агрессивен) до 10 (очень дружелюбен)"
    )
    other_pet_friendly = models.IntegerField(
        "Отношение к другим животным",
        default=5,
        help_text="1 (не терпит) - 10 (отлично ладит)"
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

    class Meta:
        verbose_name = "Животное"
        verbose_name_plural = "Животные"
        ordering = ['name']


class AdoptionApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
        ('completed', 'Завершена'),
    ]

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        verbose_name="Животное",
        related_name='applications'
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
    updated_at = models.DateTimeField(
        "Дата обновления",
        auto_now=True
    )

    def __str__(self):
        animal_name = self.animal.name or "безымянному"
        return f"Заявка на {animal_name} от {self.full_name}"

    class Meta:
        verbose_name = "Заявка на усыновление"
        verbose_name_plural = "Заявки на усыновление"
        ordering = ['-created_at']


class UserProfile(models.Model):
    HOME_TYPE_CHOICES = [
        ('apartment', 'Квартира'),
        ('house', 'Частный дом'),
        ('dacha', 'Дача'),
        ('other', 'Другое'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name='profile'
    )
    phone = models.CharField(
        "Телефон",
        max_length=20,
        blank=True
    )
    home_type = models.CharField(
        "Тип жилья",
        max_length=20,
        choices=HOME_TYPE_CHOICES,
        default='apartment'
    )
    has_children = models.BooleanField(
        "Есть дети",
        default=False
    )
    children_age = models.CharField(
        "Возраст детей",
        max_length=50,
        blank=True,
        help_text="Например: 5 лет, 10 и 12 лет"
    )
    has_other_pets = models.BooleanField(
        "Есть другие животные",
        default=False
    )
    other_pets_info = models.TextField(
        "Информация о других животных",
        blank=True,
        help_text="Какие животные, их характер"
    )
    experience_years = models.IntegerField(
        "Опыт содержания животных (лет)",
        default=0
    )
    pref_child_friendly = models.IntegerField(
        "Важность дружелюбия к детям",
        default=5,
        help_text="От 1 (не важно) до 10 (очень важно)"
    )
    pref_pet_friendly = models.IntegerField(
        "Важность дружелюбия к другим животным",
        default=5
    )
    pref_activity_level = models.IntegerField(
        "Предпочитаемый уровень активности",
        default=5,
        help_text="1 - спокойный, 10 - очень активный"
    )
    pref_size = models.CharField(
        "Предпочитаемый размер",
        max_length=10,
        choices=SIZE_CHOICES,
        blank=True
    )
    daily_walk_time = models.IntegerField(
        "Время на прогулки (минут в день)",
        default=30,
        help_text="Для собак"
    )
    has_garden = models.BooleanField(
        "Есть двор/сад",
        default=False
    )
    work_schedule = models.CharField(
        "График работы",
        max_length=50,
        blank=True,
        help_text="Например: 5/2, удаленная работа, фриланс"
    )
    created_at = models.DateTimeField(
        "Дата создания профиля",
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        "Дата обновления",
        auto_now=True
    )

    def __str__(self):
        return f"Профиль: {self.user.username}"

    def get_experience_level(self):
        if self.experience_years == 0:
            return "Новичок"
        elif self.experience_years < 3:
            return "Опытный"
        else:
            return "Профессионал"

    def calculate_compatibility_with_animal(self, animal):
        total_score = 0

        if self.has_children:
            child_score = (animal.child_friendly / 10.0) * 25
        else:
            child_score = 12.5
        total_score += child_score

        if self.has_other_pets:
            pet_score = (animal.other_pet_friendly / 10.0) * 20
        else:
            pet_score = 10
        total_score += pet_score

        activity_diff = abs(animal.activity_level - self.pref_activity_level)
        activity_score = max(0, (10 - activity_diff) / 10.0) * 15
        total_score += activity_score

        if self.pref_size and animal.size_category == self.pref_size:
            size_score = 15
        elif self.pref_size and animal.size_category != self.pref_size:
            size_score = 5
        else:
            size_score = 10
        total_score += size_score

        if self.experience_years >= 3 and animal.activity_level <= 7:
            experience_score = 10
        elif self.experience_years >= 1:
            experience_score = 7
        else:
            experience_score = 5
        total_score += experience_score

        if animal.species == 'dog' and self.daily_walk_time >= 60:
            conditions_score = 15
        elif animal.species == 'dog' and self.daily_walk_time >= 30:
            conditions_score = 10
        elif animal.species == 'dog':
            conditions_score = 5
        else:
            conditions_score = 12

        if animal.size_category == 'large' and self.has_garden:
            conditions_score += 3

        total_score += min(conditions_score, 15)

        return round(total_score, 1)

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()