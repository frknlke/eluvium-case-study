from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

# Define the IntentEnum with allowed values
class IntentEnum(str, Enum):
    place_order = "place_order"
    inquire_availability = "inquire_availability"
    request_invoice = "request_invoice"
    confirm_delivery_date = "confirm_delivery_date"
    change_order = "change_order"
    cancel_order = "cancel_order"
    inquire_shipping_status = "inquire_shipping_status"
    update_shipping_info = "update_shipping_info"
    follow_up = "follow_up"
    general_inquiry = "general_inquiry"
    complaint = "complaint"
    request_quote = "request_quote"
    send_payment_confirmation = "send_payment_confirmation"
    submit_documents = "submit_documents"

# Define the Product model
class Product(BaseModel):
    product_name: str = Field(..., description="The name of the product.")
    model: Optional[str] = Field(None, description="The model of the product, if provided.")
    quantity: Optional[float] = Field(None, description="The quantity of the product, if provided.")

# Define the main SalesOrderEmail model
class SalesOrderEmail(BaseModel):
    intent: IntentEnum = Field(..., description="The main purpose of the email.")
    customer_organization: str = Field(..., description="The sender's company or organization.")
    producer_organization: str = Field(..., description="The company or organization the sender is contacting.")
    people: List[str] = Field(..., description="Names of individuals mentioned in the email.")
    date_time: List[str] = Field(..., description="Last delivery date.")
    products: List[Product] = Field(..., description="An array of products mentioned in the email.")
    monetary_values: List[str] = Field(..., description="Prices, invoice amounts, or cost references.")
    addresses: List[str] = Field(..., description="Shipping or billing addresses.")
    phone_numbers: List[str] = Field(..., description="Any contact numbers mentioned.")
    email_addresses: List[str] = Field(..., description="Any contact emails mentioned.")