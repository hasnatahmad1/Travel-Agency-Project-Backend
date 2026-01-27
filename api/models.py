from django.db import models
from django.contrib.auth.models import User


class Voucher(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='vouchers')
    vNo = models.CharField(max_length=50, unique=True)
    agentName = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    groupName = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vNo} - {self.agentName}"

    class Meta:
        ordering = ['-created_at']


class FlightInformation(models.Model):
    voucher = models.OneToOneField(
        Voucher, on_delete=models.CASCADE, related_name='flight_info')

    # Departure Information
    departure_date = models.DateField()
    arrival_date = models.DateField()
    sector_from = models.CharField(max_length=100)
    sector_to = models.CharField(max_length=100)
    depart_time = models.TimeField()
    arrival_time = models.TimeField()
    departure_flight_no = models.CharField(max_length=50)
    departure_flight = models.CharField(max_length=200)
    departure_pnr = models.CharField(max_length=50)
    nights = models.IntegerField(help_text="Departure - Arrival nights")

    # Return Information
    return_date = models.DateField()
    return_time = models.TimeField()
    return_flight_no = models.CharField(max_length=50)
    return_flight = models.CharField(max_length=200)
    return_sector_from = models.CharField(max_length=100)
    return_sector_to = models.CharField(max_length=100)
    return_pnr = models.CharField(max_length=50)

    # Additional Information
    shirka = models.CharField(max_length=200)
    iata = models.CharField(max_length=50)
    service_no = models.CharField(max_length=50)

    def __str__(self):
        return f"Flight Info - {self.voucher.vNo}"


class Mautamer(models.Model):
    voucher = models.ForeignKey(
        Voucher, on_delete=models.CASCADE, related_name='mautamers')
    pax_name = models.CharField(max_length=200)
    passport = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.pax_name} - {self.passport}"

    class Meta:
        ordering = ['id']


class Hotel(models.Model):
    ROOM_TYPE_CHOICES = [
        ('single', 'Single Room'),
        ('double', 'Double Room'),
        ('triple', 'Triple Room'),
        ('quad', 'Quad Room'),
        ('family', 'Family Room'),
    ]

    voucher = models.ForeignKey(
        Voucher, on_delete=models.CASCADE, related_name='hotels')
    hotel_head = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    checking_date = models.DateField()
    checkout_date = models.DateField()
    nights = models.IntegerField()
    hotel_name = models.CharField(max_length=200)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)

    def __str__(self):
        return f"{self.hotel_name} - {self.city}"

    class Meta:
        ordering = ['checking_date']


class Transportation(models.Model):
    TRANSFER_TYPE_CHOICES = [
        ('bus', 'Bus'),
        ('car', 'Car'),
        ('van', 'Van'),
        ('taxi', 'Taxi'),
        ('other', 'Other'),
    ]

    voucher = models.ForeignKey(
        Voucher, on_delete=models.CASCADE, related_name='transportations')
    date = models.DateField()
    from_location = models.CharField(max_length=200)
    type_of_transfer = models.CharField(
        max_length=20, choices=TRANSFER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.type_of_transfer} - {self.from_location}"

    class Meta:
        ordering = ['date']
