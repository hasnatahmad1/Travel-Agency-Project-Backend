from django.db import models
from django.contrib.auth.models import User


class Mautamer(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='mautamers',
        help_text="Agent jiske liye ye mautamer hai",
        null=True,
        blank=True
    )
    pax_name = models.CharField(max_length=200)
    passport = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pax_name} - {self.passport} ({self.user.username if self.user else 'No User'})"

    class Meta:
        ordering = ['pax_name']


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


class VoucherMautamer(models.Model):
    """
    Junction table between Voucher and Mautamer
    Voucher mein selected mautamers ko store karta hai
    """
    voucher = models.ForeignKey(
        Voucher, on_delete=models.CASCADE, related_name='voucher_mautamers')
    mautamer = models.ForeignKey(
        Mautamer, on_delete=models.CASCADE, related_name='voucher_assignments')

    class Meta:
        unique_together = ['voucher', 'mautamer']
        ordering = ['id']

    def __str__(self):
        return f"{self.voucher.vNo} - {self.mautamer.pax_name}"


class FlightInformation(models.Model):
    voucher = models.OneToOneField(
        Voucher, on_delete=models.CASCADE, related_name='flight_info')

    departure_date = models.DateField()
    arrival_date = models.DateField()
    sector_from = models.CharField(max_length=100, blank=True, default='')
    sector_to = models.CharField(max_length=100, blank=True, default='')
    depart_time = models.TimeField()
    arrival_time = models.TimeField()
    departure_flight_no = models.CharField(
        max_length=50, blank=True, default='')
    departure_flight = models.CharField(max_length=200, blank=True, default='')
    departure_pnr = models.CharField(max_length=50, blank=True, default='')
    nights = models.IntegerField(
        help_text="Departure - Arrival nights", default=0)

    return_date = models.DateField()
    return_time = models.TimeField()
    return_flight_no = models.CharField(max_length=50, blank=True, default='')
    return_flight = models.CharField(max_length=200, blank=True, default='')
    return_sector_from = models.CharField(
        max_length=100, blank=True, default='')
    return_sector_to = models.CharField(max_length=100, blank=True, default='')
    return_pnr = models.CharField(max_length=50, blank=True, default='')

    shirka = models.CharField(max_length=200, blank=True, default='')
    iata = models.CharField(max_length=50, blank=True, default='')
    service_no = models.CharField(max_length=50, blank=True, default='')

    def __str__(self):
        return f"Flight Info - {self.voucher.vNo}"


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
    hotel_head = models.CharField(max_length=200, blank=True, default='')
    city = models.CharField(max_length=100)
    checking_date = models.DateField()
    checkout_date = models.DateField()
    nights = models.IntegerField(default=0)
    hotel_name = models.CharField(max_length=200)
    room_type = models.CharField(
        max_length=20, choices=ROOM_TYPE_CHOICES, blank=True, default='')

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
        max_length=20, choices=TRANSFER_TYPE_CHOICES, blank=True, default='')

    def __str__(self):
        return f"{self.type_of_transfer} - {self.from_location}"

    class Meta:
        ordering = ['date']
