from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.db.models import Q, Avg
from datetime import timedelta
from django.utils import timezone

from .models import User
from diagnosis.models import PlantImage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import translation


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:profile')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email, password)
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('users:profile')  # yoki o'zingizning maqsadli sahifangiz
        else:
            print('log')
            messages.error(request, "Email yoki parol noto‘g‘ri.")
    
    return render(request, 'users/login.html')


@login_required
def profile(request):
    # Fetch user's plant images
    images = PlantImage.objects.filter(user=request.user)
    
    # Handle profile form submission
    if request.method == 'POST' and 'profile_form' in request.POST:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        region = request.POST.get('region', '')  # Optional field
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        # Assuming you have a custom user model with a phone field
        if hasattr(user, 'phone'):
            user.phone = phone
        user.region = region
        user.save()
        messages.success(request, "Profil ma'lumotlari muvaffaqiyatli saqlandi!")
        return redirect('users:profile')

    # Handle password change form submission
    if request.method == 'POST' and 'password_form' in request.POST:
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, "Parol muvaffaqiyatli o'zgartirildi!")
            return redirect('users:profile')
        else:
            messages.error(request, "Yangi parollar mos kelmaydi yoki xato kiritildi!")

    # Handle language settings form submission
    if request.method == 'POST' and 'language_form' in request.POST:
        interface_language = request.POST.get('interface_language')
        results_language = request.POST.get('results_language')
        # Save language preferences (assuming you store them in user profile or session)
        request.session['interface_language'] = interface_language
        request.session['results_language'] = results_language
        # Set Django's language for the session
        translation.activate(interface_language)
        messages.success(request, "Til sozlamalari saqlandi!")
        return redirect('users:profile')

    # Initialize password change form
    password_form = PasswordChangeForm(user=request.user)

    # Calculate statistics
    from django.db.models import Count
    from datetime import datetime
    
    total_analyses = images.count()
    now = timezone.now()
    monthly_analyses = images.filter(created_at__gte=now - timedelta(days=30)).count()
    
    # Average accuracy
    avg_accuracy = images.aggregate(Avg('accuracy'))['accuracy__avg']
    average_accuracy = round(avg_accuracy, 1) if avg_accuracy else 0
    
    # Most common disease
    most_common = images.values('disease_name').annotate(count=Count('disease_name')).order_by('-count').first()
    most_common_disease = most_common['disease_name'] if most_common else 'N/A'
    
    # Recent activities (last 5 analyses)
    recent_activities = []
    for img in images[:5]:
        activity = {
            'description': f"{img.disease_name or 'Unknown'} aniqlandi ({img.accuracy:.0f}% aniqlik)",
            'created_at': img.created_at
        }
        recent_activities.append(activity)

    # Context for template
    context = {
        'images': images,
        'user': request.user,
        'password_form': password_form,
        'total_analyses': total_analyses,
        'monthly_analyses': monthly_analyses,
        'average_accuracy': average_accuracy,
        'most_common_disease': most_common_disease,
        'recent_activities': recent_activities,
    }

    return render(request, 'users/profile.html', context)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from django.http import HttpResponse
from openpyxl import Workbook
from io import BytesIO
import os

