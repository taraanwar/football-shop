from django.shortcuts import render
def show_main(request):
    context = {
        'app_name' : 'Football Shop',
        'name': 'Tara Nirmala Anwar',
        'class': 'KKI'
    }

    return render(request, "main.html", context)
