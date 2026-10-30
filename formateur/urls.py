from django.urls import path
from . import views

app_name = 'formateur'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard_alt'),

    # Profil
    path('profil/', views.profile_view, name='profile'),
    path('profil/modifier/', views.profile_edit_view, name='profile_edit'),

    # Formations (CRUD)
    path('formations/', views.formation_list_view, name='formation_list'),
    path('formations/creer/', views.formation_create_view, name='formation_create'),
    path('formations/<int:pk>/', views.formation_detail_view, name='formation_detail'),
    path('formations/<int:pk>/modifier/', views.formation_update_view, name='formation_update'),
    path('formations/<int:pk>/supprimer/', views.formation_delete_view, name='formation_delete'),

    # Participants (Apprenants)
    path('participants/', views.participant_list_view, name='participant_list'),
    path('participants/<int:pk>/statut/', views.participant_status_update_view, name='participant_status_update'),

    # Certifications
    path('certifications/', views.certification_list_view, name='certification_list'),
    path('certifications/delivrer/', views.certification_issue_view, name='certification_issue'),
    path('certifications/<int:pk>/', views.certification_detail_view, name='certification_detail'),

    # Notifications
    path('notifications/', views.notification_list_view, name='notification_list'),
    path('notifications/<int:pk>/marquer-lue/', views.notification_mark_read_view, name='notification_mark_read'),
    path('notifications/tout-marquer-lu/', views.notification_mark_all_read_view, name='notification_mark_all_read'),
]
