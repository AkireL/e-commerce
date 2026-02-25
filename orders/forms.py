from django import forms


class OrderProductForm(forms.Form):
    product = forms.ChoiceField(
        label="product",
        widget=forms.Select(attrs={
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

    def __init__(self, products=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if products:
            self.fields['product'].choices = [
                (p['id'], p['name']) for p in products
            ]
        self._products_data = {p['id']: p for p in (products or [])}

    def get_product_data(self, product_id):
        return self._products_data.get(product_id)
