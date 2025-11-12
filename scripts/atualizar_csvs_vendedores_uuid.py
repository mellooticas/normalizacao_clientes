#!/usr/bin/env python3
"""
Script para atualizar CSVs normalizados com UUIDs corretos dos vendedores
Faz cruzamento entre vendedores normalizados e as lojas
"""

import pandas as pd
import re
from pathlib import Path
import json

def extrair_vendedores_do_sql():
    """Extrai os UUIDs dos vendedores do arquivo SQL gerado"""
    
    sql_path = Path("database/10_populacao_vendedores_normalizado.sql")
    
    if not sql_path.exists():
        print("❌ Arquivo SQL não encontrado!")
        return {}, {}
    
    print("🔍 EXTRAINDO VENDEDORES DO SQL...")
    
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Extrair vendedores únicos
    vendedor_pattern = r"\('([^']+)',\s*'([^']+)',\s*'[^']+',\s*'[^']+',\s*true,\s*NOW\(\),\s*NOW\(\)\)"
    vendedor_matches = re.findall(vendedor_pattern, sql_content)
    
    vendedores_uuid = {}
    for uuid_v, nome in vendedor_matches:
        vendedores_uuid[nome] = uuid_v
    
    print(f"✅ Extraídos {len(vendedores_uuid)} vendedores únicos")
    
    # Extrair relacionamentos vendedor-loja
    relacionamento_pattern = r"\('([^']+)',\s*'([^']+)',\s*'([^']+)',\s*true,\s*'[^']+'\)"
    relacionamento_matches = re.findall(relacionamento_pattern, sql_content)
    
    # Mapear UUID vendedor -> loja_id -> codigo_sistema
    vendedor_loja_codigo = {}
    for uuid_v, loja_id, codigo in relacionamento_matches:
        if uuid_v not in vendedor_loja_codigo:
            vendedor_loja_codigo[uuid_v] = {}
        vendedor_loja_codigo[uuid_v][loja_id] = codigo
    
    print(f"✅ Extraídos {len(relacionamento_matches)} relacionamentos vendedor-loja")
    
    return vendedores_uuid, vendedor_loja_codigo

def carregar_mapeamento_excel():
    """Carrega mapeamento de normalização do Excel"""
    
    excel_path = Path("PADRONIZACAO_VENDEDORES_COMPLETA.xlsx")
    
    if not excel_path.exists():
        print("❌ Arquivo Excel não encontrado!")
        return {}
    
    df = pd.read_excel(excel_path)
    
    # Criar mapeamento: nome_original -> nome_normalizado
    mapeamento = {}
    for _, row in df.iterrows():
        if pd.notna(row['nome_original']) and pd.notna(row['nome_padronizado']):
            nome_orig = str(row['nome_original']).strip()
            nome_norm = str(row['nome_padronizado']).strip()
            mapeamento[nome_orig] = nome_norm
    
    print(f"✅ Carregado mapeamento de {len(mapeamento)} nomes originais -> normalizados")
    
    return mapeamento

