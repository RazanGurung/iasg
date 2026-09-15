from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def monthly_fees(request):
    return render(request, "core/stub.html", {"title": "Monthly fees ACH file"})
