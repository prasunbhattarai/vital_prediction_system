from django.urls import path
from . import views

urlpatterns = [
    path('', views.vitals_list, name='vitals-list'),
    path('<int:pk>/', views.vitals_detail, name='vitals-detail'),
    path('recent/', views.vitals_recent, name='vitals-recent'),
]
