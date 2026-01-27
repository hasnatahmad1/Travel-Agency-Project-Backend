from django.contrib import admin
from django.urls import path
from api.views import (
    RegisterView, LoginView,
    VoucherListCreateView, VoucherDetailView, VoucherStatusUpdateView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Voucher CRUD
    path('vouchers/', VoucherListCreateView.as_view(), name='voucher-list-create'),
    path('vouchers/<int:pk>/', VoucherDetailView.as_view(), name='voucher-detail'),
    path('vouchers/<int:pk>/status/', VoucherStatusUpdateView.as_view(),
         name='voucher-status-update'),
]
