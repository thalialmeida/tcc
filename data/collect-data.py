import requests
import json
import time
import logging
from dotenv import load_dotenv
import os


load_dotenv()

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Caminho de saída para o arquivo
output_path = "/home/thalia/TCC/data/raw/2024_09_26_arquivosfeministas.json"

# URL da API
url = "https://osint.rest/api/instagram/user_photos?query=arquivosfeministas&limit=10000&timeout=1000"

# Payload e cabeçalhos
payload = {}
headers = {
    'Authorization': f'{os.getenv("API_KEY")}'  
}
# Início da contagem do tempo
start_time = time.time()
logging.info("Iniciando a requisição para a URL: %s", url)
try:
    # Fazendo a requisição
    response = requests.get(url, headers=headers, data=payload)
    
    # Verificando o status da resposta
    response.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx

    # Processando os dados
    dados = response.json()
    
    # Logando a resposta
    logging.info("Requisição bem-sucedida. Status Code: %d", response.status_code)
    logging.info("Dados recebidos: %s", json.dumps(dados, indent=4)[:500])  # Exibir apenas os primeiros 500 caracteres

except requests.exceptions.HTTPError as http_err:
    logging.error("Erro HTTP: %s", http_err)
except requests.exceptions.ConnectionError:
    logging.error("Erro de conexão. Verifique a URL ou sua conexão de internet.")
except requests.exceptions.Timeout:
    logging.error("A requisição excedeu o tempo limite.")
except requests.exceptions.RequestException as err:
    logging.error("Ocorreu um erro: %s", err)
except json.JSONDecodeError:
    logging.error("Erro ao decodificar a resposta JSON.")
else:
    # Salvando os dados no arquivo
    with open(output_path, 'w') as f:
        json.dump(dados, f, indent=4)
    logging.info("Dados salvos em: %s", output_path)

# Fim da contagem do tempo
end_time = time.time()
logging.info("Tempo total da requisição: %.2f segundos", end_time - start_time)
