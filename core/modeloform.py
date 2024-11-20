
from django import forms
from django.forms.widgets import DateTimeBaseInput
from django.utils.safestring import mark_safe

class CustomDateInput(DateTimeBaseInput):
    def format_value(self, value):
        return str(value or '')

class FormModeloBase(forms.Form):
    def __init__(self, *args, **kwargs):
        self.ver = kwargs.pop('ver') if 'ver' in kwargs else False
        # self.editando = 'instance' in kwargs
        self.instancia = kwargs.pop('instancia', None)
        no_requeridos = kwargs.pop('no_requeridos') if 'no_requeridos' in kwargs else []
        requeridos = kwargs.pop('requeridos') if 'requeridos' in kwargs else []
        # if self.editando:
        #     self.instancia = kwargs['instance']
        super(FormModeloBase, self).__init__(*args, **kwargs)
        for nr in no_requeridos:
            self.fields[nr].required = False
        for r in requeridos:
            self.fields[r].required = True
        for k, v in self.fields.items():
            field = self.fields[k]
            if isinstance(field, forms.TimeField):
                attrs_ = self.fields[k].widget.attrs
                self.fields[k].widget = CustomDateInput(attrs={'type': 'time'})
                self.fields[k].widget.attrs = attrs_
            if isinstance(field, forms.DateField):
                attrs_ = self.fields[k].widget.attrs
                self.fields[k].widget = CustomDateInput(attrs={'type': 'date'})
                self.fields[k].widget.attrs = attrs_
                if 'class' in self.fields[k].widget.attrs:
                    self.fields[k].widget.attrs['class'] += " form-control"
                else:
                    self.fields[k].widget.attrs['class'] = "form-control"
            elif isinstance(field, forms.BooleanField):
                if 'class' in self.fields[k].widget.attrs:
                    self.fields[k].widget.attrs['class'] += "js-switch"
                else:
                    self.fields[k].widget.attrs['class'] = "js-switch"
                self.fields[k].widget.attrs['data-render'] = "switchery"
                self.fields[k].widget.attrs['data-theme'] = "default"
            else:
                if 'class' in self.fields[k].widget.attrs:
                    self.fields[k].widget.attrs['class'] += " form-control"
                else:
                    self.fields[k].widget.attrs['class'] = "form-control"
                if not 'col' in self.fields[k].widget.attrs:
                    self.fields[k].widget.attrs['col'] = "12"
            if self.fields[k].required and self.fields[k].label:
                self.fields[k].label = mark_safe(self.fields[k].label + '<span style="color:red;margin-left:2px;"><strong>*</strong></span>')
            self.fields[k].widget.attrs['data-nameinput'] = k
            if self.ver:
                self.fields[k].widget.attrs['readonly'] = "readonly"