# blog/urls.py
from django.urls import path
from django.contrib import admin
from . import views

#app_name = 'adminPage'
urlpatterns = [
    path('admin/',admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.login_view, name='logout'),
    path('chatlog/', views.admin_list, name='admin_list'),
    path('chatlog/<int:pk>/delete', views.admin_delete, name='admin_delte'),
    path('contents/', views.contents, name='contents'),
    path('contents/display', views.display_data, name='display'),
    path('upload_csv/', views.upload_csv_view, name='upload_csv'),
]
