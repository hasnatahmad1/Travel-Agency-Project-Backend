from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Voucher, FlightInformation, Mautamer, Hotel, Transportation


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data['is_staff'] = self.user.is_staff
        data['is_superuser'] = self.user.is_superuser

        return data


# Nested Serializers for Voucher
class FlightInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightInformation
        fields = [
            'id', 'departure_date', 'arrival_date', 'sector_from', 'sector_to',
            'depart_time', 'arrival_time', 'departure_flight_no', 'departure_flight',
            'departure_pnr', 'nights', 'return_date', 'return_time', 'return_flight_no',
            'return_flight', 'return_sector_from', 'return_sector_to', 'return_pnr',
            'shirka', 'iata', 'service_no'
        ]


class MautamerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mautamer
        fields = ['id', 'pax_name', 'passport']


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = [
            'id', 'hotel_head', 'city', 'checking_date', 'checkout_date',
            'nights', 'hotel_name', 'room_type'
        ]


class TransportationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transportation
        fields = ['id', 'date', 'from_location', 'type_of_transfer']


# Main Voucher Serializers
class VoucherListSerializer(serializers.ModelSerializer):
    """For listing vouchers - minimal data"""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Voucher
        fields = ['id', 'vNo', 'agentName', 'status',
                  'groupName', 'user', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


class VoucherDetailSerializer(serializers.ModelSerializer):
    """For detailed voucher view with all nested data"""
    flight_info = FlightInformationSerializer(required=False)
    mautamers = MautamerSerializer(many=True, required=False)
    hotels = HotelSerializer(many=True, required=False)
    transportations = TransportationSerializer(many=True, required=False)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Voucher
        fields = [
            'id', 'vNo', 'agentName', 'status', 'groupName', 'user',
            'flight_info', 'mautamers', 'hotels', 'transportations',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        flight_info_data = validated_data.pop('flight_info', None)
        mautamers_data = validated_data.pop('mautamers', [])
        hotels_data = validated_data.pop('hotels', [])
        transportations_data = validated_data.pop('transportations', [])

        # Create voucher
        voucher = Voucher.objects.create(**validated_data)

        # Create flight info if provided
        if flight_info_data:
            FlightInformation.objects.create(
                voucher=voucher, **flight_info_data)

        # Create mautamers
        for mautamer_data in mautamers_data:
            Mautamer.objects.create(voucher=voucher, **mautamer_data)

        # Create hotels
        for hotel_data in hotels_data:
            Hotel.objects.create(voucher=voucher, **hotel_data)

        # Create transportations
        for transportation_data in transportations_data:
            Transportation.objects.create(
                voucher=voucher, **transportation_data)

        return voucher

    def update(self, instance, validated_data):
        flight_info_data = validated_data.pop('flight_info', None)
        mautamers_data = validated_data.pop('mautamers', None)
        hotels_data = validated_data.pop('hotels', None)
        transportations_data = validated_data.pop('transportations', None)

        # Update voucher fields
        instance.vNo = validated_data.get('vNo', instance.vNo)
        instance.agentName = validated_data.get(
            'agentName', instance.agentName)
        instance.status = validated_data.get('status', instance.status)
        instance.groupName = validated_data.get(
            'groupName', instance.groupName)
        instance.save()

        # Update or create flight info
        if flight_info_data:
            FlightInformation.objects.update_or_create(
                voucher=instance,
                defaults=flight_info_data
            )

        # Update mautamers (delete old and create new)
        if mautamers_data is not None:
            instance.mautamers.all().delete()
            for mautamer_data in mautamers_data:
                Mautamer.objects.create(voucher=instance, **mautamer_data)

        # Update hotels
        if hotels_data is not None:
            instance.hotels.all().delete()
            for hotel_data in hotels_data:
                Hotel.objects.create(voucher=instance, **hotel_data)

        # Update transportations
        if transportations_data is not None:
            instance.transportations.all().delete()
            for transportation_data in transportations_data:
                Transportation.objects.create(
                    voucher=instance, **transportation_data)

        return instance


class VoucherStatusUpdateSerializer(serializers.ModelSerializer):
    """For admin to update status only"""
    class Meta:
        model = Voucher
        fields = ['status']
