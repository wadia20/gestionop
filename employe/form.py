from django import forms
from .models import Operation,Client

from .models import Employee


from django import forms
from django.contrib.auth.models import User
from .models import Employee

class EmployeeProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = Employee
        fields = ['profile_picture']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    username = forms.CharField(max_length=150)

    class Meta:
        model = User
        fields = ['username', 'email']

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label='Old Password')
    new_password = forms.CharField(widget=forms.PasswordInput, label='New Password')
    new_password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirm New Password')

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        new_password_confirm = cleaned_data.get("new_password_confirm")
        if new_password != new_password_confirm:
            raise forms.ValidationError("New passwords do not match")


class OperationForm(forms.ModelForm):
    class Meta:
        model = Operation
        fields = ['client_id', 'operation', 'observation', 'piece_jointe', 'confirmed']

    

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['client_Name', 'Date_Of_Birth', 'Phone', 'Email', 'Gender', 'Address']



from .models import CompanyInfo

class CompanyInfoForm(forms.ModelForm):
    class Meta:
        model = CompanyInfo
        fields = ['name', 'responsible_person', 'email', 'logo', 'address']
        labels = {
            'name': 'Nom de la Société',
            'responsible_person': 'Nom Responsable',
            'email': 'Email',
            'logo': 'Logo',
            'address': 'Adresse',
        }