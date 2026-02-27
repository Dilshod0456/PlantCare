"""
Disease detail views and analytics
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import Disease, PlantImage
from users.models import User


def disease_list(request):
    """List all diseases"""
    diseases = Disease.objects.all().order_by('name')
    
    # Get statistics for each disease
    disease_stats = []
    for disease in diseases:
        count = PlantImage.objects.filter(
            Q(disease=disease) | Q(disease_name__icontains=disease.name)
        ).count()
        
        disease_stats.append({
            'disease': disease,
            'detection_count': count
        })
    
    context = {
        'disease_stats': disease_stats,
        'total_diseases': diseases.count()
    }
    
    return render(request, 'diagnosis/disease_list.html', context)


def disease_detail(request, pk):
    """Disease detail page"""
    disease = get_object_or_404(Disease, pk=pk)
    
    # Get related detections
    related_images = PlantImage.objects.filter(
        Q(disease=disease) | Q(disease_name__icontains=disease.name)
    ).order_by('-created_at')[:6]
    
    # Statistics
    total_detections = PlantImage.objects.filter(
        Q(disease=disease) | Q(disease_name__icontains=disease.name)
    ).count()
    
    avg_confidence = PlantImage.objects.filter(
        Q(disease=disease) | Q(disease_name__icontains=disease.name)
    ).aggregate(Avg('accuracy'))['accuracy__avg'] or 0
    
    context = {
        'disease': disease,
        'related_images': related_images,
        'total_detections': total_detections,
        'avg_confidence': round(avg_confidence, 1),
    }
    
    return render(request, 'diagnosis/disease_detail.html', context)


@staff_member_required
def analytics_dashboard(request):
    """Admin analytics dashboard"""
    now = timezone.now()
    
    # Time periods
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Total statistics
    total_users = User.objects.count()
    total_analyses = PlantImage.objects.count()
    total_diseases = Disease.objects.count()
    
    # Recent statistics
    analyses_today = PlantImage.objects.filter(created_at__date=today).count()
    analyses_week = PlantImage.objects.filter(created_at__gte=week_ago).count()
    analyses_month = PlantImage.objects.filter(created_at__gte=month_ago).count()
    
    # Users statistics
    users_today = User.objects.filter(date_joined__date=today).count()
    users_week = User.objects.filter(date_joined__gte=week_ago).count()
    users_month = User.objects.filter(date_joined__gte=month_ago).count()
    
    # Average accuracy
    avg_accuracy = PlantImage.objects.aggregate(Avg('accuracy'))['accuracy__avg'] or 0
    
    # Most common diseases
    disease_stats = PlantImage.objects.values('disease_name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Recent analyses
    recent_analyses = PlantImage.objects.select_related('user').order_by('-created_at')[:10]
    
    # Active users
    active_users = PlantImage.objects.filter(
        created_at__gte=month_ago
    ).values('user__username').annotate(
        analysis_count=Count('id')
    ).order_by('-analysis_count')[:10]
    
    # Daily analysis chart data (last 30 days)
    daily_data = []
    for i in range(30):
        date = (now - timedelta(days=i)).date()
        count = PlantImage.objects.filter(created_at__date=date).count()
        daily_data.append({
            'date': date.strftime('%d.%m'),
            'count': count
        })
    daily_data.reverse()
    
    # Model performance by disease
    disease_performance = []
    for disease in Disease.objects.all()[:10]:
        images = PlantImage.objects.filter(
            Q(disease=disease) | Q(disease_name__icontains=disease.name)
        )
        avg_acc = images.aggregate(Avg('accuracy'))['accuracy__avg'] or 0
        disease_performance.append({
            'name': disease.name,
            'count': images.count(),
            'avg_accuracy': round(avg_acc, 1)
        })
    
    context = {
        'total_users': total_users,
        'total_analyses': total_analyses,
        'total_diseases': total_diseases,
        'analyses_today': analyses_today,
        'analyses_week': analyses_week,
        'analyses_month': analyses_month,
        'users_today': users_today,
        'users_week': users_week,
        'users_month': users_month,
        'avg_accuracy': round(avg_accuracy, 1),
        'disease_stats': disease_stats,
        'recent_analyses': recent_analyses,
        'active_users': active_users,
        'daily_data': daily_data,
        'disease_performance': disease_performance,
    }
    
    return render(request, 'diagnosis/analytics_dashboard.html', context)
