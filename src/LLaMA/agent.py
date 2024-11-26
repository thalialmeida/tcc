from llama import Llama3
from prompts import PROMPT_IDENTIFICACAO_TOPICO
import json

def topic_extract(llm, dados, max_tentativas=3):
    """
    Processa os tópicos individualmente e coleta as respostas da LLM, com tentativas adicionais em caso de erro.

    Args:
        llm: Instância da classe Llama3 para enviar os prompts.
        dados (list): Lista de tópicos (palavras-chave e textos) a serem processados.
        max_tentativas (int): Número máximo de tentativas para cada tópico em caso de erro.

    Returns:
        dict: JSON com todas as respostas coletadas para os tópicos.
    """
    resultados = {}

    # Processando cada tópico individualmente
    for i, item in enumerate(dados):
        tentativas = 0
        sucesso = False

        while tentativas < max_tentativas and not sucesso:
            # Preparando o prompt para o tópico atual
            prompt = PROMPT_IDENTIFICACAO_TOPICO + json.dumps(item)

            # Enviando o prompt para a LLM
            resposta = llm.send_prompt(prompt)

            # Processando a resposta e tentando converter para dicionário
            try:
                resposta_json = json.loads(resposta)
                for indice, topico in resposta_json.items():
                    # Ajustando o índice para o índice real na lista de dados original
                    resultados[i] = topico
                sucesso = True  # Se o JSON é válido, marcamos como sucesso
            except json.JSONDecodeError:
                tentativas += 1
                print(f"Erro ao decodificar a resposta da LLM para o tópico {i}, tentativa {tentativas} de {max_tentativas}")
                
            if not sucesso and tentativas >= max_tentativas:
                print(f"Falha ao processar o tópico {i} após {max_tentativas} tentativas.")
                resultados[i] = "Erro: Tópico não identificado"

    return resultados

if __name__ == "__main__":
    # Instanciando a classe Llama3
    llm = Llama3()
    
    # Carregando o arquivo de entrada em UTF-8
    with open('topic_analysis.json', 'r', encoding='utf-8') as file_json:
        data = json.load(file_json)

    # Processando os dados individualmente
    resultado_final = topic_extract(llm, data)

    # Salvando o JSON final com todos os tópicos identificados
    with open('output/response.json', 'w', encoding='utf-8') as f:
        json.dump(resultado_final, f, ensure_ascii=False, indent=4)

    # Exibindo o resultado final em UTF-8 para o console
    print("Resultado final:", json.dumps(resultado_final, ensure_ascii=False, indent=4))
