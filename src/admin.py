import random
import string
from django.contrib import admin, messages
from django.conf import settings
from paypalrestsdk import configure, Payout

from . import models

configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})

def payout_to_courier(modeladmin, request, queryset):
    payout_items = []
    transaction_querysets = []

    # Step 1 - Get all the valid couriers in the queryset
    for courier in queryset:
        if courier.paypal_email:
            courier_in_transactions = models.Transaction.objects.filter(
                job__courier=courier,
                status=models.Transaction.IN_STATUS,
            )

            if courier_in_transactions:
                transaction_querysets.append(courier_in_transactions)
                balance = sum(i.amount for i in courier_in_transactions)
                payout_items.append({
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": f"{balance * 0.8:.2f}",
                        "currency": "USD"
                    },
                    "receiver": courier.paypal_email,
                    "note": "Thank you.",
                    "sender_item_id": str(courier.id),
                })

    # Step 2 - Send payout batch and email to receivers
    sender_batch_id = ''.join(random.choice(string.ascii_uppercase) for i in range(12))
    payout = Payout({
        "sender_batch_header": {
            "sender_batch_id": sender_batch_id,
            "email_subject": "You have a payment"
        },
    "items": payout_items,
    })

    # Step 3 - Execute payout process and Update transaction's status to "OUT" if success
    try:
        if payout.create():
            for t in transaction_querysets:
                t.update(status=models.Transaction.OUT_STATUS)
            messages.success(request, f"payout {payout.batch_header.payout_batch_id} created successfully")
        else:
            messages.error(request, payout.error)
        
    except Exception as e:
        messages.error(request, str(e))

payout_to_courier.short_description = "Payout to Couriers"

# Register your models here.

@admin.register(models.Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ['user_full_name', 'paypal_email', 'balance',]
    actions = [payout_to_courier]

    def user_full_name(self, obj):
        return obj.user.get_full_name()

    def balance(self, obj):
        return round(sum(t.amount for t in models.Transaction.objects.filter(job__courier=obj, status=models.Transaction.IN_STATUS)) * 0.8, 2)



@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('category_name',)}
    list_display = ['category_name', 'slug']


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['stripe_payment_intent_id', 'courier_paypal_email', 'customer', 'courier', 'job', 'amount', 'status', 'created_at']
    list_display_links = ['stripe_payment_intent_id', 'courier_paypal_email']
    list_filter = ['status', ]

    def customer(self, obj):
        return obj.job.customer

    def courier(self, obj):
        return obj.job.courier

    def courier_paypal_email(self, obj):
        return obj.job.courier.paypal_email if obj.job.courier else None


admin.site.register(models.Customer)
admin.site.register(models.Job)