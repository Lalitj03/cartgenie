from django.urls import path
from .views import OptimizeCartView

urlpatterns = [
    path('v1/optimize-cart/', OptimizeCartView.as_view(), name='optimize-cart'),
]