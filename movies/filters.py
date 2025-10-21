"""
Filters for movies and series.
"""
import django_filters
from .models import Movie, Series, Genre, Country
from django.db import models


class MovieFilter(django_filters.FilterSet):
    """Фильтр для фильмов."""
    title = django_filters.CharFilter(
        field_name='title_uz',
        lookup_expr='icontains',
        label='Nom bo‘yicha qidirish'
    )
    genres = django_filters.ModelMultipleChoiceFilter(
        queryset=Genre.objects.all(),
        label='Janrlar'
    )
    countries = django_filters.ModelMultipleChoiceFilter(
        queryset=Country.objects.all(),
        label='Mamlakatlar'
    )
    year = django_filters.RangeFilter(label='Yil')
    year_from = django_filters.NumberFilter(
        field_name='year',
        lookup_expr='gte',
        label='Yildan'
    )
    year_to = django_filters.NumberFilter(
        field_name='year',
        lookup_expr='lte',
        label='Yilgacha'
    )
    actors = django_filters.CharFilter(
        method='filter_by_actors',
        label='Aktor/rejissyor bo‘yicha qidirish'
    )
    content_type = django_filters.ChoiceFilter(
        choices=[('movie', 'Film'), ('cartoon', 'Multfilm')],
        label='Turi'
    )
    
    def filter_by_actors(self, queryset, name, value):
        """Qidiruv: aktyorlar va rejissyorlar bo‘yicha (OR)."""
        if value:
            return queryset.filter(
                (
                    models.Q(actors__name__icontains=value) |
                    models.Q(directors__name__icontains=value)
                )
            ).distinct()
        return queryset
    
    class Meta:
        model = Movie
        fields = ['genres', 'countries', 'year', 'content_type']


class SeriesFilter(django_filters.FilterSet):
    """Фильтр для сериалов."""
    title = django_filters.CharFilter(
        field_name='title_uz',
        lookup_expr='icontains',
        label='Nom bo‘yicha qidirish'
    )
    genres = django_filters.ModelMultipleChoiceFilter(
        queryset=Genre.objects.all(),
        label='Janrlar'
    )
    countries = django_filters.ModelMultipleChoiceFilter(
        queryset=Country.objects.all(),
        label='Mamlakatlar'
    )
    year = django_filters.RangeFilter(label='Yil')
    actors = django_filters.CharFilter(
        method='filter_by_actors',
        label='Aktor/rejissyor bo‘yicha qidirish'
    )
    status = django_filters.ChoiceFilter(
        choices=[
            ('ongoing', 'Davom etmoqda'),
            ('completed', 'Tugallangan'),
            ('cancelled', 'Bekor qilingan'),
        ],
        label='Holat'
    )
    
    def filter_by_actors(self, queryset, name, value):
        """Qidiruv: aktyorlar va rejissyorlar bo‘yicha (OR)."""
        if value:
            return queryset.filter(
                (
                    models.Q(actors__name__icontains=value) |
                    models.Q(directors__name__icontains=value)
                )
            ).distinct()
        return queryset
    
    class Meta:
        model = Series
        fields = ['genres', 'countries', 'year', 'status']

