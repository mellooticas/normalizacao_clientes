#!/usr/bin/env python3
"""
Script melhorado para normalizar datas para PostgreSQL
"""

import pandas as pd
import os
from datetime import datetime, timedelta
import re

def converter_serial_excel_para_data(serial):
    """Converte número serial do Excel para data"""
    try:
        if pd.isna(serial) or serial == '':
            return None
        
        serial_num = float(serial)
        
        # Data base do Excel (corrigindo o bug do 1900)
        excel_base = datetime(1899, 12, 30)
        data_convertida = excel_base + timedelta(days=serial_num)
        
        return data_convertida.strftime('%Y-%m-%d')
    
    except (ValueError, TypeError):
        return None

def normalizar_datas_melhorado():
    """Normaliza datas com tratamento melhorado para PostgreSQL"""
    
    print("📅 NORMALIZAÇÃO MELHORADA DE DATAS PARA POSTGRESQL")
    print("=" * 60)
    
    # Diretórios
    dir_entrada = 'data/originais/oss/finais_completos_com_todos_uuids'
    dir_saida = 'data/originais/oss/finais_postgresql_prontos'
    
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
                
                # Normalizar valores com tratamento melhorado
                def normalizar_data_melhorado(valor):
                    if pd.isna(valor) or str(valor).strip() == '':
                        return None
                    
                    valor_str = str(valor).strip()
                    
                    # Remover timestamp se presente (YYYY-MM-DD HH:MM:SS → YYYY-MM-DD)
                    if ' ' in valor_str:
                        valor_str = valor_str.split(' ')[0]
                    
                    # Se já está no formato ISO, validar e manter
                    if re.match(r'^\d{4}-\d{2}-\d{2}$', valor_str):
                        try:
                            # Validar se é uma data válida
                            datetime.strptime(valor_str, '%Y-%m-%d')
                            return valor_str
                        except ValueError:
                            pass
                    
                    # Se é serial do Excel, converter
                    if valor_str.replace('.', '').isdigit() and len(valor_str) >= 4:
                        return converter_serial_excel_para_data(valor_str)
                    
                    # Formato DD/MM/YYYY
                    if '/' in valor_str:
                        try:
                            partes = valor_str.split('/')
                            if len(partes) == 3:
                                # Tentar DD/MM/YYYY primeiro
                                try:
                                    if int(partes[0]) <= 31 and int(partes[1]) <= 12:
                                        data_obj = datetime.strptime(valor_str, '%d/%m/%Y')
                                        return data_obj.strftime('%Y-%m-%d')
                                except ValueError:
                                    pass
                                
                                # Tentar MM/DD/YYYY
                                try:
                                    if int(partes[0]) <= 12 and int(partes[1]) <= 31:
                                        data_obj = datetime.strptime(valor_str, '%m/%d/%Y')
                                        return data_obj.strftime('%Y-%m-%d')
                                except ValueError:
                                    pass
                        except (ValueError, IndexError):
                            pass
                    
                    # Outros formatos com hífen mas não ISO
                    if '-' in valor_str and not re.match(r'^\d{4}-\d{2}-\d{2}$', valor_str):
                        try:
                            # Tentar parsing automático
                            data_obj = pd.to_datetime(valor_str, errors='coerce')
                            if pd.notna(data_obj):
                                return data_obj.strftime('%Y-%m-%d')
                        except:
                            pass
                    
                    return None
                
                df[coluna] = df[coluna].apply(normalizar_data_melhorado)
                
                valores_convertidos = df[coluna].notna().sum()
                conversoes_coluna = valores_convertidos
                conversoes_arquivo += conversoes_coluna
                
                print(f"      • Valores originais: {valores_originais}")
                print(f"      • Valores convertidos: {valores_convertidos}")
                if valores_originais > 0:
                    taxa = (valores_convertidos/valores_originais)*100
                    print(f"      • Taxa de sucesso: {taxa:.1f}%")
                    if taxa < 95:
                        print(f"      ⚠️  Taxa baixa - verificar dados")
                else:
                    print(f"      • Nenhum valor para converter")
        
        # Limpar nomes de colunas (remover espaços extras)
        df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]
        
        # Renomear colunas de data para nomes mais limpos
        df = df.rename(columns={
            'DATA DE COMPRA': 'data_compra',
            'DT NASC': 'data_nascimento', 
            'PREV DE ENTR': 'previsao_entrega'
        })
        
        # Salvar arquivo normalizado
        nome_saida = arquivo.replace('_final_todos_uuids.csv', '_postgresql_pronto.csv')
        caminho_saida = os.path.join(dir_saida, nome_saida)
        
        df.to_csv(caminho_saida, index=False)
        
        print(f"   ✅ Salvo: {nome_saida}")
        print(f"   📊 Conversões realizadas: {conversoes_arquivo}")
        
        total_registros += registros_arquivo
        total_conversoes += conversoes_arquivo
    
    print(f"\n🎉 NORMALIZAÇÃO MELHORADA COMPLETA!")
    print(f"📊 ESTATÍSTICAS FINAIS:")
    print(f"   • Arquivos processados: {len(arquivos)}")
    print(f"   • Total de registros: {total_registros:,}")
    print(f"   • Total de conversões: {total_conversoes:,}")
    print(f"   • Diretório de saída: {dir_saida}")
    
    # Listar arquivos criados
    print(f"\n📁 ARQUIVOS PRONTOS PARA POSTGRESQL:")
    arquivos_criados = [f for f in os.listdir(dir_saida) if f.endswith('.csv')]
    total_size = 0
    
    for arquivo in sorted(arquivos_criados):
        size_kb = os.path.getsize(os.path.join(dir_saida, arquivo)) / 1024
        total_size += size_kb
        print(f"   • {arquivo} ({size_kb:.1f} KB)")
    
    print(f"   📦 Total: {total_size:.1f} KB")
    
    # Verificar resultado final
    if arquivos_criados:
        print(f"\n🔍 VERIFICAÇÃO FINAL:")
        arquivo_teste = arquivos_criados[0]
        caminho_teste = os.path.join(dir_saida, arquivo_teste)
        df_teste = pd.read_csv(caminho_teste, nrows=3)
        
        print(f"   📄 Verificando: {arquivo_teste}")
        colunas_data_limpas = ['data_compra', 'data_nascimento', 'previsao_entrega']
        
        for coluna in colunas_data_limpas:
            if coluna in df_teste.columns:
                valores_exemplo = df_teste[coluna].dropna().head(2).tolist()
                print(f"      • {coluna}: {valores_exemplo}")
    
    print(f"\n✅ ARQUIVOS PRONTOS PARA IMPORTAÇÃO NO POSTGRESQL!")
    print(f"🎯 Benefícios:")
    print(f"   • Datas em formato ISO 8601 (YYYY-MM-DD)")
    print(f"   • Timestamps removidos")
    print(f"   • Nomes de colunas limpos")
    print(f"   • Compatibilidade total com PostgreSQL")
    
    return dir_saida

if __name__ == "__main__":
    normalizar_datas_melhorado()