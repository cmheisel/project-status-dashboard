from django.http import HttpResponse
from django.views.generic import View

# Create your views here.
class HealthCheck(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Health: OK")