def atualizar_csvs_com_uuids():
    """Atualiza todos os CSVs normalizados com UUIDs corretos"""
    
    print("🔧 ATUALIZANDO CSVs COM UUIDs DOS VENDEDORES")
    print("=" * 60)
    
    # Extrair dados do SQL
    vendedores_uuid, vendedor_loja_codigo = extrair_vendedores_do_sql()
    
    # Carregar mapeamento do Excel
    mapeamento_nomes = carregar_mapeamento_excel()
    
    # Mapeamento de lojas
    loja_nomes_para_id = {
        'MAUA': '9a22ccf1-36fe-4b9f-9391-ca31433dc31e',
        'PERUS': 'da3978c9-bba2-431a-91b7-970a406d3acf',
        'RIO_PEQUENO': '4e94f51f-3b0f-4e0f-ba73-64982b870f2c',
        'SUZANO': '52f92716-d2ba-441a-ac3c-94bdfabd9722',
        'SUZANO2': 'aa7a5646-f7d6-4239-831c-6602fbabb10a',
        'SAO_MATEUS': '1c35e0ad-3066-441e-85cc-44c0eb9b3ab4'
    }
    
    # Reverter mapeamento UUID -> nome normalizado
    uuid_para_nome = {uuid_v: nome for nome, uuid_v in vendedores_uuid.items()}
    
    # Diretório dos CSVs
    csv_dir = Path("data/originais/oss/normalizadas")
    
    if not csv_dir.exists():
        print(f"❌ Diretório não encontrado: {csv_dir}")
        return
    
    # Processar cada CSV
    arquivos_processados = 0
    total_registros = 0
    vendedores_encontrados = 0
    vendedores_nao_encontrados = 0
    
    for csv_file in csv_dir.glob("*_normalizado.csv"):
        print(f"\n📋 Processando: {csv_file.name}")
        
        # Extrair nome da loja do arquivo
        loja_nome = csv_file.stem.replace("_normalizado", "")
        loja_id = loja_nomes_para_id.get(loja_nome)
        
        if not loja_id:
            print(f"   ⚠️  Loja não mapeada: {loja_nome}")
            continue
        
        # Ler CSV
        try:
            df = pd.read_csv(csv_file)
            print(f"   📊 {len(df)} registros no CSV")
            
            # Verificar se já tem colunas UUID
            if 'vendedor_uuid' not in df.columns:
                df['vendedor_uuid'] = None
            if 'vendedor_nome_normalizado' not in df.columns:
                df['vendedor_nome_normalizado'] = None
            
            # Processar cada registro
            for idx, row in df.iterrows():
                consultor_original = str(row.get('             CONSULTOR  ', '')).strip()
                
                if not consultor_original or consultor_original == 'nan':
                    continue
                
                total_registros += 1
                
                # Normalizar nome do consultor
                nome_normalizado = mapeamento_nomes.get(consultor_original, consultor_original)
                
                # Buscar UUID do vendedor normalizado
                vendedor_uuid = vendedores_uuid.get(nome_normalizado)
                
                if vendedor_uuid:
                    df.loc[idx, 'vendedor_uuid'] = vendedor_uuid
                    df.loc[idx, 'vendedor_nome_normalizado'] = nome_normalizado
                    vendedores_encontrados += 1
                else:
                    print(f"   ⚠️  Vendedor não encontrado: '{consultor_original}' -> '{nome_normalizado}'")
                    vendedores_nao_encontrados += 1
            
            # Salvar CSV atualizado
            output_file = csv_dir / f"{loja_nome}_normalizado_uuid.csv"
            df.to_csv(output_file, index=False)
            
            # Estatísticas do arquivo
            com_uuid = df['vendedor_uuid'].notna().sum()
            sem_uuid = df['vendedor_uuid'].isna().sum()
            
            print(f"   ✅ Salvos {com_uuid} registros com UUID")
            if sem_uuid > 0:
                print(f"   ⚠️  {sem_uuid} registros sem UUID")
            
            arquivos_processados += 1
            
        except Exception as e:
            print(f"   ❌ Erro ao processar {csv_file.name}: {e}")
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL:")
    print(f"   • Arquivos processados: {arquivos_processados}")
    print(f"   • Total de registros: {total_registros}")
    print(f"   • Vendedores encontrados: {vendedores_encontrados}")
    print(f"   • Vendedores não encontrados: {vendedores_nao_encontrados}")
    
    if vendedores_nao_encontrados > 0:
        taxa_sucesso = (vendedores_encontrados / total_registros) * 100
        print(f"   • Taxa de sucesso: {taxa_sucesso:.1f}%")
    
    # Salvar mapeamentos para referência
    mapeamentos_completos = {
        'vendedores_uuid': vendedores_uuid,
        'vendedor_loja_codigo': vendedor_loja_codigo,
        'mapeamento_nomes': mapeamento_nomes,
        'loja_nomes_para_id': loja_nomes_para_id,
        'estatisticas': {
            'arquivos_processados': arquivos_processados,
            'total_registros': total_registros,
            'vendedores_encontrados': vendedores_encontrados,
            'vendedores_nao_encontrados': vendedores_nao_encontrados
        }
    }
    
    with open("mapeamento_vendedores_csvs_completo.json", 'w', encoding='utf-8') as f:
        json.dump(mapeamentos_completos, f, indent=2, ensure_ascii=False)
    
    print(f"   📋 Mapeamentos salvos em: mapeamento_vendedores_csvs_completo.json")
    
    if vendedores_nao_encontrados == 0:
        print("\n🎉 TODOS OS VENDEDORES FORAM MAPEADOS COM SUCESSO!")
    else:
        print(f"\n⚠️  {vendedores_nao_encontrados} vendedores precisam ser verificados")
    
    print("✅ CSVs atualizados com UUIDs dos vendedores!")

if __name__ == "__main__":
    atualizar_csvs_com_uuids()