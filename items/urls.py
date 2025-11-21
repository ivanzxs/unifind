from django.urls import path
from . import views

app_name = 'items'

urlpatterns = [
    path('post-lost/', views.post_lost_item, name='post_lost'),
    path('post-found/', views.post_found_item, name='post_found'),
    path('browse/', views.browse_items, name='browse'),
    path('<int:item_id>/', views.item_detail, name='detail'),
    path('<int:item_id>/edit/', views.edit_item, name='edit_item'),
    path('<int:item_id>/delete/', views.delete_item, name='delete_item'),
    path('<int:item_id>/mark-claimed/', views.mark_as_claimed, name='mark_as_claimed'),
]
