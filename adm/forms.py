from django import forms
from core.models import Persona
from core.modeloform import FormModeloBase

class AddTrabajoForm(FormModeloBase):
    user = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'col': '12', 'class': 'form-control', 'placeholder':'Usuario'}))
    password = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'type':'password', 'placeholder':'Contraseña'}))
    cpassword = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'type':'password', 'placeholder':'Confirmar Contraseña'}))

    cedula = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'separator': 'true',"separatortitle":'Ingrese los datos de la persona', 'placeholder':'Cédula*'}))
    nombre = forms.CharField(required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder':'Nombre*'}))
    apellido1 = forms.CharField(required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder':'Primer Apellido*'}))
    apellido2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'type':'email', 'placeholder':'Segundo Apellido'}))
    email = forms.CharField(required=False, widget=forms.TextInput(attrs={'col': '12', 'class': 'form-control', 'placeholder':'correo@gmail.com'}))
    celular = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder':'Celular'}))
    fecha_nacimiento = forms.DateField(required=False, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control'}))