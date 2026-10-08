from django.urls import path
from .views import DiseasePredictView, DiseaseSymptomsListView, DiseaseSearchView

urlpatterns = [
    path('predict/', DiseasePredictView.as_view(), name='disease-predict'),
    path('symptoms/', DiseaseSymptomsListView.as_view(), name='disease-symptoms'),
    path('search/', DiseaseSearchView.as_view(), name='disease-search'),
]
