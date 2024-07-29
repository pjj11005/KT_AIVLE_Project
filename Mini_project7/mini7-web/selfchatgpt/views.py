from django.shortcuts import render

# Create your views here.
def index(request):
    print("views index")
    return render(request, 'selfgpt/index.html')

