from django.contrib import admin
from django.contrib.auth.models import User
from .models import Voucher, FlightInformation, Mautamer, VoucherMautamer, Hotel, Transportation


class FlightInformationInline(admin.StackedInline):
    model = FlightInformation
    extra = 0
    max_num = 1


class VoucherMautamerInline(admin.TabularInline):
    model = VoucherMautamer
    extra = 1
    autocomplete_fields = ['mautamer']


class HotelInline(admin.TabularInline):
    model = Hotel
    extra = 1


class TransportationInline(admin.TabularInline):
    model = Transportation
    extra = 1


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ['vNo', 'agentName', 'status', 'user', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['vNo', 'agentName', 'user__username']
    inlines = [FlightInformationInline, VoucherMautamerInline,
               HotelInline, TransportationInline]


@admin.register(FlightInformation)
class FlightInformationAdmin(admin.ModelAdmin):
    list_display = ['voucher', 'departure_date',
                    'return_date', 'sector_from', 'sector_to']
    search_fields = ['voucher__vNo']


@admin.register(Mautamer)
class MautamerAdmin(admin.ModelAdmin):
    list_display = ['pax_name', 'passport', 'user', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['pax_name', 'passport', 'user__username']
    ordering = ['user', 'pax_name']


@admin.register(VoucherMautamer)
class VoucherMautamerAdmin(admin.ModelAdmin):
    list_display = ['voucher', 'mautamer', 'get_agent']
    list_filter = ['voucher__user']
    search_fields = ['voucher__vNo',
                     'mautamer__pax_name', 'mautamer__passport']

    def get_agent(self, obj):
        return obj.voucher.user.username
    get_agent.short_description = 'Agent'


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['hotel_name', 'city',
                    'checking_date', 'checkout_date', 'voucher']
    search_fields = ['hotel_name', 'city', 'voucher__vNo']


@admin.register(Transportation)
class TransportationAdmin(admin.ModelAdmin):
    list_display = ['type_of_transfer', 'from_location', 'date', 'voucher']
    search_fields = ['from_location', 'voucher__vNo']
