from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

# Modelos Pydantic 

class Cliente(BaseModel):
    ID_EXTERNO: str
    NOME: str
    APELIDO: str
    CPF_CNPJ: str
    IE: None 
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
    INATIVO: bool  


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
    itens: List[ItemPedido]

