from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('conversation/<int:user_id>/', views.conversation, name='conversation'),
    path('send/<int:item_id>/', views.send_message, name='send_message'),
    path('mark-returned/<int:item_id>/<int:user_id>/', views.mark_item_returned, name='mark_returned'),
]
