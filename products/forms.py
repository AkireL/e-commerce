from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock", "available", "photo"]
        labels = {
            "name": "Nombre",
            "description": "Descripción",
            "price": "Precio",
            "stock": "Stock",
            "available": "Disponible",
            "photo": "Foto",
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-700 shadow-sm transition focus:border-sky-500 focus:ring-4 focus:ring-sky-100 focus:outline-none",
                "placeholder": "Café orgánico en grano",
                "autocomplete": "off",
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-700 shadow-sm transition focus:border-sky-500 focus:ring-4 focus:ring-sky-100 focus:outline-none min-h-[140px]",
                "placeholder": "Describe brevemente beneficios, materiales o variantes",
            }),
            "price": forms.NumberInput(attrs={
                "class": "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-700 shadow-sm transition focus:border-sky-500 focus:ring-4 focus:ring-sky-100 focus:outline-none",
                "placeholder": "0.00",
                "step": "0.01",
                "min": "0",
            }),
            "stock": forms.NumberInput(attrs={
                "class": "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-700 shadow-sm transition focus:border-sky-500 focus:ring-4 focus:ring-sky-100 focus:outline-none",
                "placeholder": "250",
                "min": "0",
            }),
            "available": forms.CheckboxInput(attrs={
                "class": "h-5 w-5 rounded border-slate-300 text-sky-500 focus:ring-sky-400 focus:outline-none",
            }),
            "photo": forms.ClearableFileInput(attrs={
                "class": "block w-full rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-sm text-slate-500 transition hover:border-sky-400 focus:border-sky-500 focus:outline-none file:mr-4 file:rounded-full file:border-0 file:bg-sky-600 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white file:transition file:hover:bg-sky-700",
                "accept": "image/*",
            }),
        }
