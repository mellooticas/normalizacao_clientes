#!/usr/bin/env python3
"""
Script para cruzamento correto entre Lista DAV e Sistema
Aplicando normalização correta dos números de OS
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def normalizar_numero_os_correto(numero_str):
    """
    Normaliza números de OS corretamente:
    - Remove prefixos 4200 e 4800
    - Mantém apenas o número real da OS
    """
    if pd.isna(numero_str):
        return None
    
    numero_str = str(numero_str).strip()
    
    # Remove .0 se existir
    if numero_str.endswith('.0'):
        numero_str = numero_str[:-2]
    
    # Remove prefixos conhecidos
    if numero_str.startswith('4200'):
        return numero_str[4:]  # Remove os 4 primeiros dígitos (4200)
    elif numero_str.startswith('4800'):
        return numero_str[4:]  # Remove os 4 primeiros dígitos (4800)
    
    # Se não tem prefixo, retorna como está
    return numero_str

def cruzamento_dav_vendas_correto():
    """Cruzamento correto entre DAV e vendas usando OS reais"""
    
    print("🔄 === CRUZAMENTO CORRETO DAV vs VENDAS === 🔄")
    
    # 1. Carregar dados DAV normalizados
    print("\n📊 === CARREGANDO DADOS === 📊")
    dav = pd.read_csv('data/originais/controles_gerais/lista_dav_normalizada_20251104_224904.csv')
    print(f"✅ DAV carregado: {len(dav):,} registros")
    
    # 2. Aplicar normalização CORRETA nos números de OS
    print("\n🔧 === APLICANDO NORMALIZAÇÃO CORRETA === 🔧")
    dav['nro_os_real'] = dav['nro_os_original'].apply(normalizar_numero_os_correto)
    
    # Mostrar exemplos da normalização
    print("📋 Exemplos de normalização:")
    exemplos = dav[['nro_os_original', 'nro_os_normalizado', 'nro_os_real']].head(10)
    for _, row in exemplos.iterrows():
        print(f"   Original: {row['nro_os_original']} → Anterior: {row['nro_os_normalizado']} → CORRETO: {row['nro_os_real']}")
    
    # 3. Carregar dados de vendas - vamos verificar todos os arquivos que podem ter OS
    print("\n📂 === BUSCANDO DADOS COM NÚMEROS DE OS === 📂")
    
    # Verificar se existe algum arquivo com números de OS
    arquivos_para_testar = [
        'data_backup/vendas_os_completo.csv',
        'data/originais/extraidos_corrigidos/entregas_os_consolidado_20251104_173451.csv',
        'data/vendas_para_importar/entregas_os_final_datas_corrigidas.csv'
    ]
    
    dados_com_os = []
    
    for arquivo in arquivos_para_testar:
        try:
            df = pd.read_csv(arquivo)
            print(f"📄 Testando {arquivo}:")
            print(f"   Colunas: {df.columns.tolist()}")
            
            # Procurar colunas que podem ter OS
            os_cols = [col for col in df.columns if any(termo in col.lower() for termo in ['os', 'ordem', 'numero'])]
            if os_cols:
                print(f"   ✅ Colunas de OS encontradas: {os_cols}")
                dados_com_os.append((arquivo, df, os_cols))
            else:
                print(f"   ❌ Nenhuma coluna de OS encontrada")
        except Exception as e:
            print(f"   ❌ Erro ao carregar {arquivo}: {str(e)}")
    
    # 4. Se encontrou dados com OS, fazer cruzamento
    if dados_com_os:
        print(f"\n🎯 === ENCONTRADOS {len(dados_com_os)} ARQUIVOS COM OS === 🎯")
        
        for arquivo, df, os_cols in dados_com_os:
            print(f"\n📊 Analisando {arquivo}:")
            
            for col in os_cols:
                if col in df.columns:
                    # Normalizar OS deste arquivo também
                    df[f'{col}_normalizado'] = df[col].apply(normalizar_numero_os_correto)
                    
                    print(f"   Coluna: {col}")
                    print(f"   Registros: {len(df):,}")
                    print(f"   OS únicas: {df[f'{col}_normalizado'].nunique():,}")
                    
                    # Fazer cruzamento
                    os_dav = set(dav['nro_os_real'].dropna().astype(str))
                    os_arquivo = set(df[f'{col}_normalizado'].dropna().astype(str))
                    
                    os_comuns = os_dav & os_arquivo
                    
                    print(f"   OS em comum: {len(os_comuns):,}")
                    
                    if len(os_comuns) > 0:
                        print(f"   ✅ CRUZAMENTO ENCONTRADO!")
                        print(f"   📋 Primeiros exemplos: {list(os_comuns)[:10]}")
                        
                        # Salvar resultado do cruzamento
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        arquivo_resultado = f"data/originais/controles_gerais/cruzamento_correto_dav_{timestamp}.csv"
                        
                        # Criar DataFrame do cruzamento
                        cruzamentos = []
                        
                        for os_comum in list(os_comuns)[:500]:  # Primeiros 500 para análise
                            dav_match = dav[dav['nro_os_real'] == os_comum].iloc[0]
                            arquivo_match = df[df[f'{col}_normalizado'] == os_comum].iloc[0]
                            
                            cruzamento = {
                                'os_numero': os_comum,
                                'dav_arquivo': dav_match['arquivo_origem'],
                                'dav_cliente': dav_match['cliente_nome'],
                                'dav_data': dav_match['data_os'],
                                'dav_valor': dav_match['valor_liquido'],
                                'dav_loja': dav_match['loja_nome'],
                                'dav_status': dav_match['status'],
                                'arquivo_origem': arquivo
                            }
                            
                            # Adicionar colunas do arquivo de origem
                            for col_origem in df.columns:
                                if col_origem not in ['id', 'created_at', 'updated_at']:
                                    cruzamento[f'arquivo_{col_origem}'] = arquivo_match[col_origem]
                            
                            cruzamentos.append(cruzamento)
                        
                        if cruzamentos:
                            df_cruzamento = pd.DataFrame(cruzamentos)
                            df_cruzamento.to_csv(arquivo_resultado, index=False)
                            print(f"   💾 Cruzamento salvo: {arquivo_resultado}")
                            print(f"   📁 Registros salvos: {len(df_cruzamento):,}")
                    else:
                        print(f"   ❌ Nenhuma OS em comum")
    
    else:
        print("\n❌ Nenhum arquivo com números de OS encontrado")
        print("🔍 Vamos verificar se os números das vendas são na verdade OS:")
        
        # Testar se numero_venda é na verdade numero_os
        vendas = pd.read_csv('data/vendas_para_importar/vendas_TODAS_RENUMERADAS_SEM_DUPLICATAS.csv')
        print(f"\n📊 Testando se numero_venda são OS...")
        print(f"   Primeiras 10 numero_venda: {vendas['numero_venda'].head(10).tolist()}")
        
        # Normalizar números de venda como se fossem OS
        vendas['numero_venda_normalizado'] = vendas['numero_venda'].apply(normalizar_numero_os_correto)
        
        # Fazer cruzamento
        os_dav = set(dav['nro_os_real'].dropna().astype(str))
        os_vendas = set(vendas['numero_venda_normalizado'].dropna().astype(str))
        
        os_comuns = os_dav & os_vendas
        print(f"   OS em comum: {len(os_comuns):,}")
        
        if len(os_comuns) > 0:
            print(f"   ✅ NÚMERO DE VENDA SÃO OS!")
            
            # Salvar resultado
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            arquivo_resultado = f"data/originais/controles_gerais/cruzamento_dav_vendas_{timestamp}.csv"
            
            cruzamentos = []
            for os_comum in list(os_comuns)[:1000]:
                dav_match = dav[dav['nro_os_real'] == os_comum].iloc[0]
                venda_match = vendas[vendas['numero_venda_normalizado'] == os_comum].iloc[0]
                
                cruzamentos.append({
                    'os_numero': os_comum,
                    'dav_cliente': dav_match['cliente_nome'],
                    'dav_data': dav_match['data_os'],
                    'dav_valor': dav_match['valor_liquido'],
                    'dav_loja': dav_match['loja_nome'],
                    'dav_status': dav_match['status'],
                    'venda_numero': venda_match['numero_venda'],
                    'venda_cliente_id': venda_match['cliente_id'],
                    'venda_data': venda_match['data_venda'],
                    'venda_valor': venda_match['valor_total'],
                    'venda_loja_id': venda_match['loja_id']
                })
            
            df_cruzamento = pd.DataFrame(cruzamentos)
            df_cruzamento.to_csv(arquivo_resultado, index=False)
            print(f"   💾 Cruzamento DAV-Vendas salvo: {arquivo_resultado}")
            print(f"   📁 Registros: {len(df_cruzamento):,}")
        else:
            print(f"   ❌ Números de venda também não são OS")
    
    # 5. Estatísticas finais
    print(f"\n📊 === ESTATÍSTICAS FINAIS === 📊")
    print(f"✅ DAV processado: {len(dav):,} registros")
    print(f"🎯 OS únicas DAV: {dav['nro_os_real'].nunique():,}")
    print(f"📅 Período DAV: {dav['data_os'].min()} → {dav['data_os'].max()}")
    
    # Salvar DAV com normalização correta
    arquivo_dav_corrigido = f"data/originais/controles_gerais/lista_dav_normalizacao_correta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    dav.to_csv(arquivo_dav_corrigido, index=False)
    print(f"💾 DAV com normalização correta salvo: {arquivo_dav_corrigido}")
    
    print(f"\n💾 Script executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    cruzamento_dav_vendas_correto()