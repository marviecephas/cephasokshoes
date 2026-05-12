from .models import Customer, Shoe, Order, ShoeRequest, Content
from django.db.models import Q, Value
from .utils import send_whatsapp_message

def check_inventory(size:int, gender:str, category:str, phone_number:str, domain:str) -> list:
  """Searches the shop's database for available shoes based on specific attributes size, category and gender.
    Use this when a customer asks what is in stock, asks for a specific size (e.g., 'Do you have size 42 male canvas?'
    
    Args:
        size, gender, category, phone_number
    Returns:
        A list of matching shoe objects including SKU, price, and stock status.
    )"""
  gender_map = {'male' : 'm', 'female' : 'f', 'neutral' : 'n'}
  category_map = { 'canvas' : 'can', 'corporate' : 'cor', 'designers' : 'des', 'sandals' : 'san', 'boots' : 'bts'}
  gender_ = gender_map.get(gender.lower(), gender)
  category_ = category_map.get(category.lower(), category)
  shoes = Shoe.objects.filter(status = 'avl').filter(size = size).filter(Q(gender = gender_ ) | Q(gender = 'n'), category = category_)
  cleaned_number = phone_number.replace('whatsapp:', '')
  
  
  for s in shoes :
    msg = f"{s.sku_id} #{float(s.price)}"
    img_url = f"{domain}{s.image.url}" if s.image else None
    send_whatsapp_message(
      cleaned_number,
      msg,
      img_url
    )
    print(f'message : {msg} sent to {cleaned_number} url : {img_url}')
  return [
    {"sku_id":s.sku_id, "image_url":s.image.url if s.image else "", "price":float(s.price)} for s in shoes
    ]
    
  
def calculate_debt(phone_number:str) -> float:
  """Retrieves the total unpaid balance for a specific customer from the database.
    Use this tool whenever a customer asks 'How much do I owe?', mentions a previous payment, 
    or before finalizing a new order to check their financial standing.
    
    Args:
        phone_number: The WhatsApp phone number of the customer in string format.
    Returns:
        A float representing the total amount of money the customer still owes.
    """
  
  cleaned_number = phone_number.replace('whatsapp:', '')
  orders = Order.objects.select_related('customer').filter(customer__phone_number = cleaned_number).filter(is_picked_up = Value(True))
  order_balance = float(sum(order.balance for order in orders if order.balance > 0))
  return order_balance
  
def log_order_request(phone_number:str, sku_id:str):
  """
    Creates a temporary 'Reserved' or 'Pending Payment' order in the system. 
    Use this when a customer expresses a clear intent to buy a specific SKU but has not yet sent proof of payment. 
    This allows the shop to set aside the item and generates an expiration date for the reservation.
    
    Args:
        phone_number: Customer's phone number.
        sku_id: The unique identifier of the shoe they want.
    Returns:
        A dictionary containing the order status, ID, and the date the reservation expires.
  """
  cleaned_number = phone_number.replace('whatsapp:', '')
  customer, _ = Customer.objects.get_or_create(phone_number=cleaned_number)
  shoe = Shoe.objects.get(sku_id=sku_id)
    
  order = Order.objects.create(
        customer=customer,
        shoe=shoe,
        total_cost=shoe.price,
        payment_status='o'
  )
  order.save()
  return {
    "status" : "succesful",
    "order_id" : order.id,
    "order_expiration_date" : str(order.order_expiration_date)
  }
  
def save_user_preference(phone_number:str, lang:str) -> str:
  """
    Updates the customer's record with their preferred language (e.g., English, Pidgin, or Yoruba).
    Use this when the customer explicitly states a language preference or when you detect they 
    prefer communicating in a specific style.
    
    Args:
        phone_number: Customer's phone number.
        lang: The language (e.g., 'english', 'youruba', 'pidgin').
    Returns:
        A string indicating if the preference was successfully saved.
    """
  cleaned_number = phone_number.replace('whatsapp:', '')
  Customer.objects.filter(phone_number = cleaned_number).update(preferred_lang = lang)
  return 'success'
  
  
def update_customer_profile(phone_number:str, name:str) -> str:
  """
    Updates or fills in the 'Name' field for a customer in the database.
    Use this immediately if a customer introduces themselves (e.g., 'My name is Cephas') 
    or if you need to correct an existing name in their profile.
    
    Args:
        phone_number: The unique identifier (phone) for the customer.
        name: The name the customer wants to be called.
    Returns:
        A success message
    """
  cleaned_number = phone_number.replace('whatsapp:', '')
  Customer.objects.filter(phone_number = cleaned_number).update(name = name)
  return 'success'
  
def get_content() -> dict:
  """Fetches marketing content like fun facts and health tips."""
  queryset = Content.objects.all()
  contents = {}
  for content in queryset:
    cat = content.get_category_display()
    if cat not in contents:
      contents[cat] = []
    contents[cat].append(content.text_content)
  return contents
  
def update_shoe_request(phone_number: str, description: str, size: int) -> str:
    """
    Records a customer's interest in a shoe that is currently out of stock.
    Use this when a customer asks for a specific size or type of shoe that 
    the is not in the inventory.
    """
    cleaned_number = phone_number.replace('whatsapp:', '')
    customer, _ = Customer.objects.get_or_create(phone_number=cleaned_number)
    ShoeRequest.objects.create(
        customer=customer,
        description = description,
        requested_size=size,
    )
    return "successfull"
    
def get_preferred_lang(phone_number:str) -> str:
  """Use this to get rhe customer's preferred language for better interaction"""
  customer,_ = Customer.objects.get_or_create(phone_number = phone_number)
  return customer.preferred_lang
  
def get_user_preferred_sizes(phone_number: str) -> list:
    """Retrieves a list of shoe sizes previously ordered by this customer."""
    cleaned_number = phone_number.replace('whatsapp:', '')
    orders = Order.objects.filter(customer__phone_number=cleaned_number).values_list('shoe__size', flat=True).distinct()
    return list(orders)
    
    