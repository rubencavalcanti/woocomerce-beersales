from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import firebirdsql
from datetime import datetime

app = FastAPI()

# Detalhes da conexão com o banco de dados
host = '15.228.168.144'
port = 3050
database = '/db/beer/Coronel_Church/SYNC4_CORONEL_CHURCH.FDB'
user = 'CORONEL_CHURCH_V4'
password = 'hfPJp@Sg'

def get_connection():
    return firebirdsql.connect(host=host, port=port, database=database, user=user, password=password, charset='UTF8')

# Modelo Pydantic para o cliente
class Cliente(BaseModel):
    ID_EXTERNO: str
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
    CONTATO_TELEFONE: str
    CONTATO_CELULAR: Optional[str] = None
    CONTATO_EMAIL: Optional[EmailStr] = None
    CONTATO_OUTROS: Optional[str] = None
    ID_EMPRESA: int
    ID_VENDEDOR: Optional[int] = None
    ID_TABELA_PRECO: Optional[int] = None
    LIMITE_CREDITO: Optional[float] = None
    ID_GRUPO_CLIENTE: Optional[int] = 1
    ID_FORMA_PAGAMENTO: Optional[int] = None
    ID_PRAZO: Optional[int] = None
    DIA_ATENDIMENTO: Optional[int] = None
    PERIODICIDADE: Optional[int] = None
    OBSERVACAO: Optional[str] = None
    INATIVO: bool  # Agora é um booleano

class Pedido(BaseModel):
    ID_PEDIDO: int
    ID_CLIENTE: int
    ID_VENDEDOR: Optional[int] = None
    TIPO_PEDIDO: int
    STATUS: int
    ID_CAMPANHA: Optional[int] = None
    QUANTIDADE_ITENS: int
    VALOR_TOTAL: float
    DESCONTO: float
    OBSERVACAO: str = ''
    DATA_PEDIDO: datetime = Field(default_factory=datetime.now)
    DATA_ENTREGA_PREVISTA: Optional[datetime] = None
    ID_ENDERECO_ENTREGA: Optional[int] = None
    ID_FORMA_PAGAMENTO: Optional[int] = None
    ID_PRAZO_PAGAMENTO: Optional[int] = None
    ID_TRANSPORTADORA: Optional[int] = None
    FRETE: Optional[float] = None
    SEGURO: Optional[float] = None
    URGENTE: bool
    REQUER_APROVACAO: bool
    ID_EMPRESA: int
    ID_MOEDA: int


@app.get("/test_db_connection")
async def test_connection():
    try:
        conn = get_connection()
        return {"message": "Conexão bem-sucedida ao banco de dados"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar ao banco de dados: {e}")

@app.get("/verificar_cliente")
async def verificar_cliente(cpf_cnpj: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_BEERSALES FROM GET_CLIENTE ('01.01.2000') WHERE CPF_CNPJ = ?", (cpf_cnpj,))
        result = cursor.fetchone()
        if result:
            return {"message": "Cliente encontrado", "ID_BEERSALES": result[0]}
        else:
            return {"message": "Cliente não encontrado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar o cliente: {e}")

@app.post("/cadastrar_cliente")
async def cadastrar_cliente(cliente: Cliente):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cod_retorno = cursor.callproc('POST_CLIENTE_V4', [
            cliente.ID_EXTERNO,
            cliente.NOME,
            cliente.APELIDO,
            cliente.CPF_CNPJ,
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
        # Verifique o código de retorno e responda de acordo
        if cod_retorno == 202:
            return {"message": "Cliente cadastrado com sucesso", "COD_RETORNO": cod_retorno}
        else:
            # Handle other return codes as needed
            return {"message": "Erro ao cadastrar cliente", "COD_RETORNO": cod_retorno}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar cliente: {e}")

@app.post("/cadastrar_pedido")
async def cadastrar_pedido(pedido: Pedido):
    try:
        conn = get_connection()  # Esta função deve ser definida para obter uma conexão com seu banco de dados
        cursor = conn.cursor()
        resultado_procedimento = cursor.callproc('POST_PEDIDO_V5', [
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

        # Substitua esta linha pelo código que verifica o sucesso da operação
        # baseando-se no seu procedimento armazenado específico.
        cod_retorno = resultado_procedimento[-1]  # Assumindo que o código de retorno é o último elemento
        if cod_retorno == 202:  # Substitua "algum_valor_para_sucesso" pelo valor correspondente
            return {"message": "Pedido cadastrado com sucesso", "COD_RETORNO": cod_retorno}
        else:
            return {"message": "Erro ao cadastrar pedido", "COD_RETORNO": cod_retorno}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar pedido: {e}")

@app.post("/cadastrar_item_pedido")
async def cadastrar_item_pedido(pedido: Pedido):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        resultado_procedimento = cursor.callproc('POST_PEDIDO_ITEM', [
            pedido.ID_PEDIDO,
            pedido.ID_ITEM,
            pedido.ID_PRODUTO,
            pedido.QUANTIDADE,
            pedido.PRECO_UNITARIO,
            pedido.DESCONTO,
            pedido.OUTRAS_DESPESAS,
            pedido.PRECO_TOTAL
        ])
        conn.commit()
        # A resposta do procedimento armazenado normalmente é uma tupla, e o último elemento geralmente contém o código de retorno
        cod_retorno = resultado_procedimento[-1]
        # Verifique o código de retorno e responda de acordo
        if cod_retorno == 202:
            return {"message": "Item do pedido cadastrado com sucesso", "COD_RETORNO": cod_retorno}
        elif cod_retorno == 412:
            motivo = "Aqui você pode extrair o motivo da falha a partir do procedimento ou definir uma mensagem padrão"
            return {"message": "Inconsistência nos dados do item do pedido", "COD_RETORNO": cod_retorno, "MOTIVO": motivo}
        else:
            # Handle other return codes as needed
            return {"message": "Erro ao cadastrar item do pedido", "COD_RETORNO": cod_retorno}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar item do pedido: {e}")

# Você pode adicionar mais rotas aqui conforme necessário, usando o mesmo padrão.