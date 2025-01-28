# """
# URL configuration for hr_replacement project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/5.1/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# from django.contrib import admin
# from django.urls import path , include# type: ignore,
# from test_details import views
# from django.conf import settings
# from django.conf.urls.static import static 

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('custom_login/', views.custom_login, name='login_page'),
#     path('condidate_register/', views.condidate_register , name='register'),

#     path('face/', include('face_recognition.urls')),
#     path('rules/', include('test_details.urls')),
#     # path('result/', include('test_details.urls')),
#     path('result/', views.result , name='result'),
#     path('test/', include('test_details.urls')),
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])


from django.contrib import admin
from django.urls import path, include
from test_details import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('custom_login/', views.custom_login, name='login_page'),
    path('condidate_register/', views.condidate_register , name='register'),

    path('face/', include('face_recognition.urls')),
    # path('rules/', include('test_details.urls')),  # This includes test_details.urls for the 'rules' endpoint
    path('result/', views.result, name='result'),
    path('test/', include('test_details.urls')),
    path("rules/", views.test_rules, name="rules"),  # You might need to remove this if it's already included above
    path('congratulations/', views.congratulations, name='congratulations'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
