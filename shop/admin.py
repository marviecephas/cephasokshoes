from django.contrib import messages
from django.contrib import admin
from .models import Shoe, Customer, Order, ShoeRequest, Content, NewStockAnnouncement
from django.db.models import Count




        
admin.site.site_header = 'CEPHAS OK SHOES'
admin.site.index_title = 'SHOP administration'

from django.template.response import TemplateResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Count
from .services import cleanup_expired_orders

@staff_member_required
def admin_dashboard_view(request):
    # Your existing logic to calculate stats
    cleanup_expired_orders()
    last_month = timezone.now() - timezone.timedelta(days=30)
    hot_item = Shoe.objects.values('category', 'size').annotate(
        count=Count('sku_id')).order_by('-count').first()

    context = {
        # This keeps the Django Admin sidebar and top bar visible
        'title': 'Business Dashboard',
        'summary': {
            'sold_last_month': Order.objects.filter(date_ordered__gte = last_month).filter(shoe__status = 'sold').count(),
            'on_order': Order.objects.filter(is_picked_up=False).count(),
            'recent_requests': ShoeRequest.objects.all().order_by('-id')[:3],
            'hot_seller': hot_item,
        }
    }
    # Link this to your new UI template
    return TemplateResponse(request, "admin/shop/dashboard.html", context)
    
    
from django.urls import path

# This "hooks" your new page into the existing admin URLs
def get_admin_urls(urls):
    def get_urls():
        custom_urls = [
            # This creates the address: /admin/business-dashboard/
            path('business-dashboard/', admin.site.admin_view(admin_dashboard_view), name='business-dashboard'),
        ]
        return custom_urls + urls()
    return get_urls

# Apply the hook to the default admin site
admin.site.get_urls = get_admin_urls(admin.site.get_urls)
        
@admin.register(Shoe)
class ShoeAdmin(admin.ModelAdmin):
    # This shows the most important shoe details in a table
    list_display = ('sku_id', 'category', 'size', 'price', 'status')
    # Filter by category or status on the right sidebar
    list_filter = ('category', 'status', 'gender')
    # Search for specific SKUs easily
    search_fields = ('sku_id',)
    
    exclude = ('sku_id',)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change: # Only show on new creation
            messages.success(request, f"🚀 SHOE ADDED! WRITE THIS ON THE SHOE: {obj.sku_id}")

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'name')
    search_fields = ('phone_number', 'name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # This helps your dad see exactly who owes money at a glance
    list_display = ('customer', 'shoe', 'total_cost', 'amount_paid', 'payment_status', 'date_ordered', 'is_picked_up')
    list_display_links = ('amount_paid', 'is_picked_up')
    list_filter = ( 'is_picked_up', 'payment_status')
    readonly_fields = ('payment_status',)
    # Search by customer name or phone number
    search_fields = ('customer__name', 'customer__phone_number', 'shoe__sku_id')
    
@admin.register(ShoeRequest)
class ShoeRequestAdmin(admin.ModelAdmin):
    list_display = ('customer', 'description', 'requested_size')
    # Add the shoe selector to the edit page
    fields = ('customer', 'description', 'requested_size', 'fulfilled_by')

    def save_model(self, request, obj, form, change):
        if obj.fulfilled_by:
            # 1. Prepare the message data
            phone = obj.customer.phone_number
            shoe_name = obj.description
            shoe_size = obj.requested_size
            shoe_img = obj.fulfilled_by.image
            message_body = ''
            img_url = None
            
            # 2. Get the Image URL
            # Assuming your Shoe model has an 'image' field
            if shoe_img:
                img_url = request.build_absolute_uri(shoe_img.url)
                print(img_url)
                message_body = f"Good news! Your request for {shoe_name} size {shoe_size} is ready. Check out the photo."
            else:
                message_body = f"Good news! Your request for {shoe_name} size {shoe_size} is ready."

            # 3. Trigger your utility function
            try:
                from .utils import send_whatsapp_message # Adjust import path
                send_whatsapp_message(to_number=phone, body=message_body, media_url = img_url)
                messages.success(request, f"🚀 WhatsApp sent to {phone}")
                
                # 4. Delete the request now that it's done
                obj.delete()
                return # Exit so we don't save a deleted object
            except Exception as e:
                messages.error(request, f"❌ Failed to send WhatsApp: {str(e)}")

        super().save_model(request, obj, form, change)

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('category', 'text_content')


@admin.register(NewStockAnnouncement)
class NewStockAnnouncementAdmin(admin.ModelAdmin):
    # This ensures he only sees the date and doesn't try to edit anything
    readonly_fields = ('date_triggered',) 
    