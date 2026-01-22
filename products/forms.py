from .models import Product
from django import forms

class ProductForm(forms.Form):

    name = forms.CharField(max_length=200, label='Nombre')
    description = forms.CharField(max_length=300, label='Descripción')
    price = forms.DecimalField(max_digits=10, decimal_places=2, label='Precio')
    stock = forms.IntegerField(max_value=999999, label="stock", required=True)
    available = forms.BooleanField(initial=True, label='Disponible', required=False)
    photo = forms.ImageField(label='Foto', required=False)
    
    def save(self):
        Product.objects.create(
            name=self.cleaned_data['name'],
            description=self.cleaned_data['description'],
            price=self.cleaned_data['price'],
            stock=self.cleaned_data['stock'],
            available=self.cleaned_data['available'],
            photo=self.cleaned_data['photo'],
        )