@login_required
def history(request):
    # Fetch user's plant images
    images = PlantImage.objects.filter(user=request.user).order_by('-created_at')

    # Apply filters
    date_filter = request.GET.get('date-filter', '')
    disease_filter = request.GET.get('disease-filter', '')
    confidence_filter = request.GET.get('confidence-filter', '')
    search_query = request.GET.get('search-input', '')

    if date_filter:
        now = timezone.now()
        if date_filter == 'today':
            images = images.filter(created_at__date=now.date())
        elif date_filter == 'week':
            images = images.filter(created_at__gte=now - timedelta(days=7))
        elif date_filter == 'month':
            images = images.filter(created_at__gte=now - timedelta(days=30))
        elif date_filter == 'year':
            images = images.filter(created_at__gte=now - timedelta(days=365))

    if disease_filter:
        images = images.filter(
            Q(disease__name__icontains=disease_filter) | 
            Q(disease_name__icontains=disease_filter)
        )

    if confidence_filter:
        if confidence_filter == 'high':
            images = images.filter(accuracy__gte=80)
        elif confidence_filter == 'medium':
            images = images.filter(accuracy__gte=60, accuracy__lt=80)
        elif confidence_filter == 'low':
            images = images.filter(accuracy__lt=60)

    if search_query:
        images = images.filter(
            Q(disease__name__icontains=search_query) |
            Q(disease_name__icontains=search_query) |
            Q(ai_result__icontains=search_query)
        )

    # Apply sorting
    sort = request.GET.get('sort-select', 'date-desc')
    if sort == 'date-asc':
        images = images.order_by('created_at')
    elif sort == 'confidence-desc':
        images = images.order_by('-accuracy')
    elif sort == 'confidence-asc':
        images = images.order_by('accuracy')
    elif sort == 'disease-asc':
        images = images.order_by('disease_name')
    else:  # Default: date-desc
        images = images.order_by('-created_at')

    # Pagination
    paginator = Paginator(images, 12)  # 12 items per page
    page = request.GET.get('page')
    try:
        images_paginated = paginator.page(page)
    except PageNotAnInteger:
        images_paginated = paginator.page(1)
    except EmptyPage:
        images_paginated = paginator.page(paginator.num_pages)

    # Export functionality
    export_format = request.GET.get('export-format', '')
    if export_format:
        if export_format == 'pdf':
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="analysis_history.pdf"'
            p = canvas.Canvas(response, pagesize=letter)
            p.setFont("Helvetica", 12)
            y = 750
            p.drawString(100, y, f"Foydalanuvchi: {request.user.username} - Tahlil Tarixi")
            y -= 30
            for image in images:
                disease_name = image.disease_name or (image.disease.name if image.disease else "Noma'lum")
                accuracy = image.accuracy or 0
                p.drawString(100, y, f"Kasallik: {disease_name} | Aniqlik: {accuracy:.1f}% | Sana: {image.created_at.strftime('%d.%m.%Y %H:%M')}")
                y -= 20
                if y < 50:
                    p.showPage()
                    y = 750
            p.showPage()
            p.save()
            return response
        elif export_format == 'excel':
            wb = Workbook()
            ws = wb.active
            ws.title = "Tahlil Tarixi"
            ws.append(['Foydalanuvchi', 'Kasallik', 'Aniqlik (%)', 'Sana', 'AI Tavsiya'])
            for image in images:
                disease_name = image.disease_name or (image.disease.name if image.disease else "Noma'lum")
                accuracy = image.accuracy or 0
                ws.append([
                    request.user.username, 
                    disease_name, 
                    accuracy, 
                    image.created_at.strftime('%d.%m.%Y %H:%M'),
                    image.ai_result[:100] + '...' if len(image.ai_result) > 100 else image.ai_result
                ])
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="tahlil_tarixi.xlsx"'
            output = BytesIO()
            wb.save(output)
            response.write(output.getvalue())
            return response

    # Statistics for dashboard
    total_analyses = images.count()
    diseases_found = images.exclude(disease_name__isnull=True).exclude(disease_name='').count()
    avg_accuracy = images.aggregate(avg_acc=Avg('accuracy'))['avg_acc'] or 0
    
    # Get unique diseases for filter dropdown
    unique_diseases = set()
    for img in PlantImage.objects.filter(user=request.user):
        if img.disease and img.disease.name:
            unique_diseases.add(img.disease.name)
        if img.disease_name:
            unique_diseases.add(img.disease_name)
    unique_diseases = sorted(list(unique_diseases))

    # Context for template
    context = {
        'images_paginated': images_paginated,
        'total_count': images.count(),
        'page_obj': images_paginated,
        'date_filter': date_filter,
        'disease_filter': disease_filter,
        'confidence_filter': confidence_filter,
        'search_query': search_query,
        'sort': sort,
        'total_analyses': total_analyses,
        'diseases_found': diseases_found,
        'avg_accuracy': round(avg_accuracy, 1),
        'unique_diseases': unique_diseases,
    }

    return render(request, 'users/history.html', context)