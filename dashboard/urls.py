from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('my-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('about/', views.about_us, name='about_us'),
    path('admin/home/', views.admin_home, name='admin_home'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/approve/<int:item_id>/', views.approve_item, name='approve_item'),
    path('admin/reject/<int:item_id>/', views.reject_item, name='reject_item'),
    path('admin/notify-match/<int:match_id>/', views.notify_match, name='notify_match'),
    path('admin/browse/', views.admin_browse_items, name='admin_browse'),
    path('admin/messages/', views.admin_messages, name='admin_messages'),
    path('admin/notifications/', views.admin_notifications, name='admin_notifications'),
]
