from fastapi import FastAPI, HTTPException
from models import Cliente, Pedido, ItemPedido
from typing import List, Optional
import firebirdsql


app = FastAPI()

# Detalhes da conexão com o banco de dados
host = '15.228.168.144'
port = 3050
database = '/db/beer/Coronel_Church/SYNC4_CORONEL_CHURCH.FDB'
user = 'CORONEL_CHURCH_V4'
password = 'hfPJp@Sg'

def get_connection():
    return firebirdsql.connect(host=host, port=port, database=database, user=user, password=password, charset='UTF8')

def get_cliente_id(cpf: str) -> int:
    try:
        # Estabelecendo a conexão com o banco de dados
        conn = get_connection()
        cursor = conn.cursor()
        # Executando a consulta SQL
        cursor.execute("SELECT ID_CLIENTE FROM CLIENTE WHERE CPF_CNPJ = ?", (cpf,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return result[0]
        else:
            return None
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {e}")
        return None

@app.get("/test_db_connection")
async def test_connection():
    try:
        get_connection() # Esta função deve ser definida para obter uma conexão com seu banco de dados
        return {"message": "Conexão bem-sucedida ao banco de dados"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar ao banco de dados: {e}")

# verifica se o cliente já existe
@app.get("/verificar_cliente")
async def verificar_cliente(cpf_cnpj: str):
    try:
        conn = get_connection() # Esta função deve ser definida para obter uma conexão com seu banco de dados
        cursor = conn.cursor()
        cursor.execute("SELECT ID_BEERSALES FROM GET_CLIENTE ('01.01.2000') WHERE CPF_CNPJ = ?", (cpf_cnpj,))
        cod_retorno = cursor.fetchone()
        
        if cod_retorno[0] == None:
            return {"message": "cliente encontrado com sucesso", "COD_RETORNO": cod_retorno}   
        else:
            return {"message": "cliente nao cadastrado", "COD_RETORNO": cod_retorno}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"cliente nao cadastrado: {e}")

#cadastra um novo cliente
@app.post("/cadastrar_cliente")
async def cadastrar_cliente(cliente: Cliente):
    cliente_cpf = cliente.CPF_CNPJ.replace('.', '').replace('-', '')
    try:
        conn = get_connection() # Esta função deve ser definida para obter uma conexão com seu banco de dados
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

#Busca o id_cliente pelo 
@app.get("/buscar_cliente/{cpf}")
async def buscar_cliente(cpf: str):
    id_cliente = get_cliente_id(cpf)
    if id_cliente is not None:
        return {"ID_CLIENTE": id_cliente}
    else:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

#cadastra o pedido
@app.post("/cadastrar_pedido")
async def cadastrar_pedido(pedido: Pedido):
    try:
        conn = get_connection()  # Esta função deve ser definida para obter uma conexão com seu banco de dados
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

#cadastra os itens dos pedidos
@app.post("/cadastrar_item_pedido")
async def cadastrar_item_pedido(pedidoItem: ItemPedido):
    try:
        conn = get_connection()  # Esta função deve ser definida para obter uma conexão com seu banco de dados
        cursor = conn.cursor()

        id_pedido = int(pedidoItem.ID_PEDIDO)
        id_item = int(pedidoItem.ID_ITEM)
        id_produto = int(pedidoItem.ID_PRODUTO)
        quantidade = int(pedidoItem.QUANTIDADE)
        preco_unitario = float(pedidoItem.PRECO_UNITARIO)
        desconto = float(pedidoItem.DESCONTO)
        outras_despesas = float(pedidoItem.OUTRAS_DESPESAS)
        preco_total = float(pedidoItem.PRECO_TOTAL)
        
        cod_retorno = cursor.callproc('POST_PEDIDO_ITEM', [
                id_pedido,
                id_item,
                id_produto,
                quantidade,
                preco_unitario,
                desconto,
                outras_despesas,
                preco_total
            ])
        conn.commit()
        
        if cod_retorno[0] == 202:
            return {"message": "CONEXÃO BEM ESTABELICIDA", "COD_RETORNO": cod_retorno}
        else:
            return {f"Erro ao conectar com banco: {e}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar com banco: {e}")
