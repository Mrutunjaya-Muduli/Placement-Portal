from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('register/recruiter/', views.register_recruiter, name='register_recruiter'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Student Routes
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/ics/', views.export_job_ics, name='export_job_ics'),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('calendar/', views.placement_calendar, name='placement_calendar'),
    
    # Company Routes
    path('company/dashboard/', views.company_dashboard, name='company_dashboard'),
    path('company/post-job/', views.post_job, name='post_job'),
    path('company/candidates/<int:job_id>/', views.view_candidates, name='view_candidates'),
    path('company/update-status/<int:application_id>/', views.update_status, name='update_status'),
    
    # Custom Admin Dashboard Route
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
