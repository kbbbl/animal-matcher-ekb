from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
import pandas as pd
import plotly.graph_objects as go
from .models import Animal, Shelter, UserProfile, AdoptionApplication
from .forms import AnimalSearchForm, AdoptionApplicationForm, UserRegistrationForm, UserProfileForm


class AnimalListView(ListView):
    model = Animal
    template_name = 'animals/animal_list.html'
    context_object_name = 'animals'
    paginate_by = 6

    def get_queryset(self):
        queryset = Animal.objects.filter(is_available=True)

        species = self.request.GET.get('species')
        if species:
            queryset = queryset.filter(species=species)

        size = self.request.GET.get('size')
        if size:
            queryset = queryset.filter(size_category=size)

        sort_by = self.request.GET.get('sort_by', 'name')
        if sort_by in ['name', 'age', 'child_friendly']:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = AnimalSearchForm(self.request.GET)
        context['stats'] = self._calculate_statistics()
        return context

    def _calculate_statistics(self):
        animals = self.get_queryset().values()
        if not animals:
            return {}

        df = pd.DataFrame(animals)

        stats = {
            'total_count': len(df),
            'avg_child_friendly': round(df['child_friendly'].mean(), 1),
            'avg_activity': round(df['activity_level'].mean(), 1),
            'cats_count': len(df[df['species'] == 'cat']),
            'dogs_count': len(df[df['species'] == 'dog']),
        }
        return stats


class AnimalDetailView(DetailView):
    model = Animal
    template_name = 'animals/animal_detail.html'
    context_object_name = 'animal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['compatibility_chart'] = self._create_compatibility_chart()
        return context

    def _create_compatibility_chart(self):
        animal = self.object

        categories = ['Дети', 'Животные', 'Активность', 'Размер']
        values = [
            animal.child_friendly,
            animal.other_pet_friendly,
            animal.activity_level,
            5 if animal.size_category == 'small' else
            7 if animal.size_category == 'medium' else 9
        ]

        fig = go.Figure(data=[
            go.Bar(
                name='Параметры животного',
                x=categories,
                y=values,
                marker_color='rgb(55, 83, 109)'
            )
        ])

        fig.update_layout(
            title='Профиль совместимости',
            yaxis=dict(title='Оценка (1-10)', range=[0, 10]),
            showlegend=True,
            template='plotly_white'
        )

        return fig.to_html(full_html=False, include_plotlyjs='cdn')


def shelter_statistics(request):
    shelters = Shelter.objects.all()
    data = []

    for shelter in shelters:
        animals = shelter.animal_set.filter(is_available=True)
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
            )
        ])
        fig.update_layout(
            title='Количество животных по приютам',
            xaxis_title='Приюты',
            yaxis_title='Количество животных'
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
            application.save()

            messages.success(request, 'Заявка успешно отправлена! Мы свяжемся с вами.')
            return redirect('animal_detail', pk=animal_id)
    else:
        form = AdoptionApplicationForm()

    context = {
        'animal': animal,
        'application_form': form,
        'compatibility_chart': AnimalDetailView()._create_compatibility_chart(animal)
    }
    return render(request, 'animals/animal_detail.html', context)


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            login(request, user)
            messages.success(
                request,
                'Регистрация успешна! Заполните анкету.'
            )
            return redirect('animal_list')
    else:
        user_form = UserRegistrationForm()

    return render(
        request,
        'animals/register.html',
        {'user_form': user_form}
    )


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(
                username=username,
                password=password
            )
            if user is not None:
                login(request, user)
                messages.success(
                    request,
                    f'Добро пожаловать, {username}!'
                )
                return redirect('animal_list')
    else:
        form = AuthenticationForm()

    return render(
        request,
        'animals/login.html',
        {'form': form}
    )


@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Профиль успешно обновлен!'
            )
            return redirect('animal_list')
    else:
        form = UserProfileForm(instance=profile)

    return render(
        request,
        'animals/edit_profile.html',
        {'form': form}
    )


@login_required
def personal_recommendations(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        messages.warning(
            request,
            'Заполните анкету для получения рекомендаций'
        )
        return redirect('edit_profile')

    animals = Animal.objects.filter(is_available=True)
    recommendations = []

    for animal in animals:
        compatibility = profile.calculate_compatibility_with_animal(
            animal
        )
        recommendations.append({
            'animal': animal,
            'compatibility': compatibility
        })

    recommendations.sort(
        key=lambda x: x['compatibility'],
        reverse=True
    )

    df = pd.DataFrame([
        {
            'name': rec['animal'].name or "Безымянный",
            'species': rec['animal'].species,
            'compatibility': rec['compatibility'],
            'shelter': rec['animal'].shelter.name
        }
        for rec in recommendations
    ])

    stats = {}
    chart_html = None

    if not df.empty:
        stats = {
            'total': len(df),
            'avg_compatibility': round(
                df['compatibility'].mean(),
                1
            ),
            'max_compatibility': df['compatibility'].max(),
            'min_compatibility': df['compatibility'].min(),
            'cats_count': len(df[df['species'] == 'cat']),
            'dogs_count': len(df[df['species'] == 'dog']),
        }

        if len(df) > 0:
            fig = go.Figure(data=[
                go.Bar(
                    x=df['name'][:10],
                    y=df['compatibility'][:10],
                    marker_color='rgb(55, 83, 109)'
                )
            ])
            fig.update_layout(
                title='Топ-10 рекомендаций по совместимости',
                xaxis_title='Животные',
                yaxis_title='Совместимость (%)',
                showlegend=False
            )
            chart_html = fig.to_html(
                full_html=False,
                include_plotlyjs='cdn'
            )

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
    ).order_by('-created_at')

    if applications.exists():
        df = pd.DataFrame(
            list(applications.values(
                'status',
                'compatibility_score'
            ))
        )
        status_counts = df['status'].value_counts().to_dict()
        avg_compatibility = round(
            df['compatibility_score'].mean(),
            1
        )
    else:
        status_counts = {}
        avg_compatibility = 0

    return render(
        request,
        'animals/my_applications.html',
        {
            'applications': applications,
            'status_counts': status_counts,
            'avg_compatibility': avg_compatibility
        }
    )