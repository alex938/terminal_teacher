"""URL configuration for commands app."""
from django.urls import path
from . import views

urlpatterns = [
    # Public URLs
    path('', views.student_view, name='student_view'),
    path('api/commands/', views.api_get_commands, name='api_get_commands'),
    path('healthz/', views.healthz, name='healthz'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Admin URLs
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    
    # Protected API URLs
    path('api/submit/', views.api_submit_command, name='api_submit_command'),
    path('api/commands/<int:command_id>/delete/', views.api_delete_command, name='api_delete_command'),
    path('api/session/clear/', views.api_clear_session, name='api_clear_session'),
    path('api/session/new/', views.api_new_session, name='api_new_session'),
    path('api/commands/manual/', views.api_add_manual_command, name='api_add_manual_command'),
]
    path('api/database/nuke/', views.api_nuke_database, name='api_nuke_database'),
