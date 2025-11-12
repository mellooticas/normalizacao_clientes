#!/usr/bin/env python3
"""
Cruzamento por loja: OSS ↔ Clientes ↔ UUID
"""

import pandas as pd
from pathlib import Path

def processar_loja(nome_loja):
    """Processa uma loja específica"""
    print(f"\n🏪 PROCESSANDO LOJA: {nome_loja.upper()}")
    print("=" * 50)
    
    # 1. Carregar OSS da loja
    oss_path = Path(f"data/originais/oss/finais_postgresql_prontos/oss_{nome_loja}_clientes_ids.csv")
    if not oss_path.exists():
        print(f"❌ Arquivo OSS não encontrado: {oss_path}")
        return None
    
    oss_df = pd.read_csv(oss_path)
    print(f"📥 OSS {nome_loja}: {len(oss_df):,} registros")
    
    if 'numero_os' not in oss_df.columns:
        print(f"❌ Coluna 'numero_os' não encontrada no OSS")
        return None
    
    oss_validos = oss_df['numero_os'].notna().sum()
    print(f"   ✅ numero_os válidos: {oss_validos:,}")
    
    # 2. Carregar clientes originais da loja  
    clientes_path = Path(f"data/originais/clientes/clientes_{nome_loja}.csv")
    if not clientes_path.exists():
        print(f"❌ Arquivo clientes não encontrado: {clientes_path}")
        return None
    
    clientes_df = pd.read_csv(clientes_path)
    print(f"📥 Clientes {nome_loja}: {len(clientes_df):,} registros")
    
    if 'numero_os' not in clientes_df.columns:
        print(f"❌ Coluna 'numero_os' não encontrada nos clientes")
        return None
    
    clientes_validos = clientes_df['numero_os'].notna().sum()
    print(f"   ✅ numero_os válidos: {clientes_validos:,}")
    
    # 3. Carregar clientes UUID da loja
    uuid_path = Path(f"data/clientes_uuid/clientes_{nome_loja}.csv")
    if not uuid_path.exists():
        print(f"❌ Arquivo UUID não encontrado: {uuid_path}")
        return None
    
    uuid_df = pd.read_csv(uuid_path)
    print(f"📥 UUID {nome_loja}: {len(uuid_df):,} registros")
    
    # 4. PASSO 1: OSS ↔ Clientes via numero_os
    print(f"\n🔗 PASSO 1: OSS ↔ CLIENTES ({nome_loja})")
    
    # Preparar dados
    oss_prep = oss_df[['numero_os', 'cliente_id', 'vendedor_uuid']].copy()
    oss_prep = oss_prep.dropna(subset=['numero_os'])
    oss_prep['numero_os'] = pd.to_numeric(oss_prep['numero_os'], errors='coerce')
    oss_prep = oss_prep.dropna(subset=['numero_os'])
    
    # Determinar coluna ID nos clientes
    coluna_id = 'cliente_id' if 'cliente_id' in clientes_df.columns else 'ID'
    
    clientes_prep = clientes_df[[coluna_id, 'numero_os']].copy()
    clientes_prep = clientes_prep.dropna(subset=['numero_os'])
    clientes_prep['numero_os'] = pd.to_numeric(clientes_prep['numero_os'], errors='coerce')
    clientes_prep = clientes_prep.dropna(subset=['numero_os'])
    
    # Merge PASSO 1
    resultado_p1 = pd.merge(
        oss_prep,
        clientes_prep,
        on='numero_os',
        how='inner',
        suffixes=('_oss', '_cliente')
    )
    
    print(f"   ✅ Matches Passo 1: {len(resultado_p1):,}")
    
    if len(resultado_p1) == 0:
        print(f"   ❌ Nenhum match encontrado para {nome_loja}")
        return None
    
    # 5. PASSO 2: Clientes ↔ UUID via ID
    print(f"\n🔗 PASSO 2: CLIENTES ↔ UUID ({nome_loja})")
    
    # Determinar coluna de ligação no UUID
    coluna_ligacao = None
    colunas_possiveis = ['id_legado', 'ID', 'cliente_id_x', 'cliente_id']
    
    for col in colunas_possiveis:
        if col in uuid_df.columns:
            coluna_ligacao = col
            break
    
    if not coluna_ligacao:
        print(f"   ❌ Nenhuma coluna de ligação encontrada no UUID")
        return None
    
    print(f"   Usando '{coluna_ligacao}' como ligação")
    
    # Preparar dados PASSO 2
    step1_prep = resultado_p1[[f'{coluna_id}', 'numero_os', 'cliente_id_oss', 'vendedor_uuid']].copy()
    step1_prep = step1_prep.rename(columns={f'{coluna_id}': 'cliente_id_original'})
    
    uuid_prep = uuid_df[['cliente_id_y', coluna_ligacao, 'Cliente']].copy()
    uuid_prep = uuid_prep.dropna(subset=[coluna_ligacao])
    
    # Converter tipos
    step1_prep['cliente_id_original'] = pd.to_numeric(step1_prep['cliente_id_original'], errors='coerce')
    uuid_prep[coluna_ligacao] = pd.to_numeric(uuid_prep[coluna_ligacao], errors='coerce')
    
    # Merge PASSO 2
    resultado_final = pd.merge(
        step1_prep,
        uuid_prep,
        left_on='cliente_id_original',
        right_on=coluna_ligacao,
        how='inner'
    )
    
    print(f"   ✅ Matches Passo 2: {len(resultado_final):,}")
    
    if len(resultado_final) > 0:
        print(f"\n📋 Amostra {nome_loja}:")
        print(resultado_final[['numero_os', 'Cliente', 'cliente_id_y']].head(3).to_string())
        
        # Adicionar loja
        resultado_final['loja'] = nome_loja
        return resultado_final
    else:
        return None

def main():
    print("🚀 CRUZAMENTO POR LOJA: OSS ↔ CLIENTES ↔ UUID")
    print("=" * 60)
    
    lojas = ['perus', 'rio_pequeno', 'sao_mateus', 'suzano2', 'maua', 'suzano']
    
    resultados_todas_lojas = []
    
    for loja in lojas:
        resultado_loja = processar_loja(loja)
        if resultado_loja is not None:
            resultados_todas_lojas.append(resultado_loja)
    
    # Consolidar resultados
    if resultados_todas_lojas:
        resultado_consolidado = pd.concat(resultados_todas_lojas, ignore_index=True)
        
        print(f"\n📊 RESULTADO CONSOLIDADO")
        print("=" * 30)
        print(f"✅ Total de matches: {len(resultado_consolidado):,}")
        
        # Estatísticas por loja
        stats_loja = resultado_consolidado['loja'].value_counts()
        print(f"\n📋 Matches por loja:")
        for loja, count in stats_loja.items():
            print(f"   {loja}: {count:,}")
        
        # Estatísticas gerais
        os_unicos = resultado_consolidado['numero_os'].nunique()
        clientes_unicos = resultado_consolidado['cliente_id_y'].nunique()
        
        print(f"\n📊 OSS únicos com cliente UUID: {os_unicos:,}")
        print(f"📊 Clientes UUID únicos: {clientes_unicos:,}")
        
        # Salvar resultado
        output_path = Path("data/vendas_para_importar/mapeamento_oss_clientes_uuid_por_loja.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        resultado_consolidado.to_csv(output_path, index=False)
        
        print(f"\n💾 RESULTADO SALVO: {output_path}")
        print("\n🎯 Agora podemos usar este mapeamento para atualizar as vendas!")
        
    else:
        print("\n❌ Nenhum resultado encontrado")

if __name__ == "__main__":
    main()