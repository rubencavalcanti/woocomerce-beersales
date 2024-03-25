from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
from typing import Union

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
    ID_GRUPO_CLIENTE: int = 2
    ID_FORMA_PAGAMENTO: Optional[int] = None
    ID_PRAZO: Optional[int] = None
    DIA_ATENDIMENTO: Optional[int] = None
    PERIODICIDADE: Optional[str] = None
    OBSERVACAO: Optional[str] = None
    INATIVO: bool = False

class ItemPedido(BaseModel):
    ID_ITEM: int
    ID_PRODUTO: int
    QUANTIDADE: int
    PRECO_UNITARIO: float
    DESCONTO: float
    OUTRAS_DESPESAS: float
    PRECO_TOTAL: float

class Pedido(BaseModel):
    ID_PEDIDO: int
    ID_CLIENTE: int
    ID_VENDEDOR: int = 1
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
    URGENTE: bool = False
    REQUER_APROVACAO: bool = False
    ID_EMPRESA: int
    ID_MOEDA: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str