from django.contrib import admin
from django.urls import path
from api.views import (
    RegisterView, LoginView,
    VoucherListCreateView, VoucherDetailView, VoucherStatusUpdateView,
    AdminVoucherListView, AgentMautamerListView,
    AgentCreateView, AgentListView, AgentMautamerUploadView
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

    # Admin - Voucher Management
    path('api/admin/vouchers/', AdminVoucherListView.as_view(),
         name='admin-voucher-list'),
    path('api/admin/vouchers/<int:pk>/status/',
         VoucherStatusUpdateView.as_view(), name='voucher-status-update'),

    # Admin - Agent Management
    path('api/admin/agents/', AgentListView.as_view(), name='admin-agent-list'),
    path('api/admin/agents/create/',
         AgentCreateView.as_view(), name='admin-agent-create'),
    path('api/admin/agents/<int:agent_id>/mautamers/',
         AgentMautamerUploadView.as_view(), name='admin-agent-mautamer-upload'),

    # Agent - Mautamer Access
    path('api/agent/mautamers/', AgentMautamerListView.as_view(),
         name='agent-mautamer-list'),
]
