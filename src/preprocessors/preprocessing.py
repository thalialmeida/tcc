import spacy
import json
import re
import os
import nltk
from nltk.stem import PorterStemmer

nltk.download('punkt')

class PrePreprocessor:
    def __init__(self, language="pt"):
        # Carrega o modelo de linguagem do SpaCy para português
        self.nlp = spacy.load(f"pt_core_news_sm")

    def load_data(self, file_path):
        """Carrega os dados de postagens de um arquivo JSON."""
        if file_path.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                self.data = json_data
        else:
            raise ValueError("Formato de arquivo não suportado. Use .json.")

    def decode_text(self, text):
        """Decodifica texto que contém códigos de escape Unicode."""
        return text.encode('utf-8').decode('utf-8')
        

    def remove_emojis(self, text):
        """Remove emojis do texto usando regex."""
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # Emoticons
                                   u"\U0001F300-\U0001F5FF"  # Símbolos e pictogramas
                                   u"\U0001F680-\U0001F6FF"  # Transporte e símbolos de mapas
                                   u"\U0001F1E0-\U0001F1FF"  # Bandeiras (sinalizadores)
                                   u"\U00002500-\U00002BEF"  # Símbolos diversos
                                   u"\U00002702-\U000027B0"  # Mais símbolos diversos
                                   u"\U000024C2-\U0001F251"  # Letras circundadas
                                   "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text)

    def preprocess_hashtags(self, hashtags):
        """Preprocessa as hashtags, removendo o símbolo #."""
        processed_hashtags = [hashtag.lstrip('#') for hashtag in hashtags]
        return ' '.join(processed_hashtags)
    
    # def split_joined_words(self, text):
    #     """
    #     Insere espaços entre palavras juntas usando a biblioteca wordninja.
    #     Exemplo: 'indesejadavocê' vira 'indesejada você'.
    #     """
    #     # Separa palavras concatenadas
    #     words = wordninja.split(text)
    #     return ' '.join(words)
    
    def preprocess_text(self, text):
        """Realiza o pré-processamento no texto."""
        
        stemmer = PorterStemmer()
        
        text = self.decode_text(text)
        text = self.remove_emojis(text)
        text = text.replace('\n', '')  # Remove quebras de linha (\n)
        text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)  # Remove URLs
        text = re.sub(r"@\w+", "", text)  # Remove menções
        text = re.sub(r"[^\w\s]", "", text)  # Remove pontuação
        text = text.lower()  # Converte para minúsculas
        
        # Processa o texto usando o SpaCy
        doc = self.nlp(text)

        # Extrai tokens relevantes (lematizados e removendo stopwords e pontuação)
        lemmas = [
            token.lemma_ for token in doc if not token.is_stop and not token.is_punct
        ]

        # Realiza o stemming nos tokens lematizados (3° melhoria do pre-proc, pois sem o steamming, alguns topicos vieram enviesados)
        stemmed_tokens = [stemmer.stem(token) for token in lemmas]
        return " ".join(stemmed_tokens)


    def combine_text_fields(self, row):
        """Combina campos de título, texto em mídia e hashtags em uma única string."""
        combined_text = ''
        
        # Adiciona o título processado (se disponível)
        if 'title' in row and row['title']:
            combined_text += row['processed_title'] + ' '
        
        # Adiciona o texto processado da mídia (se disponível)
        if 'text_on_media' in row and row['text_on_media']:
            combined_text += ' '.join(row['processed_text_on_media']) + ' '
        
        # Adiciona as hashtags processadas (se disponíveis)
        if 'hashtags' in row and row['hashtags']:
            combined_text += row['processed_hashtags'] + ' '
        
        # Remove possíveis espaços extras
        return combined_text.strip()
    
    def preprocess_all(self):
        """Aplica o pré-processamento a todas as postagens."""
        combined_messages = []

        for row in self.data:
            # Processa o campo 'title' (título da postagem)
            if 'title' in row and row['title']:
                row['processed_title'] = self.preprocess_text(row['title'])
            
            # Processa o campo 'text_on_media' (texto de mídia)
            if 'text_on_media' in row and row['text_on_media']:
                row['processed_text_on_media'] = [
                    self.preprocess_text(text['text_on_media']) for text in row['text_on_media']
                ]
            
            # Processa o campo 'hashtags' (hashtags da postagem)
            if 'hashtags' in row and row['hashtags']:
                row['processed_hashtags'] = self.preprocess_hashtags(row['hashtags'])
            
            # Combina os campos de título, texto em mídia e hashtags em uma string para BERTopic
            combined_text = self.combine_text_fields(row)
            
            # Adiciona o texto combinado ao array de mensagens
            combined_messages.append(combined_text)
        
        return combined_messages
    
    # def preprocess_text_list(self, text_list):
    #     """
    #     Aplica o pré-processamento em uma lista de strings.
    #     Retorna uma lista de strings com as palavras separadas e processadas.
    #     """
    #     processed_texts = []
    #     for text in text_list:
    #         # Aplica o pré-processamento em cada texto da lista
    #         processed_text = self.split_joined_words(text)
    #         processed_texts.append(processed_text)
    #     return processed_texts
    
    def save_processed_data(self, output_path, processed_data):
        """Salva os dados processados em um arquivo JSON, no formato adequado."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=4)
            
    def combine_json_files(self, input_paths, output_path):
        """Combina múltiplos arquivos JSON em um único arquivo JSON."""
        combined_data = []

        # Itera sobre todos os arquivos JSON fornecidos
        for file_path in input_paths:
            if os.path.exists(file_path) and file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Verifica se o arquivo contém uma lista de strings
                    if isinstance(data, list):
                        combined_data.extend(data)
                    else:
                        print(f"O arquivo {file_path} não contém uma lista de strings.")
            else:
                print(f"Arquivo {file_path} não encontrado ou não é um arquivo JSON.")

        # Salva os dados combinados no arquivo de saída
        with open(output_path, 'w', encoding='utf-8') as out_file:
            json.dump(combined_data, out_file, ensure_ascii=False, indent=4)

        print(f"Os arquivos foram combinados e salvos em {output_path}.")

    def remove_empty_strings(self, text_list):
        """
        Remove strings vazias de uma lista de strings.
        """
        return [text for text in text_list if text.strip() != ""]