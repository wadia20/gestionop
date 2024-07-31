from .models import *
from django.contrib import auth
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .form import *
from employe.models import Client,Operation,type_operation,CompanyInfo

from django.views import View
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

# home page
def home(request):
    company_info = CompanyInfo.objects.first()
    print(f"Company Info: {company_info}")  # Debugging line
    return render(request, 'login.html', {'company_info': company_info})

def base(request):
    return render(request, "dashboard.html")
#logout

def logout_employe(request):
    auth.logout(request)
    return redirect('employe:login')
#login page 
def login_employe(request):
    company_info = CompanyInfo.objects.first()
    if request.method == 'POST':
        username = request.POST.get('login')
        password = request.POST.get('pass')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("employe:base")
        else:
            messages.warning(request, 'something went wrong')
            return redirect('employe:login')
    return render(request,'login.html',{'company_info': company_info})

#add client
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from .models import Client

def ADD_CLIENT(request):
    if request.method == 'POST':
        id = request.POST.get('client_id')
        name = request.POST.get('client_name')
        birth = request.POST.get('client_birth')
        phone = request.POST.get('client_phone')
        email = request.POST.get('client_email')
        gender = request.POST.get('client_gender')
        address = request.POST.get('client_Address')

        if not all([id, name, birth, phone, email, gender, address]):
            messages.error(request, 'All fields are required.')
            return render(request, 'client/add_client.html')

        client = Client(
            client_id=id,
            client_Name=name,
            Date_Of_Birth=birth,
            Phone=phone,
            Email=email,
            Gender=gender,
            Address=address,
        )

        try:
            client.save()
            messages.success(request, 'Client added successfully!')
            return redirect('employe:client_show')  # Redirect to client list
        except IntegrityError:
            messages.error(request, 'Client ID already exists.')
            return render(request, 'client/add_client.html')

    return render(request, 'client/add_client.html')



#add operation
from django.shortcuts import render, redirect


from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.contrib import messages
from .form import OperationForm
from django.views.generic import ListView

def ADD_OPERATION(request):
    if request.method == 'POST':
        form = OperationForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                form.save()
                messages.success(request, 'Operation added successfully!')
                return redirect('employe:add_operation')
        except IntegrityError:
            messages.error(request, 'Operation ID already exists.')
            return render(request, 'client/add_operation.html', {'form': form})
    else:
        form = OperationForm()  # Ensure form is initialized for GET request
    
    typeoperation = type_operation.objects.all()
    
    return render(request, 'client/add_operation.html', {'form': form, 'typeoperation': typeoperation})


from django.views.generic import ListView
#showing list of operations

from django.shortcuts import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
class OperationListView(ListView):
    model = Operation
    template_name = 'client/operation_list.html'
    context_object_name = 'operations'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['operations'] = page_obj.object_list
        return context



