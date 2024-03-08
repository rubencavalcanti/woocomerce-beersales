from fastapi import FastAPI, HTTPException
import firebirdsql

# Inicialização do aplicativo FastAPI
app = FastAPI()

# Detalhes de conexão com o banco de dados
host: str = '15.228.168.144'
port: int = 3050
database: str = '/db/beer/Coronel_Church/SYNC4_CORONEL_CHURCH.FDB'
user: str = 'CORONEL_CHURCH_V4'
password: str = 'hfPJp@Sg'


# Função para verificar a conexão com o banco de dados
def test_db_connection() -> dict:
    try:
        with firebirdsql.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                charset='UTF8'
        ) as connection:
            return {"message": "Conexão bem-sucedida ao banco de dados"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar ao banco de dados: {e}")


# Rota para verificar a conexão com o banco de dados
@app.get("/test_db_connection")
async def test_connection():
    return test_db_connection()


# Rota para verificar se o cliente existe
@app.get("/verificar_cliente")
async def verificar_cliente(cpf_cnpj: str):
    try:
        with firebirdsql.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                charset='UTF8'
        ) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT ID_BEERSALES FROM GET_CLIENTE ('01.01.2000') WHERE CPF_CNPJ = ?", (cpf_cnpj,))
            result = cursor.fetchone()
            if result:
                return {"message": "Cliente encontrado"}
            else:
                return {"message": "Cliente não encontrado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar o cliente: {e}")


# Rota para cadastrar um novo cliente
@app.post("/cadastrar_cliente")
async def cadastrar_cliente(cliente: dict):
    try:
        # Verificando se todos os campos obrigatórios estão presentes no dicionário cliente
        campos_obrigatorios = ['ID_EXTERNO', 'NOME', 'APELIDO', 'CPF_CNPJ', 'ENDERECO_RUA', 'ENDERECO_NUMERO',
                               'ENDERECO_CEP', 'ENDERECO_BAIRRO', 'ENDERECO_CIDADE', 'ENDERECO_UF',
                               'CONTATO_TELEFONE', 'CONTATO_EMAIL', 'ID_EMPRESA', 'INATIVO']
        for campo in campos_obrigatorios:
            if campo not in cliente:
                raise HTTPException(status_code=400, detail=f"Campo obrigatório ausente: {campo}")

        with firebirdsql.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            charset='UTF8'
        ) as connection:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT * FROM POST_CLIENTE_V4 (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cliente['ID_EXTERNO'],  # Varchar(15)
                cliente['NOME'],  # Varchar(100)
                cliente['APELIDO'],  # Varchar(100)
                cliente['CPF_CNPJ'],  # Varchar(14)
                cliente.get('IE'),  # Varchar(14)
                cliente['ENDERECO_RUA'],  # Varchar(80)
                cliente['ENDERECO_NUMERO'],  # Varchar(15)
                cliente.get('ENDERECO_COMPLEMENTO', ''),  # Varchar(50)
                cliente['ENDERECO_CEP'],  # Varchar(8)
                cliente['ENDERECO_BAIRRO'],  # Varchar(50)
                cliente['ENDERECO_CIDADE'],  # Varchar(50)
                cliente['ENDERECO_UF'],  # Varchar(2)
                cliente['CONTATO_TELEFONE'],  # Varchar(500)
                cliente.get('CONTATO_CELULAR'),  # Varchar(500)
                cliente['CONTATO_EMAIL'],  # Varchar(500)
                cliente.get('CONTATO_OUTROS'),  # Varchar(500)
                cliente['ID_EMPRESA'],  # Integer
                cliente.get('ID_VENDEDOR', None),  # Integer
                cliente.get('ID_TABELA_PRECO', None),  # Integer
                cliente.get('LIMITE_CREDITO', None),  # Numeric(15,2)
                cliente.get('ID_GRUPO_CLIENTE', None),  # Integer
                cliente.get('ID_FORMA_PAGAMENTO', None),  # Integer
                cliente.get('ID_PRAZO', None),  # Integer
                cliente.get('DIA_ATENDIMENTO', None),  # SmallInt
                cliente.get('PERIODICIDADE', None),  # SmallInt
                cliente.get('OBSERVACAO', ''),  # Varchar(500)
                cliente['INATIVO']  # Varchar(5)
            ))

            connection.commit()

        return {"message": "Cliente cadastrado com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar o cliente: {e}")


# Rota para receber os dados do pedido da loja virtual
@app.post("/pedido_loja_virtual")
async def receber_dados_pedido(data: dict):
    try:
        with firebirdsql.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                charset='UTF8'
        ) as connection:
            cursor = connection.cursor()

            # Verificar se o cliente já está cadastrado
            cursor.execute("SELECT ID_BEERSALES FROM GET_CLIENTE ('01.01.2000') WHERE CPF_CNPJ = ?", (data['cliente']['CPF_CNPJ'],))
            result = cursor.fetchone()

            # Se o cliente não estiver cadastrado, enviar os dados do cliente
            if not result:
                cursor.callproc('POST_CLIENTE_V4', [
                    data['cliente']['ID_EXTERNO'],
                    data['cliente']['NOME'],
                    data['cliente']['APELIDO'],
                    data['cliente']['CPF_CNPJ'],
                    '',
                    data['cliente']['ENDERECO_RUA'],
                    data['cliente']['ENDERECO_NUMERO'],
                    data.get('ENDERECO_COMPLEMENTO', ''),
                    data['cliente']['ENDERECO_CEP'],
                    data['cliente']['ENDERECO_BAIRRO'],
                    data['cliente']['ENDERECO_CIDADE'],
                    data['cliente']['ENDERECO_UF'],
                    data['cliente']['CONTATO_TELEFONE'],
                    data.get('CONTATO_CELULAR', ''),
                    data['cliente']['CONTATO_EMAIL'],
                    data.get('CONTATO_OUTROS', ''),
                    data['cliente']['ID_EMPRESA'],
                    data.get('ID_VENDEDOR', None),
                    data.get('ID_TABELA_PRECO', None),
                    data.get('LIMITE_CREDITO', None),
                    data.get('ID_GRUPO_CLIENTE', None),  # Removido o valor padrão 2
                    data.get('ID_FORMA_PAGAMENTO', None),
                    data.get('ID_PRAZO', None),
                    data.get('DIA_ATENDIMENTO', None),
                    data.get('PERIODICIDADE', None),
                    data.get('OBSERVACAO', ''),
                    'N'
                ])
                connection.commit()

            # Inserir os dados do pedido
            cursor.execute("""
                INSERT INTO PEDIDO (NUMERO, CLIENTE_ID, VALOR_TOTAL)
                VALUES (?, ?, ?)
            """, (
                data['pedido']['NUMERO'],
                result[0] if result else cursor.lastrowid,
                data['pedido']['VALOR_TOTAL']
            ))

            # Obter o ID do pedido recém-inserido
            pedido_id = cursor.lastrowid

            # Enviar os dados dos itens do pedido
            for item in data['itens']:
                cursor.execute("""
                    INSERT INTO ITEM_PEDIDO (NUMERO_PEDIDO, PRODUTO, QUANTIDADE, VALOR_UNITARIO)
                    VALUES (?, ?, ?, ?)
                """, (
                    f"{data['pedido']['NUMERO']}/{item['PRODUTO']}",
                    item['PRODUTO'],
                    item['QUANTIDADE'],
                    item['VALOR_UNITARIO']
                ))

            # Confirmar a transação
            connection.commit()

        return {"message": "Pedido recebido e processado com sucesso"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar os dados do pedido: {e}")
