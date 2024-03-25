from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from models import Cliente, Pedido, Token, TokenData, User, UserInDB
from typing import List, Optional
import firebirdsql
import bcrypt


app = FastAPI()

# Detalhes da conexão com o banco de dados
host = '15.228.168.144'
port = 3050
database = '/db/beer/Coronel_Church/SYNC4_CORONEL_CHURCH.FDB'
user = 'CORONEL_CHURCH_V4'
password = 'hfPJp@Sg'

def get_connection():
    return firebirdsql.connect(host=host, port=port, database=database, user=user, password=password, charset='UTF8')


# Definição das suas configurações JWT
SECRET_KEY = "uma_chave_secreta_muito_segura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "usuario": {
        "username": "usuario",
        "hashed_password": "$2b$12$W3zbr5MROi.Hj2mZ8.VoeOJFfShBnBj6Ib.bpeG/eMKuz8QF9uiF2",  # hash para "senha"
    }
}

SECRET_KEY = "1234"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodifica o token usando a chave secreta
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # Extraí o usuário do "banco de dados"
        user = get_user(fake_users_db, username=username)
        if user is None:
            raise credentials_exception
        return user
    except (JWTError):
        raise credentials_exception

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Aqui você adicionaria suas rotas de API existentes...
@app.get("/test_db_connection")
async def test_connection(User = Depends(get_current_user)):
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
        result = cursor.fetchone()
        if result:
            return {"message": "Cliente encontrado", "ID_BEERSALES": result[0]}
        else:
            return {"message": "Cliente não encontrado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar o cliente: {e}")

#cadastra um novo cliente
@app.post("/cadastrar_cliente")
async def cadastrar_cliente(cliente: Cliente, current_user: User = Depends(get_current_user)):
    try:
        conn = get_connection() # Esta função deve ser definida para obter uma conexão com seu banco de dados
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

        return {"message": "Cliente cadastrado com sucesso", "COD_RETORNO": cod_retorno}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar cliente: {e}")

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
async def cadastrar_item_pedido(pedido: Pedido):
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

        for item in pedido.ITENS:
            cod_retorno = cursor.callproc('POST_PEDIDO_ITEM', [
                pedido.ID_PEDIDO,
                item.ID_ITEM,
                item.ID_PRODUTO,
                item.QUANTIDADE,
                item.PRECO_UNITARIO,
                item.DESCONTO,
                item.OUTRAS_DESPESAS,
                item.PRECO_TOTAL
            ])
            conn.commit()
        return {"message": "Pedido cadastrado com sucesso", "COD_RETORNO": cod_retorno}   
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar pedido: {e}")
    

    # try:
    #     conn = get_connection() # Esta função deve ser definida para obter uma conexão com seu banco de dados
    #     cursor = conn.cursor()

    #     for item in pedido.itens:
    #         cod_retorno = cursor.callproc('POST_PEDIDO_ITEM', [
    #             pedido.ID_PEDIDO,
    #             item.ID_ITEM,
    #             item.ID_PRODUTO,
    #             item.QUANTIDADE,
    #             item.PRECO_UNITARIO,
    #             item.DESCONTO,
    #             item.OUTRAS_DESPESAS,
    #             item.PRECO_TOTAL
    #         ])
    #         conn.commit()
                
    #     return {"message": "Item do pedido cadastrado com sucesso", "COD_RETORNO": cod_retorno}
                    
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Erro ao cadastrar item do pedido: {e}")
    
#Funções de Utilidade para Autenticação




#Rotas de Autenticação

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
