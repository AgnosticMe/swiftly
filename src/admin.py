from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Customer)
admin.site.register(models.Courier)
admin.site.register(models.Job)

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
