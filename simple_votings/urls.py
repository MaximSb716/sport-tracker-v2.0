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
    path('voting', voting, name='voting'),
    path('voting/new', new_voting, name='voting/new'),
    path('voting/delete', delete_voting, name='voting/delete'),
    path('add_voting', add_voting, name='add_voting'),
    path('applications', applications, name='applications'),
    path('approve_item', approve_item, name='approve_item'),
    path('reject_item', reject_item, name='reject_item'),
    path('add_voting/<int:voting_id>/', add_voting, name='add_voting'),
    path('secure_inventory/', secure_inventory, name='secure_inventory'),
    path('user_detail/<int:user_id>/', user_detail, name='user_detail'),
    path('issue_inventory/<int:user_id>/<int:voting_id>/<str:item_name>/', issue_inventory, name='issue_inventory'),
    path('view_inventory/', view_inventory, name='view_inventory'),
    path('items/', item_list, name='item_list'),
    path('items/create/', item_create, name='item_create'),
    path('items/update/<int:item_id>/', item_update, name='item_update'),
    path('items/delete/<int:item_id>/', item_delete, name='item_delete'),
    path('view_reports/', view_reports, name='view_reports'),
    path("", include("main.urls"))
]

urlpatterns += static(settings.UPLOADS_URL, document_root=settings.UPLOADS_ROOT)
