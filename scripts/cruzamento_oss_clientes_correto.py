#!/usr/bin/env python3
"""
Cruzamento correto: OSS ↔ Clientes via numero_os
"""

import pandas as pd
from pathlib import Path

def carregar_arquivos_oss():
    """Carrega arquivos OSS com numero_os"""
    print("📊 CARREGANDO ARQUIVOS OSS")
    print("=" * 30)
    
    oss_path = Path("data/originais/oss/finais_postgresql_prontos")
    oss_dados = []
    
    for arquivo in oss_path.glob("oss_*.csv"):
        print(f"📥 {arquivo.name}")
        df = pd.read_csv(arquivo)
        
        if 'numero_os' in df.columns:
            print(f"   ✅ Registros: {len(df):,}")
            print(f"   ✅ numero_os válidos: {df['numero_os'].notna().sum():,}")
            oss_dados.append(df)
        else:
            print(f"   ❌ Coluna 'numero_os' não encontrada")
    
    if oss_dados:
        oss_final = pd.concat(oss_dados, ignore_index=True)
        print(f"\n✅ Total OSS: {len(oss_final):,}")
        return oss_final
    else:
        return None

def carregar_clientes_originais():
    """Carrega clientes originais"""
    print("\n📊 CARREGANDO CLIENTES ORIGINAIS")
    print("=" * 35)
    
    clientes_path = Path("data/originais/clientes")
    clientes_dados = []
    
    for arquivo in clientes_path.glob("*.csv"):
        print(f"📥 {arquivo.name}")
        df = pd.read_csv(arquivo)
        
        if 'numero_os' in df.columns:
            print(f"   ✅ Registros: {len(df):,}")
            print(f"   ✅ numero_os válidos: {df['numero_os'].notna().sum():,}")
            clientes_dados.append(df)
        else:
            print(f"   ❌ Coluna 'numero_os' não encontrada")
            print(f"   📋 Colunas disponíveis: {list(df.columns)}")
    
    if clientes_dados:
        clientes_final = pd.concat(clientes_dados, ignore_index=True)
        print(f"\n✅ Total clientes originais: {len(clientes_final):,}")
        return clientes_final
    else:
        return None

def carregar_clientes_uuid():
    """Carrega clientes com UUID"""
    print("\n📊 CARREGANDO CLIENTES UUID")
    print("=" * 30)
    
    clientes_path = Path("data/clientes_uuid")
    clientes_dados = []
    
    for arquivo in clientes_path.glob("*.csv"):
        print(f"📥 {arquivo.name}")
        df = pd.read_csv(arquivo)
        print(f"   Registros: {len(df):,}")
        clientes_dados.append(df)
    
    if clientes_dados:
        clientes_final = pd.concat(clientes_dados, ignore_index=True)
        print(f"\n✅ Total clientes UUID: {len(clientes_final):,}")
        return clientes_final
    else:
        return None

def executar_passo1(oss_df, clientes_originais_df):
    """PASSO 1: OSS ↔ Clientes Originais via numero_os"""
    print("\n🔗 PASSO 1: OSS ↔ CLIENTES ORIGINAIS")
    print("=" * 40)
    
    # Verificar colunas disponíveis
    print("Colunas OSS:", ['numero_os', 'cliente_id', 'vendedor_uuid', 'loja_nome'])
    print("Colunas clientes:", list(clientes_originais_df.columns))
    
    # Determinar coluna ID nos clientes
    coluna_id = None
    if 'ID' in clientes_originais_df.columns:
        coluna_id = 'ID'
    elif 'cliente_id' in clientes_originais_df.columns:
        coluna_id = 'cliente_id'
    else:
        print("❌ Nenhuma coluna ID encontrada nos clientes")
        return None
    
    print(f"Usando '{coluna_id}' como identificador dos clientes")
    
    # Preparar dados
    oss_prep = oss_df[['numero_os', 'cliente_id', 'vendedor_uuid', 'loja_nome']].copy()
    oss_prep = oss_prep.dropna(subset=['numero_os'])
    
    clientes_prep = clientes_originais_df[[coluna_id, 'numero_os']].copy()
    clientes_prep = clientes_prep.dropna(subset=['numero_os'])
    
    print(f"OSS com numero_os: {len(oss_prep):,}")
    print(f"Clientes com numero_os: {len(clientes_prep):,}")
    
    # Converter para mesmo tipo
    oss_prep['numero_os'] = pd.to_numeric(oss_prep['numero_os'], errors='coerce')
    clientes_prep['numero_os'] = pd.to_numeric(clientes_prep['numero_os'], errors='coerce')
    
    # Remover NaN após conversão
    oss_prep = oss_prep.dropna(subset=['numero_os'])
    clientes_prep = clientes_prep.dropna(subset=['numero_os'])
    
    print(f"OSS após limpeza: {len(oss_prep):,}")
    print(f"Clientes após limpeza: {len(clientes_prep):,}")
    
    # Fazer o merge
    resultado = pd.merge(
        oss_prep,
        clientes_prep,
        on='numero_os',
        how='inner',
        suffixes=('_oss', '_cliente')
    )
    
    print(f"✅ Matches PASSO 1: {len(resultado):,}")
    
    # Mostrar amostra
    if len(resultado) > 0:
        print("\n📋 Amostra de matches:")
        print(resultado[['numero_os', 'cliente_id', coluna_id]].head().to_string())
    
    # Padronizar nome da coluna ID
    resultado = resultado.rename(columns={coluna_id: 'cliente_id_original'})
    
    return resultado

