from django import forms
from django.core.validators import RegexValidator


class PaymentForm(forms.Form):
    card_holder = forms.CharField(label="Nombre del titular", max_length=100)
    card_number = forms.CharField(
        label="Número de tarjeta",
        max_length=16,
        validators=[RegexValidator(r"^\d{16}$", "Ingresa 16 dígitos")],
        widget=forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "cc-number"}),
    )
    cvv = forms.CharField(
        label="CVV",
        max_length=3,
        validators=[RegexValidator(r"^\d{3}$", "Ingresa 3 dígitos")],
        widget=forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "cc-csc", "type": "password"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_classes = "w-full rounded-lg border border-gray-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
        for field in self.fields.values():
            field.widget.attrs["class"] = base_classes
