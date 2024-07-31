from django.contrib import admin
from .models import Employee,Client,Operation
# Register your models here.
admin.site.register(Employee)
admin.site.register(Client)
admin.site.register(Operation)

from django.contrib import admin
from .models import CompanyInfo

admin.site.register(CompanyInfo)