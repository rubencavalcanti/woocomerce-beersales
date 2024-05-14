from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import json

app = FastAPI()

class MetaData(BaseModel):
    id: int
    key: str
    value: str

class BillingAddress(BaseModel):
    first_name: str
    last_name: str
    company: Optional[str] = None
    address_1: str
    address_2: Optional[str] = None
    city: str
    state: str
    postcode: str
    country: str
    email: str
    phone: str
    number: Optional[str] = None
    neighborhood: Optional[str] = None
    persontype: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    cnpj: Optional[str] = None
    ie: Optional[str] = None
    birthdate: Optional[str] = None
    gender: Optional[str] = None
    cellphone: Optional[str] = None

class ShippingAddress(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    address_1: Optional[str] = None
    address_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    number: Optional[str] = None
    neighborhood: Optional[str] = None

class LineItem(BaseModel):
    id: int
    name: str
    product_id: int
    variation_id: int
    quantity: int
    tax_class: Optional[str] = None
    subtotal: str
    subtotal_tax: str
    total: str
    total_tax: str
    taxes: List[dict]
    meta_data: List[MetaData]
    sku: str
    price: float
    image: dict
    parent_name: Optional[str] = None

class WooCommerceOrder(BaseModel):
    id: int
    parent_id: int
    status: str
    currency: str
    version: str
    prices_include_tax: bool
    date_created: str
    date_modified: str
    discount_total: str
    discount_tax: str
    shipping_total: str
    shipping_tax: str
    cart_tax: str
    total: str
    total_tax: str
    customer_id: int
    order_key: str
    billing: BillingAddress
    shipping: Optional[ShippingAddress] = None
    payment_method: str
    payment_method_title: str
    transaction_id: Optional[str] = None
    customer_ip_address: str
    customer_user_agent: str
    created_via: str
    customer_note: Optional[str] = None
    date_completed: Optional[str] = None
    date_paid: Optional[str] = None
    cart_hash: str
    number: str
    meta_data: List[MetaData]
    line_items: List[LineItem]
    tax_lines: List[dict]
    shipping_lines: List[dict]
    fee_lines: List[dict]
    coupon_lines: List[dict]
    refunds: List[dict]
    payment_url: str
    is_editable: bool
    needs_payment: bool
    needs_processing: bool
    date_created_gmt: str
    date_modified_gmt: str
    date_completed_gmt: Optional[str] = None
    date_paid_gmt: Optional[str] = None
    currency_symbol: str
    _links: dict
    shipping_method: Optional[str] = None  # Tornando shipping_method opcional

@app.post("/webhook/woocommerce")
async def receive_woocommerce_webhook(request: Request):
    try:
        body = await request.body()
        if not body:
            raise HTTPException(status_code=400, detail="Corpo da requisição está vazio")

        print("Raw body:", body.decode('utf-8'))

        order_data = json.loads(body)
        print("Parsed JSON data:", order_data)

        order = WooCommerceOrder(**order_data)

        # Variáveis para armazenar os dados
        order_id = order.id
        order_status = order.status
        date_created = order.date_created
        date_modified = order.date_modified
        total_value = order.total
        discount_total = order.discount_total
        customer_note = order.customer_note
        payment_method = order.payment_method
        shipping_method = order.shipping_method
        shipping_total = order.shipping_total

        billing_address = order.billing
        shipping_address = order.shipping

        items = order.line_items

        # Variáveis adicionais de meta_data
        delivery_date = None
        for meta in order.meta_data:
            if meta.key == "_billing_data":
                delivery_date = meta.value
                break

        # Exibir os dados capturados
        print("Recebido pedido do WooCommerce:")
        print("ID do Pedido:", order_id)
        print("Status do Pedido:", order_status)
        print("Data de Criação:", date_created)
        print("Data de Modificação:", date_modified)
        print("Valor Total:", total_value)
        print("Desconto Total:", discount_total)
        print("Observações do Cliente:", customer_note)
        print("Método de Pagamento:", payment_method)
        print("Método de Envio:", shipping_method)
        print("Valor Total do Envio:", shipping_total)

        print("Endereço de Cobrança:")
        print("Primeiro Nome:", billing_address.first_name)
        print("Último Nome:", billing_address.last_name)
        print("E-mail:", billing_address.email)
        print("Telefone:", billing_address.phone)
        print("Endereço 1:", billing_address.address_1)
        print("Endereço 2:", billing_address.address_2)
        print("Cidade:", billing_address.city)
        print("Estado/UF:", billing_address.state)
        print("CEP:", billing_address.postcode)
        print("País:", billing_address.country)

        if shipping_address:
            print("Endereço de Envio:")
            print("Primeiro Nome:", shipping_address.first_name)
            print("Último Nome:", shipping_address.last_name)
            print("Endereço 1:", shipping_address.address_1)
            print("Endereço 2:", shipping_address.address_2)
            print("Cidade:", shipping_address.city)
            print("Estado/UF:", shipping_address.state)
            print("CEP:", shipping_address.postcode)
            print("País:", shipping_address.country)

        print("Itens do Pedido:")
        for item in items:
            print("ID do Item:", item.id)
            print("ID do Produto:", item.product_id)
            print("Nome do Produto:", item.name)
            print("Quantidade:", item.quantity)
            print("Subtotal:", item.subtotal)
            print("Total:", item.total)

        print("Data de Entrega:", delivery_date)

        return {"message": "Pedido recebido com sucesso"}
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao decodificar JSON: {e}")
    except HTTPException as e:
        print("HTTP Exception:", e.detail)
        raise e
    except Exception as e:
        print("Erro:", e)
        raise HTTPException(status_code=500, detail=f"Erro ao processar webhook do WooCommerce: {e}")

@app.post("/webhook/woocommerce_test")
async def webhook_test(request: Request):
    try:
        body = await request.body()
        if not body:
            raise HTTPException(status_code=400, detail="Corpo da requisição está vazio")
        print("Webhook Test Raw body:", body.decode('utf-8'))
        return {"message": "Webhook de teste recebido com sucesso"}
    except Exception as e:
        print("Erro no webhook de teste:", e)
        raise HTTPException(status_code=500, detail=f"Erro ao processar webhook de teste do WooCommerce: {e}")
