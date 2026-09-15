from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from apps.clients.models import Client


@login_required
def home(request):
    client = Client.objects.filter(active=True).order_by("id").first()
    if client is None:
        client = Client.objects.order_by("id").first()
    if client is None:
        return redirect("login")
    return redirect("client_detail", pk=client.id)
