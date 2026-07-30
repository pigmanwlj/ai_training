from django.urls import path

from . import views

from django.conf.urls.static import static

from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('add', views.add, name='madd'),
    path('training/', views.training_page, name='training_page'),
    path('training/run-ollama/', views.training_run_ollama, name='training_run_ollama'),
    path('training/connect-terminal/', views.training_connect_terminal, name='training_connect_terminal'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

