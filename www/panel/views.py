from rest_framework import viewsets
from rest_framework.response import Response

from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import Therapist, Store
from .serializers import TherapistSerializer

User = get_user_model()


class TherapistViewSet(viewsets.ModelViewSet):
    queryset = Therapist.objects.all()
    serializer_class = TherapistSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, 
            data=request.data, 
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'detail': 'Therapist deleted successfully.'}, 
            status=status.HTTP_200_OK
        )

@ensure_csrf_cookie
@login_required
def manage_therapists(request):
    therapists = Therapist.objects.all().order_by('-created_at')
    return render(
        request, 
        'panel/manage_therapists.html', 
        {'therapists': therapists}
    )



@ensure_csrf_cookie
def login_view(request):
    """
    使用 Django Auth。
    表單欄位建議為 name="email" 與 name="password"。
    預設 ModelBackend 用 username；這裡我們用 email 來當 username 試登，
    找不到就再用 username 試一次（兩者擇一皆可登入）。
    """
    if request.method == "POST":
        email_or_username = request.POST.get("email") or ""
        password = request.POST.get("password") or ""

        user = None

        # 先試 email 當 username（常見做法：把 User.username 設為 email）
        user = authenticate(request, username=email_or_username, password=password)

        # 若你希望支援「email 存在於 user.email，但 username 不是 email」的情境，可再查一次：
        if user is None:
            try:
                by_email = User.objects.get(email=email_or_username)
                user = authenticate(request, username=by_email.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            return redirect("portal_home")
        else:
            return render(request, "panel/login.html", {"error": "帳號或密碼錯誤"})

    return render(request, "panel/login.html")


def logout_view(request):
    """
    直接用 Django 的 logout：會清除目前瀏覽器 session 內的登入使用者。
    注意：這也會把 Django Admin 登出（同一瀏覽器同一 session）。
    若你想讓 Admin 不受影響，請改用不同子網域或不同 SESSION_COOKIE_NAME。
    """
    logout(request)
    return redirect("login")


@login_required
def portal_home(request):
    """
    成功登入後可用 request.user 取得當前使用者，
    若想拿到 Store，可：Store.objects.get(user=request.user)
    """
    # 範例：嘗試抓取商家的 Store 資料（如果不是店家也不會壞，只是會找不到）
    store = Store.objects.filter(user=request.user).first()
    ctx = {"store": store}
    return render(request, "panel/portal_home.html", ctx)
