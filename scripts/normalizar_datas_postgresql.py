#!/usr/bin/env python3
"""
Script para normalizar datas para formato PostgreSQL (ISO 8601)
"""

import pandas as pd
import os
from datetime import datetime, timedelta

def converter_serial_excel_para_data(serial):
    """Converte número serial do Excel para data"""
    try:
        # Excel considera 1900-01-01 como dia 1, mas tem um bug no ano 1900
        # Python considera 1900-01-01 como base
        if pd.isna(serial) or serial == '':
            return None
        
        serial_num = float(serial)
        
        # Data base do Excel (corrigindo o bug do 1900)
        excel_base = datetime(1899, 12, 30)
        data_convertida = excel_base + timedelta(days=serial_num)
        
        return data_convertida.strftime('%Y-%m-%d')
    
    except (ValueError, TypeError):
        return None

def normalizar_datas_csvs():
    """Normaliza datas nos CSVs para formato PostgreSQL"""
    
    print("📅 NORMALIZANDO DATAS PARA FORMATO POSTGRESQL")
    print("=" * 60)
    
    # Diretórios
    dir_entrada = 'data/originais/oss/finais_completos_com_todos_uuids'
    dir_saida = 'data/originais/oss/finais_datas_normalizadas'
    
    # Criar diretório de saída
    os.makedirs(dir_saida, exist_ok=True)
    
    # Colunas de data identificadas
    colunas_data = [
        '            DATA DE COMPRA         ',
        'DT NASC',
        'PREV DE ENTR'
    ]
    
    arquivos = [f for f in os.listdir(dir_entrada) if f.endswith('.csv')]
    
    total_conversoes = 0
    total_registros = 0
    
    for arquivo in sorted(arquivos):
        print(f"\n📄 Processando: {arquivo}")
        
        caminho_entrada = os.path.join(dir_entrada, arquivo)
        df = pd.read_csv(caminho_entrada)
        
        registros_arquivo = len(df)
        conversoes_arquivo = 0
        
        # Processar cada coluna de data
        for coluna in colunas_data:
            if coluna in df.columns:
                print(f"   📊 Processando coluna: '{coluna}'")
                
                valores_originais = df[coluna].notna().sum()
                
                # Normalizar valores
                def normalizar_data(valor):
                    if pd.isna(valor) or str(valor).strip() == '':
                        return None
                    
                    valor_str = str(valor).strip()
                    
                    # Se já está no formato ISO, manter
                    if '-' in valor_str and len(valor_str) == 10:
                        try:
                            # Validar se é uma data válida
                            datetime.strptime(valor_str, '%Y-%m-%d')
                            return valor_str
                        except ValueError:
                            pass
                    
                    # Se é serial do Excel, converter
                    if valor_str.isdigit() and len(valor_str) >= 4:
                        return converter_serial_excel_para_data(valor_str)
                    
                    # Outros formatos - tentar parsing automático
                    try:
                        if '/' in valor_str:
                            # Assumir DD/MM/YYYY ou MM/DD/YYYY
                            partes = valor_str.split('/')
                            if len(partes) == 3:
                                if int(partes[0]) > 12:  # Provavelmente DD/MM/YYYY
                                    data_obj = datetime.strptime(valor_str, '%d/%m/%Y')
                                else:  # Provavelmente MM/DD/YYYY
                                    data_obj = datetime.strptime(valor_str, '%m/%d/%Y')
                                return data_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        pass
                    
                    return None
                
                df[coluna] = df[coluna].apply(normalizar_data)
                
                valores_convertidos = df[coluna].notna().sum()
                conversoes_coluna = valores_convertidos
                conversoes_arquivo += conversoes_coluna
                
                print(f"      • Valores originais: {valores_originais}")
                print(f"      • Valores convertidos: {valores_convertidos}")
                print(f"      • Taxa de sucesso: {(valores_convertidos/valores_originais)*100:.1f}%" if valores_originais > 0 else "      • Nenhum valor para converter")
        
        # Salvar arquivo normalizado
        nome_saida = arquivo.replace('_final_todos_uuids.csv', '_datas_normalizadas.csv')
        caminho_saida = os.path.join(dir_saida, nome_saida)
        
        df.to_csv(caminho_saida, index=False)
        
        print(f"   ✅ Salvo: {nome_saida}")
        print(f"   📊 Conversões realizadas: {conversoes_arquivo}")
        
        total_registros += registros_arquivo
        total_conversoes += conversoes_arquivo
    
    print(f"\n🎉 NORMALIZAÇÃO COMPLETA!")
    print(f"📊 ESTATÍSTICAS FINAIS:")
    print(f"   • Arquivos processados: {len(arquivos)}")
    print(f"   • Total de registros: {total_registros:,}")
    print(f"   • Total de conversões: {total_conversoes:,}")
    print(f"   • Diretório de saída: {dir_saida}")
    
    # Listar arquivos criados
    print(f"\n📁 ARQUIVOS NORMALIZADOS CRIADOS:")
    arquivos_criados = [f for f in os.listdir(dir_saida) if f.endswith('.csv')]
    total_size = 0
    
    for arquivo in sorted(arquivos_criados):
        size_kb = os.path.getsize(os.path.join(dir_saida, arquivo)) / 1024
        total_size += size_kb
        print(f"   • {arquivo} ({size_kb:.1f} KB)")
    
    print(f"   📦 Total: {total_size:.1f} KB")
    
    # Verificar resultado em um arquivo
    if arquivos_criados:
        print(f"\n🔍 VERIFICAÇÃO DA NORMALIZAÇÃO:")
        arquivo_teste = arquivos_criados[0]
        caminho_teste = os.path.join(dir_saida, arquivo_teste)
        df_teste = pd.read_csv(caminho_teste, nrows=5)
        
        print(f"   📄 Verificando: {arquivo_teste}")
        for coluna in colunas_data:
            if coluna in df_teste.columns:
                valores_exemplo = df_teste[coluna].dropna().head(3).tolist()
                print(f"      • {coluna}: {valores_exemplo}")
    
    print(f"\n✅ DATAS NORMALIZADAS PARA POSTGRESQL!")
    print(f"🎯 Formatos agora em ISO 8601 (YYYY-MM-DD)")
    
    return dir_saida

if __name__ == "__main__":
    normalizar_datas_csvs()