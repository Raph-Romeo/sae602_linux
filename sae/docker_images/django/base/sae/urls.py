from django.urls import path
from .views import index, index_redirect, account, create

urlpatterns = [
    path('', index),
    path('index', index_redirect),
    path('account/<int:id>', account),
    path('create', create),
]