def executar_passo2(resultado_passo1, clientes_uuid_df):
    """PASSO 2: Clientes Originais ↔ Clientes UUID via ID"""
    print("\n🔗 PASSO 2: CLIENTES ORIGINAIS ↔ CLIENTES UUID")
    print("=" * 50)
    
    if len(resultado_passo1) == 0:
        print("❌ Nenhum resultado do Passo 1 para processar")
        return None
    
    # Verificar coluna de ligação nos clientes UUID
    print("Colunas clientes UUID:", list(clientes_uuid_df.columns))
    
    # Possíveis colunas de ligação
    colunas_id = ['id_legado', 'ID', 'cliente_id_x', 'ID_original']
    coluna_ligacao = None
    
    for col in colunas_id:
        if col in clientes_uuid_df.columns:
            coluna_ligacao = col
            print(f"✅ Usando coluna '{col}' para ligação")
            break
    
    if not coluna_ligacao:
        print("❌ Nenhuma coluna de ligação encontrada")
        return None
    
    # Preparar dados
    step1_prep = resultado_passo1[['cliente_id_original', 'numero_os', 'cliente_id', 'vendedor_uuid']].copy()
    uuid_prep = clientes_uuid_df[['cliente_id_y', coluna_ligacao, 'Cliente']].copy()
    uuid_prep = uuid_prep.dropna(subset=[coluna_ligacao])
    
    print(f"Resultado Passo 1: {len(step1_prep):,}")
    print(f"Clientes UUID: {len(uuid_prep):,}")
    
    # Converter tipos
    step1_prep['cliente_id_original'] = pd.to_numeric(step1_prep['cliente_id_original'], errors='coerce')
    uuid_prep[coluna_ligacao] = pd.to_numeric(uuid_prep[coluna_ligacao], errors='coerce')
    
    # Fazer merge
    resultado_final = pd.merge(
        step1_prep,
        uuid_prep,
        left_on='cliente_id_original',
        right_on=coluna_ligacao,
        how='inner'
    )
    
    print(f"✅ Matches PASSO 2: {len(resultado_final):,}")
    
    # Mostrar amostra
    if len(resultado_final) > 0:
        print("\n📋 Amostra final:")
        print(resultado_final[['numero_os', 'Cliente', 'cliente_id_y']].head().to_string())
    
    return resultado_final

def main():
    print("🚀 CRUZAMENTO OSS ↔ CLIENTES ↔ UUID")
    print("=" * 50)
    
    # 1. Carregar dados
    oss_df = carregar_arquivos_oss()
    if oss_df is None:
        return
    
    clientes_originais_df = carregar_clientes_originais()
    if clientes_originais_df is None:
        return
    
    clientes_uuid_df = carregar_clientes_uuid()
    if clientes_uuid_df is None:
        return
    
    # 2. Executar Passo 1
    resultado_passo1 = executar_passo1(oss_df, clientes_originais_df)
    
    # 3. Executar Passo 2
    resultado_final = executar_passo2(resultado_passo1, clientes_uuid_df)
    
    # 4. Salvar resultado
    if resultado_final is not None and len(resultado_final) > 0:
        output_path = Path("data/vendas_para_importar/mapeamento_oss_clientes_uuid.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        resultado_final.to_csv(output_path, index=False)
        
        print(f"\n💾 RESULTADO SALVO: {output_path}")
        print(f"📊 Total de OSS com cliente UUID: {len(resultado_final):,}")
        
        # Estatísticas
        oss_unicos = resultado_final['numero_os'].nunique()
        clientes_unicos = resultado_final['cliente_id_y'].nunique()
        
        print(f"📊 OSS únicos: {oss_unicos:,}")
        print(f"📊 Clientes UUID únicos: {clientes_unicos:,}")
        
        print("\n🎯 Agora podemos atualizar as vendas com estes UUIDs!")
    else:
        print("\n❌ Nenhum resultado para salvar")

if __name__ == "__main__":
    main()