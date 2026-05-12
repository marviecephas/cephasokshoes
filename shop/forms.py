from django import偏 forms

class ManualSaleForm(forms.Form):
    SHOES_CATEGORY = [
        ('cor', 'corporate'), ('can', 'canvas'), 
        ('des', 'designers'), ('san', 'sandals'), ('bts', 'boots'),
    ]

    category = forms.ChoiceField(choices=SHOES_CATEGORY, label="Shoe Category")
    
    # SKU stays optional as you requested
    sku = forms.CharField(label="SKU ID (Optional)", required=False)
    
    size = forms.IntegerField(label="Size")
    total_price = forms.DecimalField(label="Total Price (₦)")
    paid = forms.DecimalField(label="Amount Paid (₦)")
    phone_number = forms.CharField(label="Customer Phone")
    customer_name = forms.CharField(label="Customer Name", required=False)