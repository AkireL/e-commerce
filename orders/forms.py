from django import forms


class OrderProductForm(forms.Form):
    product = forms.IntegerField(
        label="product",
        widget=forms.NumberInput(attrs={
            "class": "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-700 shadow-sm transition focus:border-sky-500 focus:ring-4 focus:ring-sky-100 focus:outline-none",
        }),
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Cantidad",
        widget=forms.NumberInput(attrs={
            "class": "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-700 shadow-sm transition focus:border-sky-500 focus:ring-4 focus:ring-sky-100 focus:outline-none",
            "min": "1",
        }),
    )
