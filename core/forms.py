from django import forms
from .models import Persona
from .modeloform import FormModeloBase

class PersonaForm(FormModeloBase):
    user = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'col': '12', 'class': 'form-control', 'placeholder':'Usuario'}))
    password = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'type':'password', 'placeholder':'Contraseña'}))
    cpassword = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'type':'password', 'placeholder':'Confirmar Contraseña'}))

    cedula = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder':'Cédula*'}))
    nombre = forms.CharField(required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder':'Nombre*'}))
    apellido1 = forms.CharField(required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder':'Primer Apellido*'}))
    apellido2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'type':'email', 'placeholder':'Segundo Apellido'}))
    email = forms.CharField(required=False, widget=forms.TextInput(attrs={'col': '12', 'class': 'form-control', 'placeholder':'correo@gmail.com'}))
    celular = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder':'Celular'}))
    fecha_nacimiento = forms.DateField(required=False, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control'}))