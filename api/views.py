from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .serializers import (
    RegisterSerializer, MyTokenObtainPairSerializer,
    VoucherListSerializer, VoucherDetailSerializer, VoucherStatusUpdateSerializer,
    MautamerSerializer
)
from .models import Voucher, Mautamer


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
    Admin only: Update voucher status (Approve/Reject)
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
            return Response({
                'message': 'Status updated successfully',
                'status': serializer.data['status']
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MautamerBulkUploadView(APIView):
    """
    Admin only: Bulk upload mautamers from Excel data
    POST: Upload multiple mautamers for a voucher
    """
    permission_classes = [IsAdminUser]

    def post(self, request, voucher_id):
        try:
            voucher = Voucher.objects.get(id=voucher_id)
        except Voucher.DoesNotExist:
            return Response(
                {'error': 'Voucher not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        mautamers_data = request.data.get('mautamers', [])

        if not mautamers_data:
            return Response(
                {'error': 'No mautamers data provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Delete existing mautamers for this voucher
        voucher.mautamers.all().delete()

        # Create new mautamers
        created_mautamers = []
        for mautamer_data in mautamers_data:
            if 'pax_name' not in mautamer_data or 'passport' not in mautamer_data:
                continue

            mautamer = Mautamer.objects.create(
                voucher=voucher,
                pax_name=mautamer_data['pax_name'],
                passport=mautamer_data['passport']
            )
            created_mautamers.append(mautamer)

        # Serialize and return created mautamers
        response_serializer = MautamerSerializer(created_mautamers, many=True)

        return Response(
            {
                'message': f'{len(created_mautamers)} mautamers uploaded successfully',
                'mautamers': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class AdminVoucherListView(APIView):
    """
    Admin only: Get all vouchers with additional details for admin panel
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        vouchers = Voucher.objects.all().order_by('-created_at')

        vouchers_data = []
        for voucher in vouchers:
            flight_info = voucher.flight_info if hasattr(
                voucher, 'flight_info') else None

            vouchers_data.append({
                'id': voucher.id,
                'vNo': voucher.vNo,
                'agentName': voucher.agentName,
                'groupName': voucher.groupName,
                'status': voucher.status,
                'arrival_date': flight_info.arrival_date if flight_info else None,
                'return_date': flight_info.return_date if flight_info else None,
                'nights': flight_info.nights if flight_info else 0,
                'mautamers_count': voucher.mautamers.count(),
                'created_at': voucher.created_at,
                'updated_at': voucher.updated_at
            })

        return Response(vouchers_data)
