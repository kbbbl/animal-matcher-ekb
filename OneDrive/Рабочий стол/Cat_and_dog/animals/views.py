# animals/views.py
from django.shortcuts import render
from django.views.generic import ListView, DetailView
import pandas as pd
import plotly.graph_objects as go
from .models import Animal, Shelter
from .forms import AnimalSearchForm


class AnimalListView(ListView):
    # Отображение списка животных с фильтрацией и сортировкой
    model = Animal
    template_name = 'animals/animal_list.html'
    context_object_name = 'animals'
    paginate_by = 6

    def get_queryset(self):
        # Фильтрация доступных животных по параметрам
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
        # Добавление формы поиска и статистики в контекст
        context = super().get_context_data(**kwargs)
        context['search_form'] = AnimalSearchForm(self.request.GET)
        context['stats'] = self._calculate_statistics()
        return context

    def _calculate_statistics(self):
        # Расчет статистики с использованием Pandas
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
    # Детальная страница животного с графиком совместимости
    model = Animal
    template_name = 'animals/animal_detail.html'
    context_object_name = 'animal'

    def get_context_data(self, **kwargs):
        # Добавление графика Plotly в контекст
        context = super().get_context_data(**kwargs)
        context['compatibility_chart'] = self._create_compatibility_chart()
        return context

    def _create_compatibility_chart(self):
        # Создание интерактивного графика Plotly
        animal = self.object

        categories = ['Дети', 'Животные', 'Активность', 'Размер']
        values = [
            animal.child_friendly,
            animal.pet_friendly,
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
    # Статистика приютов с использованием Pandas и Plotly
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