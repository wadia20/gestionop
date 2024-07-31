from django.urls import path, include
from . import views
from django.contrib import admin
from django.contrib.auth import views as auth_views
from .views import OperationListView,operation_list_pdf,Clients_show, Generate_pdf,DashboardView
app_name = "employe"

urlpatterns = [
  
    path('', views.login_employe, name='login'),
    path('logout/', views.logout_employe, name='logoutw'),
    
    path('dashboard/', views.DashboardView.as_view(), name='base'),
    path('client/add',views.ADD_CLIENT,name='add_client'),
    path('operation/add',views.ADD_OPERATION,name='add_operation'),
    path('operation/all',OperationListView.as_view(),name='all_operation'),
    path('operations/pdf/',operation_list_pdf, name='operationlistpdf'),
    path('client/search/', views.search_clients, name='search_clients'),  # Search path
    path('clients/<str:client_id>',views.operation_details, name='detailsop'),
    path('client/show', Clients_show.as_view(), name='client_show'),
    path('clients/<str:client_id>/pdf/<int:operation_id>/', views.Generate_pdf, name='generate_pdf'),
    path('searchoperation/', views.search_operations, name='search_operations'),
    path('dash', views.home, name='Dashboard'),
    path('operation/delete/<int:operation_id>/', views.delete_operation, name='delete_operation'),
    path('delete_client/<str:client_id>', views.delete_client, name='delete_client'),  
    
    path('edit_client/', views.edit_client, name='edit_client'),  
    path('edit_operation/<int:operation_id>/', views.edit_operation, name='edit_operation'),
    path('edit_client/', views.edit_client, name='edit_client'),
    path('edit_client/<str:client_id>/', views.edit_client_with_id, name='edit_client_with_id'),
    path('detailoperation/<int:operation_id>/', views.detail1_operation, name='detailoperation'),
    path('profile/', views.profile_view, name='profile'),
    path('client_report/', views.client_report, name='client_report'),
    path('operation_report/', views.operation_report, name='operation_report'),

    path('edit-company-info/', views.edit_company_info, name='edit_company_info'),


]
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)