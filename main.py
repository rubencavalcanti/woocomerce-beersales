from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class WooCommerceOrder(BaseModel):
    id: int
    customer_id: int
    total: float
    status: str

@app.post("/webhook/woocommerce")
async def receive_woocommerce_webhook(order: WooCommerceOrder):
    try:
        # Lógica para lidar com os dados recebidos do WooCommerce
        print("Recebido pedido do WooCommerce:")
        print("ID do Pedido:", order.id)
        print("ID do Cliente:", order.customer_id)
        print("Total do Pedido:", order.total)
        print("Status do Pedido:", order.status)

        # Aqui você pode integrar os dados do pedido com o Firebird ou fazer qualquer outra operação necessária
        # Exemplo:
        # inserir_pedido_no_firebird(order)

        return {"message": "Pedido recebido com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar webhook do WooCommerce: {e}")
