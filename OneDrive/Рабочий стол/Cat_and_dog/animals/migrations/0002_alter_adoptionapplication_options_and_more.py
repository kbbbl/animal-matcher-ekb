import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adoptionapplication',
            options={'ordering': ['-created_at'], 'verbose_name': 'Заявка на усыновление', 'verbose_name_plural': 'Заявки на усыновление'},
        ),
        migrations.AlterModelOptions(
            name='animal',
            options={'ordering': ['name'], 'verbose_name': 'Животное', 'verbose_name_plural': 'Животные'},
        ),
        migrations.AlterModelOptions(
            name='shelter',
            options={'verbose_name': 'Приют', 'verbose_name_plural': 'Приюты'},
        ),
        migrations.AddField(
            model_name='adoptionapplication',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.AddField(
            model_name='animal',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='animals/', verbose_name='Фотография'),
        ),
        migrations.AddField(
            model_name='shelter',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание приюта'),
        ),
        migrations.AddField(
            model_name='shelter',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='Email приюта'),
        ),
        migrations.AlterField(
            model_name='adoptionapplication',
            name='animal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='animals.animal', verbose_name='Животное'),
        ),
        migrations.AlterField(
            model_name='adoptionapplication',
            name='status',
            field=models.CharField(choices=[('pending', 'На рассмотрении'), ('approved', 'Одобрена'), ('rejected', 'Отклонена'), ('completed', 'Завершена')], default='pending', max_length=20, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='animal',
            name='other_pet_friendly',
            field=models.IntegerField(default=5, help_text='1 (не терпит) - 10 (отлично ладит)', verbose_name='Отношение к другим животным'),
        ),
        migrations.AlterField(
            model_name='animal',
            name='shelter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='animals', to='animals.shelter', verbose_name='Приют'),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Телефон')),
                ('home_type', models.CharField(choices=[('apartment', 'Квартира'), ('house', 'Частный дом'), ('dacha', 'Дача'), ('other', 'Другое')], default='apartment', max_length=20, verbose_name='Тип жилья')),
                ('has_children', models.BooleanField(default=False, verbose_name='Есть дети')),
                ('children_age', models.CharField(blank=True, help_text='Например: 5 лет, 10 и 12 лет', max_length=50, verbose_name='Возраст детей')),
                ('has_other_pets', models.BooleanField(default=False, verbose_name='Есть другие животные')),
                ('other_pets_info', models.TextField(blank=True, help_text='Какие животные, их характер', verbose_name='Информация о других животных')),
                ('experience_years', models.IntegerField(default=0, verbose_name='Опыт содержания животных (лет)')),
                ('pref_child_friendly', models.IntegerField(default=5, help_text='От 1 (не важно) до 10 (очень важно)', verbose_name='Важность дружелюбия к детям')),
                ('pref_pet_friendly', models.IntegerField(default=5, verbose_name='Важность дружелюбия к другим животным')),
                ('pref_activity_level', models.IntegerField(default=5, help_text='1 - спокойный, 10 - очень активный', verbose_name='Предпочитаемый уровень активности')),
                ('pref_size', models.CharField(blank=True, choices=[('small', 'Маленький'), ('medium', 'Средний'), ('large', 'Крупный')], max_length=10, verbose_name='Предпочитаемый размер')),
                ('daily_walk_time', models.IntegerField(default=30, help_text='Для собак', verbose_name='Время на прогулки (минут в день)')),
                ('has_garden', models.BooleanField(default=False, verbose_name='Есть двор/сад')),
                ('work_schedule', models.CharField(blank=True, help_text='Например: 5/2, удаленная работа, фриланс', max_length=50, verbose_name='График работы')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания профиля')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Профиль пользователя',
                'verbose_name_plural': 'Профили пользователей',
            },
        ),
    ]
