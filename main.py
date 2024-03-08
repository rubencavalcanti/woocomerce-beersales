from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
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
# Você pode adicionar mais rotas aqui conforme necessário, usando o mesmo padrão.

