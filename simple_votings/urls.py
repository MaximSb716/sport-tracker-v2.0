"""
URL configuration for simple_votings project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from main.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index1, name='index1'),
    path('about_us/', about_us, name='about_us'),
    path('catalog/', catalog, name='catalog'),
    path('profile/', profile, name='profile'),
    path('survey/', survey, name='survey'),
    path('voting', voting, name='voting'),
    path('voting/new', new_voting, name='voting/new'),
    path('voting/delete', delete_voting, name='voting/delete'),
    path('add_voting', add_voting, name='add_voting'),
    path('applications', applications, name='applications'),
    path('approve_item', approve_item, name='approve_item'),
    path('reject_item', reject_item, name='reject_item'),
    path('add_voting/<int:voting_id>/', add_voting, name='add_voting'),
    path('submit_inventory/', submit_inventory, name='submit_inventory'),
    path("", include("main.urls"))
]

urlpatterns += static(settings.UPLOADS_URL, document_root=settings.UPLOADS_ROOT)
