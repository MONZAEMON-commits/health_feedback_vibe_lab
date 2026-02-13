from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import User


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if not username or not password:
            return render(
                request,
                "accounts/login.html",
                {"error": "ユーザー名とパスワードを入力してください。"},
            )
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role_level in (User.ROLE_ADMIN_L1, User.ROLE_ADMIN_L2):
                return redirect("dashboard:dashboard")
            return redirect("conditions:input")
        return render(request, "accounts/login.html", {"error": "ログインに失敗しました。"})
    return render(request, "accounts/login.html")


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("accounts:login")
    return render(request, "accounts/logout.html")
