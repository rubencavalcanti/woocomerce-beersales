from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import firebirdsql
import json

app = FastAPI()

# Detalhes da conexão com o banco de dados
host = '15.228.168.144'
port = 3050
database = '/db/beer/Coronel_Church/SYNC4_CORONEL_CHURCH.FDB'
user = 'CORONEL_CHURCH_V4'
password = 'hfPJp@Sg'

# Função para obter a conexão com o banco de dados
def get_connection():
    return firebirdsql.connect(host=host, port=port, database=database, user=user, password=password, charset='UTF8')

# Modelos de dados
class Cliente(BaseModel):
    ID_EXTERNO: int
    NOME: str
    APELIDO: str
    CPF_CNPJ: str
    IE: Optional[str] = None
    ENDERECO_RUA: str
    ENDERECO_NUMERO: str
    ENDERECO_COMPLEMENTO: Optional[str] = None
    ENDERECO_CEP: str
    ENDERECO_BAIRRO: str
    ENDERECO_CIDADE: str
    ENDERECO_UF: str
    CONTATO_TELEFONE: Optional[str] = None
    CONTATO_CELULAR: Optional[str] = None
    CONTATO_EMAIL: Optional[str] = None
    CONTATO_OUTROS: Optional[str] = None
    ID_EMPRESA: int
    ID_VENDEDOR: int
    ID_TABELA_PRECO: int
    LIMITE_CREDITO: float
    ID_GRUPO_CLIENTE: int
    ID_FORMA_PAGAMENTO: int
    ID_PRAZO: int
    DIA_ATENDIMENTO: Optional[str] = None
    PERIODICIDADE: Optional[str] = None
    OBSERVACAO: Optional[str] = None
    INATIVO: bool

class Pedido(BaseModel):
    ID_PEDIDO: int
    ID_CLIENTE: int
    ID_VENDEDOR: int
    TIPO_PEDIDO: str
    STATUS: str
    ID_CAMPANHA: Optional[int] = None
    QUANTIDADE_ITENS: int
    VALOR_TOTAL: float
    DESCONTO: Optional[float] = None
    OBSERVACAO: Optional[str] = None
    DATA_PEDIDO: str
    DATA_ENTREGA_PREVISTA: str
    ID_ENDERECO_ENTREGA: Optional[int] = None
    ID_FORMA_PAGAMENTO: int
    ID_PRAZO_PAGAMENTO: int
    ID_TRANSPORTADORA: Optional[int] = None
    FRETE: Optional[float] = None
    SEGURO: Optional[float] = None
    URGENTE: bool
    REQUER_APROVACAO: bool
    ID_EMPRESA: int
    ID_MOEDA: int

class ItemPedido(BaseModel):
    ID_PEDIDO: int
    ID_ITEM: int
    ID_PRODUTO: int
    QUANTIDADE: int
    PRECO_UNITARIO: float
    DESCONTO: Optional[float] = None
    OUTRAS_DESPESAS: Optional[float] = None
    PRECO_TOTAL: float

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

