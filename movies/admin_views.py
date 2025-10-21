"""
Admin views for getting next episode/season numbers
"""
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .models import Season, Episode

@staff_member_required
def get_next_episode_number(request):
    """Получить следующий номер эпизода для сезона"""
    season_id = request.GET.get('season_id')
    if not season_id:
        return JsonResponse({'error': 'season_id required'}, status=400)
    
    try:
        season = Season.objects.get(pk=season_id)
        last_episode = Episode.objects.filter(season=season).order_by('-episode_number').first()
        next_number = (last_episode.episode_number + 1) if last_episode else 1
        return JsonResponse({'next_number': next_number})
    except Season.DoesNotExist:
        return JsonResponse({'error': 'Season not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@staff_member_required
def get_next_season_number(request):
    """Получить следующий номер сезона для сериала"""
    series_id = request.GET.get('series_id')
    if not series_id:
        return JsonResponse({'error': 'series_id required'}, status=400)
    
    try:
        from .models import Series
        series = Series.objects.get(pk=series_id)
        last_season = Season.objects.filter(series=series).order_by('-season_number').first()
        next_number = (last_season.season_number + 1) if last_season else 1
        return JsonResponse({'next_number': next_number})
    except Series.DoesNotExist:
        return JsonResponse({'error': 'Series not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
