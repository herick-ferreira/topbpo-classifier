import pandas as pd
from unidecode import unidecode
import os, re

def process_csv(file_path):
    try:
        # Load the CSV file
        df = pd.read_csv(file_path, sep=';', encoding='latin-1')

        # Function to classify type of launch
        def classificar_lancamento(row):
            endereco = str(row['ENDEREÇO DO IMÓVEL']).strip() if pd.notna(row['ENDEREÇO DO IMÓVEL']) else ""
            locatario = str(row['LOCATÁRIO']).strip() if pd.notna(row['LOCATÁRIO']) else ""
            imovel = str(row['IMÓVEL']).strip() if pd.notna(row['IMÓVEL']) else ""
            historico = str(row['HISTORICO']).strip() if pd.notna(row['HISTORICO']) else ""
            descricao = unidecode(str(row['DESCRIÇÃO'])).strip().lower() if pd.notna(row['DESCRIÇÃO']) else ""

            # Classification logic
            if (imovel == "41939" and locatario == "27005491000110" and
                ("divida ativa" in descricao or historico in ['541', '141'])):
                return 'Lançamentos Contábeis'

            if  historico in ['541', '141']:
                if verificar_reembolso(df, locatario, imovel, ['541', '141']):
                    return 'Lançamentos Contábeis'
                else:
                    return 'Lançamentos manuais'
            
            elif historico in ['510', '110']:
                if verificar_reembolso(df, locatario, imovel, ['510', '110']):
                    return 'Lançamentos Contábeis'
                else:
                    return 'Lançamentos manuais'
            
            elif historico in ['505', '105']:
                if verificar_reembolso(df, locatario, imovel, ['505', '105']):
                    return 'Lançamentos Contábeis'
                else:
                    return 'Lançamentos manuais'
                



            if endereco == "" and locatario == "" and imovel == "0":
                return 'Lançamentos manuais'

            if imovel == "99996":
                return 'Lançamentos manuais'

            if pd.notna(row['VALOR RECEBIDO']) and str(row['VALOR RECEBIDO']).strip() != "":
                if (descricao in ['aluguel', 'desc. aluguel', 'dif. aluguel', 'multa contratual'] or 
                    historico in ['101', '701', '131', '201', '137']):
                    return 'Recibos de Venda'

            if pd.notna(row['VALOR PAGO']) and str(row['VALOR PAGO']).strip() != "":
                if (descricao in ['tx. expediente', 'comissao', 'passagem', 'anuncio', 'diversos'] or
                    historico in ['512', '516', '554', '530', '517']):
                    return 'Despesas'

                if locatario == "":
                    if (descricao in ['condominio', 'consumo luz', 'cota extra', 'imp.predial(iptu)', 
                                     'taxa incendio', 'seguro c/fogo'] or
                        historico in ['502', '503', '506', '505', '528', '504']):
                        return 'Despesas'
                    return 'Despesas'

            if ((pd.notna(row['VALOR PAGO']) and str(row['VALOR PAGO']).strip() != "") or 
                (pd.notna(row['VALOR RECEBIDO']) and str(row['VALOR RECEBIDO']).strip() != "")):
                if (pd.notna(row['IMÓVEL']) and str(row['IMÓVEL']).strip() not in ["0", "00000", "99996"] and 
                    pd.notna(row['LOCATÁRIO']) and str(row['LOCATÁRIO']).strip() != ""):
                    if (descricao in ['imp.predial(iptu)', 'taxa incendio', 'condominio', 
                                      'seguro c/fogo', 'agua e esgoto', 'seguro fianca', 'cota extra', 'aforamento'] or
                        historico in ['503', '528', '103', '128', '502', '134', '104', '584', '505', '149', '591', '524', '202', '141', '191']):
                        return 'Lançamentos Contábeis'

            return 'Lançamentos manuais'

        # Apply classification
        df['TIPO DE LANÇAMENTO'] = df.apply(classificar_lancamento, axis=1)

        # Create output filename
        base_filename = os.path.basename(file_path)
        name_without_ext = os.path.splitext(base_filename)[0]
        output_filename = f"{name_without_ext}_classificado.xlsx"
        output_file = os.path.join('processed', output_filename)
        
        # Ensure processed directory exists
        os.makedirs('processed', exist_ok=True)
        
        # Aplicar limpeza em todas as colunas de texto
        for col in df.columns:
            if df[col].dtype == 'object':  # Colunas de texto
                df[col] = df[col].apply(limpar_para_excel)
        
        # Save the classified data to Excel
        df.to_excel(output_file, index=False)

        return output_file
        
    except Exception as e:
        raise Exception(f"Error processing CSV file: {str(e)}")

# Função auxiliar para verificar reembolso
def verificar_reembolso(df, locatario, imovel, values=[]):
    """
    Verifica se existe cruzamento entre HISTORICO para mesmo LOCATÁRIO e IMÓVEL
    """
    if not locatario or not imovel or imovel in ["0", "00000", "99996"]:
        return False
    
    # Filtrar registros do mesmo locatário e imóvel
    registros_mesmo_local = df[
        (df['LOCATÁRIO'].astype(str).str.strip() == locatario) & 
        (df['IMÓVEL'].astype(str).str.strip() == imovel)
    ]
    
    # Verificar se existem ambos os históricos da lista de valores
    historicos = registros_mesmo_local['HISTORICO'].astype(str).str.strip().unique()
    
    response = all(value in historicos for value in values) if values else False
    return response

# Função para limpar caracteres especiais para Excel
def limpar_para_excel(texto):
    """
    Remove caracteres que podem causar problemas no Excel
    """
    if pd.isna(texto):
        return ""
    
    texto = str(texto)
    # Remove caracteres de controle (0x00-0x1F exceto tab, newline, carriage return)
    texto = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', texto)
    # Remove caracteres problemáticos específicos
    texto = texto.replace('\x00', '').replace('\x01', '').replace('\x02', '')
    
    return texto