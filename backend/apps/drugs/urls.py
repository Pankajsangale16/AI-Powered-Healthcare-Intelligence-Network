from django.urls import path
from .views import DrugListView, DrugRecommendView

urlpatterns = [
    path('', DrugListView.as_view(), name='drug-list'),
    path('recommend/', DrugRecommendView.as_view(), name='drug-recommend'),
]
