from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q, Avg, Count
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from .models import Animal, Shelter, UserProfile, AdoptionApplication
from .forms import AnimalSearchForm, AdoptionApplicationForm, UserRegistrationForm, UserProfileForm


class AnimalListView(ListView):
    model = Animal
    template_name = 'animals/animal_list.html'
    context_object_name = 'animals'
    paginate_by = 6

    def get_queryset(self):
        queryset = Animal.objects.filter(is_available=True).select_related('shelter')

        species = self.request.GET.get('species')
        if species:
            queryset = queryset.filter(species=species)

        size = self.request.GET.get('size')
        if size:
            queryset = queryset.filter(size_category=size)

        sort_by = self.request.GET.get('sort_by', 'name')
        if sort_by in ['name', 'age', 'child_friendly']:
            queryset = queryset.order_by(sort_by)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(breed__icontains=search))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = AnimalSearchForm(self.request.GET)

        animals = Animal.objects.filter(is_available=True).values()
        if animals:
            df = pd.DataFrame(animals)
            context['stats'] = {
                'total_count': len(df),
                'avg_child_friendly': round(df['child_friendly'].mean(), 1),
                'avg_activity': round(df['activity_level'].mean(), 1),
                'cats_count': len(df[df['species'] == 'cat']),
                'dogs_count': len(df[df['species'] == 'dog']),
            }
        else:
            context['stats'] = {
                'total_count': 0,
                'avg_child_friendly': 0,
                'avg_activity': 0,
                'cats_count': 0,
                'dogs_count': 0,
            }

        return context


class AnimalDetailView(DetailView):
    model = Animal
    template_name = 'animals/animal_detail.html'
    context_object_name = 'animal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            try:
                profile = self.request.user.profile
                context['user_compatibility'] = profile.calculate_compatibility_with_animal(self.object)

                categories = ['Дружелюбие к детям', 'Отношение к животным', 'Активность', 'Размер', 'Опыт']
                user_prefs = [
                    profile.pref_child_friendly,
                    profile.pref_pet_friendly,
                    profile.pref_activity_level,
                    7 if profile.pref_size == 'medium' else 5 if profile.pref_size == 'small' else 9,
                    min(profile.experience_years * 2, 10)
                ]
                animal_scores = [
                    self.object.child_friendly,
                    self.object.other_pet_friendly,
                    self.object.activity_level,
                    5 if self.object.size_category == 'small' else 7 if self.object.size_category == 'medium' else 9,
                    5
                ]

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='Ваши предпочтения',
                    x=categories,
                    y=user_prefs,
                    marker_color='#4361ee'
                ))
                fig.add_trace(go.Bar(
                    name='Характеристики животного',
                    x=categories,
                    y=animal_scores,
                    marker_color='#4cc9f0'
                ))

                fig.update_layout(
                    title=f'Совместимость: {context["user_compatibility"]}%',
                    barmode='group',
                    yaxis=dict(title='Оценка (1-10)', range=[0, 10]),
                    height=400
                )

                context['compatibility_chart'] = fig.to_html(full_html=False, include_plotlyjs='cdn')

            except UserProfile.DoesNotExist:
                context['user_compatibility'] = None
                context['compatibility_chart'] = None
        else:
            categories = ['Дети', 'Животные', 'Активность']
            values = [
                self.object.child_friendly,
                self.object.other_pet_friendly,
                self.object.activity_level
            ]

            fig = go.Figure(data=[
                go.Bar(x=categories, y=values, marker_color='#4361ee')
            ])
            fig.update_layout(
                title='Характеристики животного',
                yaxis=dict(title='Оценка (1-10)', range=[0, 10]),
                height=300
            )
            context['compatibility_chart'] = fig.to_html(full_html=False, include_plotlyjs='cdn')

        return context


def shelter_statistics(request):
    shelters = Shelter.objects.all()
    data = []

    for shelter in shelters:
        animals = shelter.animals.filter(is_available=True)
        if animals.exists():
            df = pd.DataFrame(list(animals.values()))
            data.append({
                'name': shelter.name,
                'animal_count': len(animals),
                'avg_age': round(df['age'].mean(), 1),
                'avg_child_friendly': round(df['child_friendly'].mean(), 1),
            })

    chart_html = None
    if data:
        df_stats = pd.DataFrame(data)
        fig = go.Figure(data=[
            go.Bar(
                x=df_stats['name'],
                y=df_stats['animal_count'],
                text=df_stats['animal_count'],
                textposition='auto',
                marker_color='#4361ee'
            )
        ])
        fig.update_layout(
            title='Количество животных по приютам',
            xaxis_title='Приюты',
            yaxis_title='Количество животных',
            height=500
        )
        chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return render(request, 'animals/shelter_stats.html', {
        'shelters': shelters,
        'chart_html': chart_html,
        'stats_data': data
    })


