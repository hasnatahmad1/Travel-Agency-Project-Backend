from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.contrib.auth.models import User
from .serializers import (
    RegisterSerializer, MyTokenObtainPairSerializer,
    VoucherListSerializer, VoucherDetailSerializer, VoucherStatusUpdateSerializer,
    MautamerSerializer, AgentCreateSerializer
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
                'mautamers_count': voucher.voucher_mautamers.count(),
                'created_at': voucher.created_at,
                'updated_at': voucher.updated_at
            })

        return Response(vouchers_data)


# Mautamer Views
class AgentMautamerListView(APIView):
    """
    Agent apne mautamers ki list dekhne ke liye
    GET: Returns all mautamers for logged-in agent
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mautamers = Mautamer.objects.filter(user=request.user)
        serializer = MautamerSerializer(mautamers, many=True)
        return Response(serializer.data)


class AgentCreateView(APIView):
    """
    Admin only: Create agent with mautamers
    POST: Create new agent and upload their mautamers
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AgentCreateSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Get created mautamers count
            mautamers_count = Mautamer.objects.filter(user=user).count()

            return Response(
                {
                    'message': 'Agent created successfully',
                    'agent_id': user.id,
                    'username': user.username,
                    'mautamers_uploaded': mautamers_count
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AgentListView(APIView):
    """
    Admin only: Get all agents (non-staff users)
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        agents = User.objects.filter(is_staff=False).order_by('username')

        agents_data = []
        for agent in agents:
            agents_data.append({
                'id': agent.id,
                'username': agent.username,
                'mautamers_count': agent.mautamers.count(),
                'vouchers_count': agent.vouchers.count(),
                'date_joined': agent.date_joined
            })

        return Response(agents_data)


class AgentMautamerUploadView(APIView):
    """
    Admin only: Upload mautamers for existing agent
    POST: Bulk upload mautamers for an agent
    """
    permission_classes = [IsAdminUser]

    def post(self, request, agent_id):
        try:
            agent = User.objects.get(id=agent_id, is_staff=False)
        except User.DoesNotExist:
            return Response(
                {'error': 'Agent not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        mautamers_data = request.data.get('mautamers', [])

        if not mautamers_data:
            return Response(
                {'error': 'No mautamers data provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Option to replace or append
        replace_existing = request.data.get('replace_existing', False)

        if replace_existing:
            # Delete existing mautamers for this agent
            agent.mautamers.all().delete()

        # Create new mautamers
        created_count = 0
        skipped_count = 0

        for mautamer_data in mautamers_data:
            if 'pax_name' not in mautamer_data or 'passport' not in mautamer_data:
                skipped_count += 1
                continue

            # Check for duplicates
            if Mautamer.objects.filter(
                user=agent,
                passport=mautamer_data['passport']
            ).exists():
                skipped_count += 1
                continue

            Mautamer.objects.create(
                user=agent,
                pax_name=mautamer_data['pax_name'],
                passport=mautamer_data['passport']
            )
            created_count += 1

        return Response(
            {
                'message': f'{created_count} mautamers uploaded successfully',
                'created': created_count,
                'skipped': skipped_count,
                'total_mautamers': agent.mautamers.count()
            },
            status=status.HTTP_201_CREATED
        )
