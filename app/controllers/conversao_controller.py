import requests as http_requests
from app.config.settings import EXCHANGE_API_URL


def convert(valor, de, para):
    """Converte valor entre moedas usando API externa de câmbio.

    Retorna tupla `(sucesso, payload, status_http)` para uso direto na camada de rota.
    """

    try:
        # Timeout curto evita bloquear a aplicação quando o provedor externo degrada.
        resp = http_requests.get(f"{EXCHANGE_API_URL}/{de}", timeout=5)
        dados = resp.json()

        if dados.get("result") != "success":
            return False, {"erro": "Erro ao consultar taxa de câmbio"}, 502

        taxa = dados["rates"].get(para)
        if taxa is None:
            return False, {"erro": f"Moeda {para} não encontrada"}, 400

        convertido = round(valor * taxa, 2)
        return (
            True,
            {
                "valor_original": valor,
                "moeda_origem": de,
                "moeda_destino": para,
                "taxa": taxa,
                "valor_convertido": convertido,
            },
            200,
        )
    except http_requests.RequestException:
        return False, {"erro": "Falha na conexão com API de câmbio"}, 502