def submit_adoption_application(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id)

    if request.method == 'POST':
        form = AdoptionApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.animal = animal

            if request.user.is_authenticated:
                try:
                    profile = request.user.profile
                    application.compatibility_score = profile.calculate_compatibility_with_animal(animal)
                except UserProfile.DoesNotExist:
                    application.compatibility_score = 50.0
            else:
                application.compatibility_score = 50.0

            application.save()

            messages.success(
                request,
                f'✅ Заявка на {animal.name} успешно отправлена! '
                f'Совместимость: {application.compatibility_score}%. '
                'Мы свяжемся с вами в ближайшее время.'
            )
            return redirect('animal_detail', pk=animal_id)
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['full_name'] = request.user.get_full_name() or request.user.username
            initial_data['email'] = request.user.email
            try:
                initial_data['phone'] = request.user.profile.phone
            except UserProfile.DoesNotExist:
                pass

        form = AdoptionApplicationForm(initial=initial_data)

    context = {
        'animal': animal,
        'application_form': form,
    }

    detail_view = AnimalDetailView()
    detail_view.object = animal
    detail_view.request = request
    context.update(detail_view.get_context_data(object=animal))

    return render(request, 'animals/animal_detail.html', context)


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()

        print(f"DEBUG register - username: {username}")
        print(f"DEBUG register - email: {email}")
        print(f"DEBUG register - password1: {password1}")
        print(f"DEBUG register - password2: {password2}")
        print(f"DEBUG register - POST data: {dict(request.POST)}")

        if not password1:
            messages.error(request, 'Введите пароль')
            return render(request, 'animals/register.html')

        if len(password1) < 8:
            messages.error(request, 'Пароль должен содержать не менее 8 символов')
            return render(request, 'animals/register.html')

        errors = []

        if not username:
            errors.append('Введите имя пользователя')
        if not email:
            errors.append('Введите email')
        if not password1:
            errors.append('Введите пароль')
        if not password2:
            errors.append('Подтвердите пароль')

        if password1 and password2 and password1 != password2:
            errors.append('Пароли не совпадают')

        from django.contrib.auth.models import User
        if username and User.objects.filter(username=username).exists():
            errors.append('Пользователь с таким именем уже существует')
        if email and User.objects.filter(email=email).exists():
            errors.append('Пользователь с таким email уже существует')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'animals/register.html')

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )

            from django.contrib.auth import login
            login(request, user)

            messages.success(
                request,
                f'✅ Регистрация успешна! Добро пожаловать, {username}!'
            )
            messages.info(
                request,
                'Заполните анкету в меню пользователя для получения персональных рекомендаций.'
            )

            return redirect('animal_list')

        except Exception as e:
            messages.error(request, f'Ошибка при регистрации: {str(e)}')
            return render(request, 'animals/register.html')

    return render(request, 'animals/register.html')


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'✅ Добро пожаловать, {username}!')

                try:
                    profile = user.profile
                    if not profile.phone:
                        messages.info(request, 'Заполните анкету для получения рекомендаций')
                except UserProfile.DoesNotExist:
                    messages.info(request, 'Заполните анкету для получения рекомендаций')

                return redirect('animal_list')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = AuthenticationForm()

    return render(request, 'animals/login.html', {'form': form})


def custom_logout(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, '✅ Вы успешно вышли из системы')
        return redirect('animal_list')
    else:
        return render(request, 'animals/logout_confirm.html')


@login_required
def edit_profile(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Если профиля нет - создаем
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Профиль успешно обновлен!')
            return redirect('personal_recommendations')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'animals/edit_profile.html', {'form': form})


@login_required
def personal_recommendations(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Заполните анкету для получения рекомендаций')
        return redirect('edit_profile')

    animals = Animal.objects.filter(is_available=True).select_related('shelter')

    if not animals.exists():
        messages.info(request, 'Нет доступных животных для рекомендаций')
        return render(request, 'animals/personal_recommendations.html', {
            'recommendations': [],
            'stats': {},
            'profile': profile,
            'chart_html': None
        })

    recommendations = []
    for animal in animals:
        compatibility = profile.calculate_compatibility_with_animal(animal)
        recommendations.append({
            'animal': animal,
            'compatibility': compatibility
        })

    recommendations.sort(key=lambda x: x['compatibility'], reverse=True)

    df = pd.DataFrame([
        {
            'name': rec['animal'].name or "Безымянный",
            'species': rec['animal'].species,
            'compatibility': rec['compatibility'],
            'shelter': rec['animal'].shelter.name,
            'age': rec['animal'].age
        }
        for rec in recommendations
    ])

    stats = {}
    chart_html = None

    if not df.empty:
        stats = {
            'total': len(df),
            'avg_compatibility': round(df['compatibility'].mean(), 1),
            'cats_count': len(df[df['species'] == 'cat']),
            'dogs_count': len(df[df['species'] == 'dog']),
            'top_compatibility': df['compatibility'].iloc[0] if len(df) > 0 else 0,
        }

        if len(df) >= 3:
            top_10 = df.head(10)
            fig = px.bar(
                top_10,
                x='name',
                y='compatibility',
                title='Топ-10 рекомендаций по совместимости',
                labels={'name': 'Животное', 'compatibility': 'Совместимость (%)'},
                color='compatibility',
                color_continuous_scale='Viridis',
                text='compatibility'
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(
                xaxis_tickangle=-45,
                height=500,
                showlegend=False
            )
            chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return render(
        request,
        'animals/personal_recommendations.html',
        {
            'recommendations': recommendations[:12],
            'stats': stats,
            'profile': profile,
            'chart_html': chart_html
        }
    )


@login_required
def my_applications(request):
    applications = AdoptionApplication.objects.filter(
        email=request.user.email
    ).select_related('animal', 'animal__shelter').order_by('-created_at')

    status_counts = {}
    avg_compatibility = 0

    if applications.exists():
        df = pd.DataFrame(list(applications.values(
            'status', 'compatibility_score'
        )))

        status_counts = df['status'].value_counts().to_dict()
        avg_compatibility = round(df['compatibility_score'].mean(), 1)

        if status_counts:
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title='Статусы ваших заявок',
                color=list(status_counts.keys()),
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
        else:
            chart_html = None
    else:
        chart_html = None
        messages.info(request, 'У вас пока нет заявок на усыновление')

    return render(
        request,
        'animals/my_applications.html',
        {
            'applications': applications,
            'status_counts': status_counts,
            'avg_compatibility': avg_compatibility,
            'chart_html': chart_html
        }
    )