from src.preprocessors.preprocessing import PrePreprocessor

import json 
def main():
    # lista_bases = ['/home/thalia/TCC/data/raw/2024_09_22_coletivo_feminista.json', 
    #                '/home/thalia/TCC/data/raw/2024_09_22_feminiismo.json', 
    #                '/home/thalia/TCC/data/raw/2024_09_22_feminismo_semdemagogia.json', 
    #                '/home/thalia/TCC/data/raw/2024_09_22_planetaella.json',
    #                '/home/thalia/TCC/data/raw/2024_09_26_arquivosfeministas.json',
    #                '/home/thalia/TCC/data/raw/2024_09_26_revistatpm.json' ]
    # Instancia o pré-processador
    preprocessor = PrePreprocessor()
    
    # # Carrega os dados do arquivo JSON
    preprocessor.load_data(f'/home/thalia/TCC/data/raw/combined_results.json')
    
    # # Processa todos os textos e hashtags
    processed_texts = preprocessor.preprocess_all()
    
    # # # Salva o resultado no formato JSON (um array de mensagens combinadas)
    # preprocessor.save_processed_data(f'/home/thalia/TCC/data/processed/profiles_data_3.json', processed_texts)

    # preprocessor.combine_json_files(lista_bases, '/home/thalia/TCC/data/processed/profiles_data.json')

    with open('/home/thalia/TCC/data/processed/profiles_data_3.json', 'r', encoding='utf-8') as f:
            text_list = json.load(f)

    processed_list = preprocessor.remove_empty_strings(text_list)

    # print( len(text_list), len(processed_list),) #antes: 11582 depois:11070 
    preprocessor.save_processed_data(f'/home/thalia/TCC/data/processed/profiles_data_3.json', processed_list)



if __name__ == "__main__":
    main()
