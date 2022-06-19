from django.shortcuts import get_object_or_404, render

from .models import UserIp


def get_client_ip(request):
    x_forw_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forw_for is not None:
        ip = x_forw_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def show_client_ip(request):
    ip_adresse = get_client_ip(request)
    UserIp.objects.all().update(Ip=ip_adresse)
    
    return render(request, 'adresse.html', {"ip_adresse":ip_adresse})