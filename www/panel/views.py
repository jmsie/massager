from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import Therapist, Store
from .serializers import TherapistSerializer

User = get_user_model()


class TherapistViewSet(viewsets.ModelViewSet):
    serializer_class = TherapistSerializer
    queryset = Therapist.objects.none()  # Default queryset to avoid errors

    def get_queryset(self):
        # 只看自己店、且未刪
        store = getattr(self.request.user, "store", None)
        print("Here")
        if not store:
            return Therapist.objects.none()
        return Therapist.objects.filter(store=store, is_deleted=False)

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
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])
        return Response({"detail": "Therapist soft deleted successfully."},
                        status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        # Associate the therapist with the currently logged-in user's store
        store_name = self.request.session.get('store_name')
        store = Store.objects.filter(name=store_name).first()
        if store:
            serializer.save(store=store)
        else:
            raise ValueError("Store not found for the current session.")

    def perform_update(self, serializer):
        # Prevent changing the store during updates
        if 'store' in serializer.validated_data:
            raise ValueError("Changing the store is not allowed.")
        serializer.save()


@ensure_csrf_cookie
@login_required
def manage_therapists(request):
    therapists = Therapist.objects.all().order_by('-created_at').filter(is_deleted=False)
    return render(
        request,
        'panel/manage_therapists.html',
        {'therapists': therapists}
    )


@ensure_csrf_cookie
def login_view(request):
    if request.method == "POST":
        email_or_username = request.POST.get("email") or ""
        password = request.POST.get("password") or ""

        user = None

        # 先試 email 當 username（常見做法：把 User.username 設為 email）
        user = authenticate(
            request, username=email_or_username, password=password
        )

        # 若你希望支援「email 存在於 user.email，但 username 不是 email」的情境，可再查一次：
        if user is None:
            try:
                by_email = User.objects.get(email=email_or_username)
                user = authenticate(
                    request, username=by_email.username, password=password
                )
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)

            # Store the store name in the session
            store = Store.objects.filter(user=user).first()
            if store:
                request.session['store_name'] = store.name

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
    # Use store name from session
    ctx = {"store_name": request.session.get("store_name", "店家名稱")}
    return render(request, "panel/portal_home.html", ctx)