@app.get("/test_db_connection")
async def test_connection():
    try:
        get_connection()  # Esta função deve ser definida para obter uma conexão com seu banco de dados
        return {"message": "Conexão bem-sucedida ao banco de dados"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar ao banco de dados: {e}")

# Verifica se o cliente já existe
@app.get("/verificar_cliente")
async def verificar_cliente(cpf_cnpj: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_BEERSALES FROM GET_CLIENTE ('01.01.2000') WHERE CPF_CNPJ = ?", (cpf_cnpj,))
        cod_retorno = cursor.fetchone()
        if cod_retorno and cod_retorno[0] is not None:
            return {"message": "cliente encontrado com sucesso", "COD_RETORNO": cod_retorno}
        else:
            return {"message": "cliente não cadastrado", "COD_RETORNO": cod_retorno}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar cliente: {e}")

# Cadastra um novo cliente
@app.post("/cadastrar_cliente")
async def cadastrar_cliente(cliente: Cliente):
    cliente_cpf = cliente.CPF_CNPJ.replace('.', '').replace('-', '')
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cod_retorno = cursor.callproc('POST_CLIENTE_V4', [
            cliente.ID_EXTERNO,
            cliente.NOME,
            cliente.APELIDO,
            cliente_cpf,
            cliente.IE,
            cliente.ENDERECO_RUA,
            cliente.ENDERECO_NUMERO,
            cliente.ENDERECO_COMPLEMENTO,
            cliente.ENDERECO_CEP,
            cliente.ENDERECO_BAIRRO,
            cliente.ENDERECO_CIDADE,
            cliente.ENDERECO_UF,
            cliente.CONTATO_TELEFONE,
            cliente.CONTATO_CELULAR,
            cliente.CONTATO_EMAIL,
            cliente.CONTATO_OUTROS,
            cliente.ID_EMPRESA,
            cliente.ID_VENDEDOR,
            cliente.ID_TABELA_PRECO,
            cliente.LIMITE_CREDITO,
            cliente.ID_GRUPO_CLIENTE,
            cliente.ID_FORMA_PAGAMENTO,
            cliente.ID_PRAZO,
            cliente.DIA_ATENDIMENTO,
            cliente.PERIODICIDADE,
            cliente.OBSERVACAO,
            cliente.INATIVO  # Diretamente como um booleano
        ])
        conn.commit()
        if cod_retorno[0] == 202:
            return {"message": "cliente cadastrado com sucesso", "COD_RETORNO": cod_retorno}
        else:
            return {"message": "Houve um erro ao cadastrar o cliente", "COD_RETORNO": cod_retorno}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar cliente: {e}")

# Busca o ID do cliente pelo CPF
@app.get("/buscar_cliente/{cpf}")
async def buscar_cliente(cpf: str):
    id_cliente = get_cliente_id(cpf)
    if id_cliente is not None:
        return {"ID_CLIENTE": id_cliente}
    else:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

# Cadastra o pedido
@app.post("/cadastrar_pedido")
async def cadastrar_pedido(pedido: Pedido):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cod_retorno = cursor.callproc('POST_PEDIDO_V5', [
            pedido.ID_PEDIDO,
            pedido.ID_CLIENTE,
            pedido.ID_VENDEDOR,
            pedido.TIPO_PEDIDO,
            pedido.STATUS,
            pedido.ID_CAMPANHA,
            pedido.QUANTIDADE_ITENS,
            pedido.VALOR_TOTAL,
            pedido.DESCONTO,
            pedido.OBSERVACAO,
            pedido.DATA_PEDIDO,
            pedido.DATA_ENTREGA_PREVISTA,
            pedido.ID_ENDERECO_ENTREGA,
            pedido.ID_FORMA_PAGAMENTO,
            pedido.ID_PRAZO_PAGAMENTO,
            pedido.ID_TRANSPORTADORA,
            pedido.FRETE,
            pedido.SEGURO,
            pedido.URGENTE,
            pedido.REQUER_APROVACAO,
            pedido.ID_EMPRESA,
            pedido.ID_MOEDA
        ])
        conn.commit()
        if cod_retorno[0] == 202:
            return {"message": "Pedido cadastrado com sucesso", "COD_RETORNO": cod_retorno}
        else:
            return {"message": "Houve um erro ao cadastrar o pedido", "COD_RETORNO": cod_retorno}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar pedido: {e}")

# Cadastra os itens do pedido
@app.post("/cadastrar_item_pedido")
async def cadastrar_item_pedido(pedidoItem: ItemPedido):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cod_retorno = cursor.callproc('POST_PEDIDO_ITEM', [
            pedidoItem.ID_PEDIDO,
            pedidoItem.ID_ITEM,
            pedidoItem.ID_PRODUTO,
            pedidoItem.QUANTIDADE,
            pedidoItem.PRECO_UNITARIO,
            pedidoItem.DESCONTO,
            pedidoItem.OUTRAS_DESPESAS,
            pedidoItem.PRECO_TOTAL
        ])
        conn.commit()
        if cod_retorno[0] == 202:
            return {"message": "Item do pedido cadastrado com sucesso", "COD_RETORNO": cod_retorno}
        else:
            return {"message": "Houve um erro ao cadastrar o item do pedido", "COD_RETORNO": cod_retorno}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar item do pedido: {e}")

# Recebe o webhook do WooCommerce
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

        # Extrair dados do pedido e do cliente
        billing_address = order.billing
        shipping_address = order.shipping
        items = order.line_items

        # Verificar se o cliente já está cadastrado
        cliente_id = get_cliente_id(billing_address.cpf)
        if not cliente_id:
            # Cadastrar o cliente
            novo_cliente = Cliente(
                ID_EXTERNO=order.customer_id,
                NOME=billing_address.first_name + ' ' + billing_address.last_name,
                APELIDO=billing_address.first_name,
                CPF_CNPJ=billing_address.cpf,
                IE=billing_address.ie or '',
                ENDERECO_RUA=billing_address.address_1,
                ENDERECO_NUMERO=billing_address.number or '',
                ENDERECO_COMPLEMENTO=billing_address.address_2 or '',
                ENDERECO_CEP=billing_address.postcode,
                ENDERECO_BAIRRO=billing_address.neighborhood or '',
                ENDERECO_CIDADE=billing_address.city,
                ENDERECO_UF=billing_address.state,
                CONTATO_TELEFONE=billing_address.phone,
                CONTATO_CELULAR=billing_address.cellphone or '',
                CONTATO_EMAIL=billing_address.email,
                CONTATO_OUTROS='',
                ID_EMPRESA=1,  # Supondo ID_EMPRESA como 1 para todos os clientes
                ID_VENDEDOR=1,  # Supondo ID_VENDEDOR como 1 para todos os clientes
                ID_TABELA_PRECO=1,  # Supondo ID_TABELA_PRECO como 1 para todos os clientes
                LIMITE_CREDITO=0,  # Supondo LIMITE_CREDITO como 0 para todos os clientes
                ID_GRUPO_CLIENTE=1,  # Supondo ID_GRUPO_CLIENTE como 1 para todos os clientes
                ID_FORMA_PAGAMENTO=1,  # Supondo ID_FORMA_PAGAMENTO como 1 para todos os clientes
                ID_PRAZO=1,  # Supondo ID_PRAZO como 1 para todos os clientes
                DIA_ATENDIMENTO='',
                PERIODICIDADE='',
                OBSERVACAO='',
                INATIVO=False
            )
            response = await cadastrar_cliente(novo_cliente)
            if response['COD_RETORNO'][0] != 202:
                raise HTTPException(status_code=500, detail="Erro ao cadastrar cliente no banco de dados")

            cliente_id = get_cliente_id(billing_address.cpf)

        # Cadastrar o pedido
        novo_pedido = Pedido(
            ID_PEDIDO=order.id,
            ID_CLIENTE=cliente_id,
            ID_VENDEDOR=1,  # Supondo ID_VENDEDOR como 1 para todos os pedidos
            TIPO_PEDIDO='V',  # Supondo TIPO_PEDIDO como 'V' (venda) para todos os pedidos
            STATUS=order.status,
            ID_CAMPANHA=None,
            QUANTIDADE_ITENS=len(items),
            VALOR_TOTAL=float(order.total),
            DESCONTO=float(order.discount_total),
            OBSERVACAO=order.customer_note or '',
            DATA_PEDIDO=order.date_created,
            DATA_ENTREGA_PREVISTA=order.date_modified,  # Usando a data de modificação como data de entrega prevista
            ID_ENDERECO_ENTREGA=None,  # Supondo ID_ENDERECO_ENTREGA como None para todos os pedidos
            ID_FORMA_PAGAMENTO=1,  # Supondo ID_FORMA_PAGAMENTO como 1 para todos os pedidos
            ID_PRAZO_PAGAMENTO=1,  # Supondo ID_PRAZO_PAGAMENTO como 1 para todos os pedidos
            ID_TRANSPORTADORA=None,  # Supondo ID_TRANSPORTADORA como None para todos os pedidos
            FRETE=0.0,
            SEGURO=0.0,
            URGENTE=False,
            REQUER_APROVACAO=False,
            ID_EMPRESA=1,  # Supondo ID_EMPRESA como 1 para todos os pedidos
            ID_MOEDA=1  # Supondo ID_MOEDA como 1 para todos os pedidos
        )
        response = await cadastrar_pedido(novo_pedido)
        if response['COD_RETORNO'][0] != 202:
            raise HTTPException(status_code=500, detail="Erro ao cadastrar pedido no banco de dados")

        # Cadastrar os itens do pedido
        for item in items:
            novo_item = ItemPedido(
                ID_PEDIDO=order.id,
                ID_ITEM=item.id,
                ID_PRODUTO=item.product_id,
                QUANTIDADE=item.quantity,
                PRECO_UNITARIO=float(item.price),
                DESCONTO=float(item.subtotal_tax),
                OUTRAS_DESPESAS=0.0,
                PRECO_TOTAL=float(item.total)
            )
            response = await cadastrar_item_pedido(novo_item)
            if response['COD_RETORNO'][0] != 202:
                raise HTTPException(status_code=500, detail="Erro ao cadastrar item do pedido no banco de dados")

        return {"message": "Pedido recebido e processado com sucesso"}

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao decodificar JSON: {e}")
    except HTTPException as e:
        print("HTTP Exception:", e.detail)
        raise e
    except Exception as e:
        print("Erro:", e)
        raise HTTPException(status_code=500, detail=f"Erro ao processar pedido: {e}")
