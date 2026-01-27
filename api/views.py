from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import (
    RegisterSerializer, MyTokenObtainPairSerializer,
    VoucherListSerializer, VoucherDetailSerializer, VoucherStatusUpdateSerializer
)
from .models import Voucher


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'User registered successfully'},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# Voucher CRUD Views
class VoucherListCreateView(ListCreateAPIView):
    """
    GET: List all vouchers for authenticated user
    POST: Create new voucher
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VoucherDetailSerializer
        return VoucherListSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # Admin can see all vouchers
            return Voucher.objects.all()
        # Normal user can only see their own vouchers
        return Voucher.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VoucherDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve single voucher with all details
    PUT/PATCH: Update voucher
    DELETE: Delete voucher
    """
    permission_classes = [IsAuthenticated]
    serializer_class = VoucherDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Voucher.objects.all()
        return Voucher.objects.filter(user=user)


class VoucherStatusUpdateView(APIView):
    """
    Admin only: Update voucher status
    """
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            voucher = Voucher.objects.get(pk=pk)
        except Voucher.DoesNotExist:
            return Response(
                {'error': 'Voucher not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = VoucherStatusUpdateSerializer(
            voucher,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
