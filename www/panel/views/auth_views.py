from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model

from ..models import Store

User = get_user_model()


@ensure_csrf_cookie
def login_view(request):
    if request.method == "POST":
        email_or_username = request.POST.get("email") or ""
        password = request.POST.get("password") or ""

        user = None
        user = authenticate(request, username=email_or_username, password=password)

        if user is None:
            try:
                by_email = User.objects.get(email=email_or_username)
                user = authenticate(request, username=by_email.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            store = Store.objects.filter(user=user).first()
            if store:
                request.session['store_name'] = store.name
            return redirect("portal_home")
        else:
            return render(request, "panel/login.html", {"error": "帳號或密碼錯誤"})

    return render(request, "panel/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")
