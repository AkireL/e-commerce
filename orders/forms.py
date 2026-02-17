from django import forms

from products.models import Product


class OrderProductForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(available=True),
        label="Producto",
        empty_label=None,
    )
    quantity = forms.IntegerField(min_value=1, initial=1, label="Cantidad")
