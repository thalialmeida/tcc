import os
import json
import requests
from transformers import AutoTokenizer
from llama_index.core import Settings, Document
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from dotenv import load_dotenv

load_dotenv()

class Llama3:
    def __init__(self, logger: object = None, max_tokens: int = 4096):
        """
        Inicializa a classe Llama3.

        Args:
            logger (object): Logger para registrar logs (opcional).
            max_tokens (int): Número máximo de tokens que o modelo pode processar.
        """
        self.__logger = logger
        self.max_tokens = max_tokens

        base_url = os.getenv("LLAMA_BASE_URL") or "http://127.0.0.1:11434"
        request_timeout = float(os.getenv("LLAMA_REQUEST_TIMEOUT", 10))  
        Settings.embed_model = OllamaEmbedding(
            base_url=base_url,
            model_name= os.getenv("EMBEDDED_MODEL") or "all-minilm",
        )
        Settings.tokenizer = AutoTokenizer.from_pretrained(
            (os.getenv('TOKENIZER_MODEL') or 'neuralmind/bert-large-portuguese-cased'), 
            do_lower_case=False,
        )

        self.__llm = Settings.llm = Ollama(
            base_url=base_url, 
            model=(os.getenv("LLM_MODEL") or "llama3"), 
            request_timeout=request_timeout
        )
        self.tokenizer = AutoTokenizer.from_pretrained('neuralmind/bert-large-portuguese-cased')

    def truncate_prompt(self, prompt: str) -> str:
        """
        Corta o prompt para se ajustar ao limite de tokens do modelo.

        Args:
            prompt (str): O prompt original.

        Returns:
            str: O prompt truncado.
        """
        tokens = self.tokenizer.encode(prompt, truncation=False)

        if len(tokens) > self.max_tokens:
            if self.__logger:
                self.__logger.warning(f"Prompt excede {self.max_tokens} tokens. Truncando.")
            # Truncar o número de tokens até o máximo permitido
            tokens = tokens[:self.max_tokens]
            prompt_truncado = self.tokenizer.decode(tokens, skip_special_tokens=True)
            return prompt_truncado

        return prompt

    def send_prompt(self, prompt: str) -> str:
        """
        Envia um prompt para a LLM e retorna a resposta.

        Args:
            prompt (str): O prompt a ser enviado para a LLM.

        Returns:
            str: A resposta da LLM.
        """
        # Truncar o prompt se exceder o limite de tokens
        prompt = self.truncate_prompt(prompt)

        if self.__logger:
            self.__logger.info(f"Enviando prompt para a LLM: {prompt}")

        try:
            # Fazendo a requisição para a LLM
            response = requests.post(
                f"{self.__llm.base_url}/api/generate",
                json={"model": self.__llm.model, "prompt": prompt}
            )

            # Log da resposta bruta para inspecionar
            if self.__logger:
                self.__logger.info(f"Resposta bruta do servidor: {response.text}")
            
            # Verificando a resposta
            if response.status_code == 200:
                return self.format_response(response.text)
            else:
                if self.__logger:
                    self.__logger.error(f"Erro na resposta da LLM: {response.status_code} - {response.text}")
                return f"Erro: {response.status_code} - {response.text}"

        except requests.exceptions.RequestException as e:
            if self.__logger:
                self.__logger.error(f"Erro ao enviar prompt: {e}")
            return f"Erro na comunicação com o servidor: {str(e)}"

    def format_response(self, raw_response: str) -> str:
        """
        Formata a resposta recebida da LLM, concatenando todos os campos "response".

        Args:
            raw_response (str): Resposta bruta do servidor (vários JSONs).

        Returns:
            str: A resposta formatada.
        """
        formatted_response = ""
        try:
            # Quebrando a resposta bruta em linhas e processando cada linha
            for line in raw_response.splitlines():
                # Parse cada linha de JSON e extrai o campo "response"
                data = json.loads(line)
                formatted_response += data.get("response", "")
        except json.JSONDecodeError as e:
            if self.__logger:
                self.__logger.error(f"Erro ao decodificar JSON: {e}")
            return f"Erro: Resposta não está no formato JSON esperado. Conteúdo: {raw_response}"

        return formatted_response

    def response_to_json(self, resposta_llm, arquivo_saida):
        """
        Extrai e converte a parte JSON dentro de uma string em um dicionário Python, e salva o resultado em um arquivo JSON.

        Args:
            resposta_llm (str): A string que contém o JSON.
            arquivo_saida (str): O caminho/nome do arquivo para salvar o JSON extraído.
        """
        inicio_json = resposta_llm.find("{")
        
        if inicio_json == -1:
            raise ValueError("Nenhum JSON encontrado na string fornecida.")
        
        json_str = resposta_llm[inicio_json:]
        
        try:
            dados_json = json.loads(json_str)
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                json.dump(dados_json, f, ensure_ascii=False, indent=4)
        except json.JSONDecodeError:
            raise ValueError("Erro ao decodificar o JSON. Verifique o formato.")

