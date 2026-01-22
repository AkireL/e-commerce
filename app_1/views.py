from django.shortcuts import render

# Create your views here.
def my_view(request):
    return render(request, 'card_list.html', context={
        'cars': [
        {
            'title': "mazda"
        },
        {
            'title': 'vmw'
        },
        {
            'title': 'bmw'
        },
        {
            'title': 'toyota'
        },
        ]
    })