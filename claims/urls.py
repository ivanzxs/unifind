from django.urls import path
from . import views

app_name = 'claims'

urlpatterns = [
    path('claim/<int:item_id>/', views.claim_item, name='claim_item'),
    path('review/<int:claim_id>/', views.review_claim, name='review_claim'),
]