def operation_list_pdf(request):
    query = request.GET.get('query')
    if query:
        operations = Operation.objects.filter(client_id__icontains=query)
    else:
        operations = Operation.objects.all()
    
    template_path = 'client/operation_list_pdf.html'
    context = {'operations': operations}
    template = get_template(template_path)
    html = template.render(context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="operations_{query}.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    
    return response
# afficher les cients avec leurs operations

from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Client, Operation
from django.core.paginator import Paginator
class Clients_show(View):
    def get(self, request):
        clients_list = Client.objects.all()
        paginator = Paginator(clients_list, 10)  # Show 10 clients per page.
        page_number = request.GET.get('page')
        clients = paginator.get_page(page_number)
        
        for client in clients:
            operations_count = Operation.objects.filter(client_id=client.client_id).count()
            client.operations_count = operations_count
            client.operations = Operation.objects.filter(client_id=client.client_id)

        context = {
            'clients': clients
        }
        return render(request, 'client/show_client.html', context)


def search_clients(request):
    query = request.GET.get('query', '').strip()
    clients_list = Client.objects.filter(client_id=query) if query else Client.objects.none()
    
    paginator = Paginator(clients_list, 10)  # Show 10 clients per page.
    page_number = request.GET.get('page')
    clients = paginator.get_page(page_number)
    
    for client in clients:
        operations_count = Operation.objects.filter(client_id=client.client_id).count()
        client.operations_count = operations_count
        client.operations = Operation.objects.filter(client_id=client.client_id)

    context = {
        'clients': clients,
        'query': query
    }
    return render(request, 'client/show_client.html', context)

#pdf

from django.shortcuts import get_object_or_404, HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Operation
import os
from django.conf import settings

def Generate_pdf(request, client_id, operation_id):
    client = get_object_or_404(Client, client_id=client_id)
    operation = get_object_or_404(Operation, id=operation_id, client_id=client_id)
    company = CompanyInfo.objects.first()  # Récupère les informations de la première entreprise

    filename = request.GET.get('filename', 'default_filename.pdf')  # Récupère le nom du fichier à partir de la chaîne de requête

    context = {
        'client': client,
        'operations': [operation],  # Passe uniquement l'opération sélectionnée
        'company': company,  # Ajoute les informations de l'entreprise au contexte
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    template = get_template('pdf_template.html')
    html = template.render(context)

    # Crée le PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

#recherche d'operarion
from django.shortcuts import render
from .models import Operation

def search_operations(request):
    query = request.GET.get('query')
    if query:
        operations = Operation.objects.filter(client_id__icontains=query)
    else:
        operations = Operation.objects.all()
    return render(request, 'client/operation_list.html', {'operations': operations})


from django.views.generic import TemplateView
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import json


class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Operations pagination
        operations_list = Operation.objects.order_by('-operation_date')
        paginator_operations = Paginator(operations_list, 5)  # Show 5 operations per page

        page_number_operations = self.request.GET.get('page_operations')
        page_obj_operations = paginator_operations.get_page(page_number_operations)
        context['page_obj_operations'] = page_obj_operations

        # Employees pagination
        employees_list = Employee.objects.all()
        paginator_employees = Paginator(employees_list, 10)  # Show 10 employees per page

        page_number_employees = self.request.GET.get('page_employees')
        page_obj_employees = paginator_employees.get_page(page_number_employees)
        context['page_obj_employees'] = page_obj_employees

        context['clients_count'] = Client.objects.count()

        total_operations = Operation.objects.count()
        operations_per_day = Operation.objects.filter(operation_date=timezone.now().date()).count()

        # Prepare data for Operations Month by Month chart
        operations_by_month = Operation.objects.extra(select={'month': "strftime('%Y-%m', operation_date)"}).values('month').annotate(count=Count('id')).order_by('month')
        operations_by_month = list(operations_by_month)
        context['operations_by_month'] = json.dumps(operations_by_month)

        # Prepare data for Clients Month by Month chart
        clients_by_month = Client.objects.extra(select={'month': "strftime('%Y-%m', created_date)"}).values('month').annotate(count=Count('id')).order_by('month')
        clients_by_month = list(clients_by_month)
        context['clients_by_month'] = json.dumps(clients_by_month)

        context['total_operations'] = total_operations
        context['operations_per_day'] = operations_per_day

        return context

from django.shortcuts import get_object_or_404


def operation_details(request, client_id):
    client = get_object_or_404(Client, client_id=client_id)
    operations_list = Operation.objects.filter(client_id=client_id)

    # Pagination logic
    paginator = Paginator(operations_list, 10)  # Show 10 operations per page
    page_number = request.GET.get('page')
    operations = paginator.get_page(page_number)

    context = {
        'client_id': client_id,
        'operations': operations,
        'client': client,
    }

    return render(request, 'client/specifique_operations.html', context)



from django.urls import reverse

#delete operation
# def delete_operations(request):
#     query = request.GET.get('query')
#     if query:
#         operations = Operation.objects.filter(client_id__icontains=query)
#     else:
#         operations = Operation.objects.all()

#     if request.method == 'POST':
#         operation_id = request.POST.get('operation_id')
#         if operation_id:
#             operation_to_delete = get_object_or_404(Operation, id=operation_id)
#             operation_to_delete.delete()
#             messages.success(request, 'L\'opération a été supprimée avec succès.')
#             return redirect(reverse('employe:delete_operations') + f'?query={query}')

#     return render(request, 'client/delete_operation.html', {'operations': operations})
def delete_operation(request, operation_id):
    operation = get_object_or_404(Operation, id=operation_id)
    client_id = operation.client_id
    operation.delete()
    messages.success(request, "Operation deleted successfully")
    return redirect('employe:detailsop', client_id=client_id)

#edit operation 
def edit_operation(request, operation_id):
    operation = get_object_or_404(Operation, id=operation_id)
    
    if request.method == 'POST':
        form = OperationForm(request.POST, request.FILES, instance=operation)
        if form.is_valid():
            client_id = form.cleaned_data['client_id']
            if not Client.objects.filter(client_id=client_id).exists():
                messages.error(request, "aucun client trouve avec ce CIN il faut l'ajouter.")
                return redirect('employe:add_client') 
            form.save()
            messages.success(request, "Operation updated successfully")
            return redirect('employe:detailsop', client_id=operation.client_id)
        else:
            messages.error(request, "Invalid operation")
    else:
        form = OperationForm(instance=operation)

    context = {
        'form': form,
        'operation': operation
    }

    return render(request, 'client/edit_operation.html', context)


#delete a client
def delete_client(request, client_id):
    client = get_object_or_404(Client, client_id=client_id)

    if request.method == 'POST':
        operations = Operation.objects.filter(client_id=client_id)
        operations.delete()
        client.delete()
        messages.success(request, 'Client ' + client.client_Name + ' has been deleted successfully.')
        return redirect('employe:client_show')

    return render(request, 'client/delete_client.html', {'client': client})

from .form import ClientForm

def edit_client(request):
    client_id = request.GET.get('client_id')
    client = None
    if client_id:
        try:
            client = Client.objects.get(client_id=client_id)
        except Client.DoesNotExist:
            messages.error(request, 'Client ID does not exist. Please try again.')
            return redirect('employe:edit_client')
    return render(request, 'client/edit_client.html', {'client': client})

def edit_client_with_id(request, client_id):
    client = get_object_or_404(Client, client_id=client_id)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client updated successfully!')
            return redirect('employe:detailsop', client_id=client_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClientForm(instance=client)
    return render(request, 'client/edit_client.html', {'form': form, 'client': client})

def detail1_operation(request,operation_id):


    operation = get_object_or_404(Operation, id=operation_id)
    
    return render(request, 'client/operation_detail.html',{'operation': operation})




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .form import UserUpdateForm, PasswordChangeForm, EmployeeProfileForm
from .models import Employee

@login_required
def profile_view(request):
    if request.method == 'POST':
        if 'profile_picture' in request.FILES or 'profile_picture' in request.POST:
            profile_form = EmployeeProfileForm(request.POST, request.FILES, instance=request.user.employee)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile picture updated successfully.")
            else:
                messages.error(request, "Failed to update profile picture.")
            return redirect('employe:profile')
        
        elif 'username' in request.POST or 'email' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "User information updated successfully.")
            else:
                messages.error(request, "Failed to update user information.")
            return redirect('employe:profile')
        
        elif 'old_password' in request.POST:
            password_form = PasswordChangeForm(request.POST)
            if password_form.is_valid():
                old_password = password_form.cleaned_data['old_password']
                new_password = password_form.cleaned_data['new_password']
                if request.user.check_password(old_password):
                    request.user.set_password(new_password)
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    messages.success(request, "Password updated successfully.")
                else:
                    messages.error(request, "Old password is incorrect.")
            else:
                messages.error(request, "Failed to update password.")
            return redirect('employe:profile')
    
    else:
        user_form = UserUpdateForm(instance=request.user)
        password_form = PasswordChangeForm()
        profile_form = EmployeeProfileForm(instance=request.user.employee)

    return render(request, 'client/profile.html', {
        'user_form': user_form,
        'password_form': password_form,
        'profile_form': profile_form
    })




from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def clear_profile_picture(request):
    employee = request.user.employee
    if employee.profile_picture:
        employee.profile_picture.delete(save=True)
        messages.success(request, "Profile picture cleared successfully.")
    else:
        messages.info(request, "No profile picture to clear.")
    return redirect('employe:profile')  # Adjust this to the URL name of your profile view


#rapport def client_report(request):
from django.utils.timezone import datetime

def client_report(request):
    clients = []
    start_date = ''
    end_date = ''

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # Convert date strings to datetime objects
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Query operations within the specified date range
        operations = Operation.objects.filter(operation_date__range=(start_datetime, end_datetime))

        # Get unique client_ids from the operations
        client_ids = operations.values_list('client_id', flat=True).distinct()

        # Query clients based on the client_ids
        clients = Client.objects.filter(client_id__in=client_ids)

        # Pagination
        paginator = Paginator(clients, 10)  # Show 10 clients per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = []

    context = {
        'page_obj': page_obj,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'client/client_report.html', context)


def operation_report(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

                # Query operations within the date range
                operations = Operation.objects.filter(
                    operation_date__range=(start_date, end_date)
                )

                paginator = Paginator(operations, 10)  # 10 operations per page
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)

                context = {
                    'operations': page_obj,
                    'start_date': start_date,
                    'end_date': end_date,
                }
                return render(request, 'client/operation_report.html', context)

            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
        else:
            messages.error(request, "Both start and end dates are required.")

    return render(request, 'client/operation_report.html')




from .models import CompanyInfo
from .form import CompanyInfoForm

def edit_company_info(request):
    company_info = CompanyInfo.objects.first()  # Assuming there is only one instance
    if request.method == 'POST':
        form = CompanyInfoForm(request.POST, request.FILES, instance=company_info)
        if form.is_valid():
            form.save()
            return redirect('employe:edit_company_info')  # Redirect to the homepage after saving
    else:
        form = CompanyInfoForm(instance=company_info)
    return render(request, 'client/edit_company_info.html', {'form': form})