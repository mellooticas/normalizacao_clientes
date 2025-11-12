#!/usr/bin/env python3
"""
Cruzamento em 2 passos: OSS → Clientes Originais → Clientes UUID
"""

import pandas as pd
from pathlib import Path

def carregar_oss_clientes_ids():
    """PASSO 1: Carrega OSS com IDs de clientes normalizados"""
    print("📊 PASSO 1: CARREGANDO OSS COM CLIENTE IDS")
    print("=" * 50)
    
    oss_path = Path("data/originais/oss/finais_postgresql_prontos")
    
    oss_completos = []
    
    # Carregar apenas arquivos oss_*_clientes_ids.csv
    for arquivo in oss_path.glob("oss_*_clientes_ids.csv"):
        print(f"📥 {arquivo.name}")
        df = pd.read_csv(arquivo)
        print(f"   Registros: {len(df):,}")
        print(f"   Colunas importantes: OS N°, cliente_id, vendedor_uuid")
        oss_completos.append(df)
    
    if oss_completos:
        oss_final = pd.concat(oss_completos, ignore_index=True)
        print(f"\n✅ Total OSS: {len(oss_final):,}")
        
        # Verificar dados
        os_validos = oss_final['OS N°'].notna().sum()
        clientes_validos = oss_final['cliente_id'].notna().sum()
        vendedores_validos = oss_final['vendedor_uuid'].notna().sum()
        
        print(f"📊 OS N° válidos: {os_validos:,}")
        print(f"📊 Cliente IDs válidos: {clientes_validos:,}")
        print(f"📊 Vendedor UUIDs válidos: {vendedores_validos:,}")
        
        return oss_final
    else:
        print("❌ Nenhum arquivo OSS encontrado")
        return None

def carregar_clientes_originais():
    """Carrega clientes originais para fazer ponte"""
    print("\n📊 CARREGANDO CLIENTES ORIGINAIS (PONTE)")
    print("=" * 45)
    
    clientes_path = Path("data/originais/clientes")
    
    clientes_originais = []
    
    for arquivo in clientes_path.glob("*.csv"):
        print(f"📥 {arquivo.name}")
        df = pd.read_csv(arquivo)
        print(f"   Registros: {len(df):,}")
        clientes_originais.append(df)
    
    if clientes_originais:
        clientes_final = pd.concat(clientes_originais, ignore_index=True)
        print(f"\n✅ Total clientes originais: {len(clientes_final):,}")
        return clientes_final
    else:
        return None

def carregar_clientes_uuid():
    """Carrega clientes com UUID final"""
    print("\n📊 CARREGANDO CLIENTES UUID FINAL")
    print("=" * 40)
    
    clientes_uuid_path = Path("data/clientes_uuid")
    
    clientes_uuid = []
    
    for arquivo in clientes_uuid_path.glob("*.csv"):
        print(f"📥 {arquivo.name}")
        df = pd.read_csv(arquivo)
        print(f"   Registros: {len(df):,}")
        clientes_uuid.append(df)
    
    if clientes_uuid:
        clientes_final = pd.concat(clientes_uuid, ignore_index=True)
        print(f"\n✅ Total clientes UUID: {len(clientes_final):,}")
        return clientes_final
    else:
        return None

def executar_cruzamento_passo1(oss_df, clientes_originais_df):
    """PASSO 1: OSS → Clientes Originais via numero_os"""
    print("\n🔄 EXECUTANDO PASSO 1: OSS → CLIENTES ORIGINAIS")
    print("=" * 55)
    
    # Verificar se existe coluna numero_os nos clientes originais
    print("Colunas clientes originais:", list(clientes_originais_df.columns))
    
    if 'numero_os' not in clientes_originais_df.columns:
        print("❌ Coluna 'numero_os' não encontrada em clientes originais")
        print("Tentando encontrar coluna similar...")
        
        # Procurar colunas similares
        colunas_os = [col for col in clientes_originais_df.columns if 'os' in col.lower() or 'n°' in col.lower()]
        print(f"Colunas similares encontradas: {colunas_os}")
        
        if not colunas_os:
            print("❌ Nenhuma coluna de OS encontrada")
            return None
    
    # Se numero_os não existe, usar ID como ponte (pode ser que já seja o numero_os)
    coluna_ponte = 'numero_os' if 'numero_os' in clientes_originais_df.columns else 'ID'
    
    print(f"Usando coluna '{coluna_ponte}' como ponte")
    
    # Preparar dados para merge
    oss_prep = oss_df[['OS N°', 'cliente_id', 'vendedor_uuid', 'loja_nome']].copy()
    oss_prep = oss_prep.dropna(subset=['OS N°'])
    
    # Limpar e converter OS N° - remover valores inválidos
    oss_prep = oss_prep[oss_prep['OS N°'] != ',']
    oss_prep = oss_prep[oss_prep['OS N°'] != '']
    oss_prep['OS N°'] = pd.to_numeric(oss_prep['OS N°'], errors='coerce')
    oss_prep = oss_prep.dropna(subset=['OS N°'])
    
    clientes_prep = clientes_originais_df[['ID', coluna_ponte] if coluna_ponte != 'ID' else ['ID']].copy()
    clientes_prep = clientes_prep.dropna(subset=['ID'])
    
    print(f"OSS preparados: {len(oss_prep):,}")
    print(f"Clientes preparados: {len(clientes_prep):,}")
    
    # Se numero_os não existe, assumir que ID é o numero_os
    if coluna_ponte == 'ID':
        # Tentar match direto ID ↔ OS N°
        clientes_prep['numero_os_calculado'] = clientes_prep['ID']
        resultado = oss_prep.merge(
            clientes_prep[['ID', 'numero_os_calculado']], 
            left_on='OS N°', 
            right_on='numero_os_calculado', 
            how='inner'
        )
    else:
        # Usar numero_os existente
        resultado = oss_prep.merge(
            clientes_prep, 
            left_on='OS N°', 
            right_on=coluna_ponte, 
            how='inner'
        )
    
    print(f"✅ Matches PASSO 1: {len(resultado):,}")
    
    if len(resultado) > 0:
        print("📊 Exemplo do resultado:")
        print(resultado[['OS N°', 'cliente_id', 'ID', 'vendedor_uuid']].head())
    
    return resultado

def executar_cruzamento_passo2(resultado_passo1, clientes_uuid_df):
    """PASSO 2: Clientes Originais → Clientes UUID via ID"""
    print("\n🔄 EXECUTANDO PASSO 2: CLIENTES ORIGINAIS → UUID")
    print("=" * 50)
    
    if resultado_passo1 is None:
        print("❌ Resultado do Passo 1 é None")
        return None
    
    # Verificar colunas de ligação no clientes_uuid
    colunas_uuid = list(clientes_uuid_df.columns)
    print(f"Colunas clientes UUID: {colunas_uuid}")
    
    # Procurar coluna de ligação (id_legado, ID, etc.)
    coluna_ligacao = None
    if 'id_legado' in colunas_uuid:
        coluna_ligacao = 'id_legado'
    elif 'ID' in colunas_uuid:
        coluna_ligacao = 'ID'
    else:
        print("❌ Nenhuma coluna de ligação encontrada")
        return None
    
    print(f"Usando coluna '{coluna_ligacao}' para ligação")
    
    # Preparar merge
    resultado_prep = resultado_passo1[['OS N°', 'cliente_id', 'ID', 'vendedor_uuid', 'loja_nome']].copy()
    
    uuid_prep = clientes_uuid_df[[coluna_ligacao, 'cliente_id_y']].copy()
    uuid_prep = uuid_prep.dropna(subset=[coluna_ligacao, 'cliente_id_y'])
    
    print(f"Resultado Passo 1: {len(resultado_prep):,}")
    print(f"Clientes UUID preparados: {len(uuid_prep):,}")
    
    # Merge final
    resultado_final = resultado_prep.merge(
        uuid_prep,
        left_on='ID',
        right_on=coluna_ligacao,
        how='inner'
    )
    
    print(f"✅ Matches PASSO 2 (FINAL): {len(resultado_final):,}")
    
    if len(resultado_final) > 0:
        print("📊 Exemplo do resultado final:")
        print(resultado_final[['OS N°', 'cliente_id_y', 'vendedor_uuid', 'loja_nome']].head())
        
        # Estatísticas
        os_unicos = resultado_final['OS N°'].nunique()
        clientes_unicos = resultado_final['cliente_id_y'].nunique()
        vendedores_unicos = resultado_final['vendedor_uuid'].nunique()
        
        print(f"\n📊 ESTATÍSTICAS FINAIS:")
        print(f"   OS únicos: {os_unicos:,}")
        print(f"   Clientes únicos: {clientes_unicos:,}")
        print(f"   Vendedores únicos: {vendedores_unicos:,}")
    
    return resultado_final

def main():
    print("🚀 CRUZAMENTO EM 2 PASSOS: OSS → CLIENTES → UUID")
    print("=" * 60)
    
    # Carregar dados
    oss_df = carregar_oss_clientes_ids()
    if oss_df is None:
        return
    
    clientes_originais_df = carregar_clientes_originais()
    if clientes_originais_df is None:
        return
    
    clientes_uuid_df = carregar_clientes_uuid()
    if clientes_uuid_df is None:
        return
    
    # Executar cruzamentos
    resultado_passo1 = executar_cruzamento_passo1(oss_df, clientes_originais_df)
    
    resultado_final = executar_cruzamento_passo2(resultado_passo1, clientes_uuid_df)
    
    if resultado_final is not None and len(resultado_final) > 0:
        # Salvar resultado
        output_path = Path("data/vendas_para_importar/mapeamento_oss_clientes_uuid.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        resultado_final.to_csv(output_path, index=False)
        
        print(f"\n💾 RESULTADO SALVO: {output_path}")
        print(f"📊 {len(resultado_final):,} relacionamentos OSS → Cliente UUID")
        print("\n🎯 Agora podemos usar este mapeamento para enriquecer as vendas!")
    else:
        print("\n❌ Nenhum resultado final obtido")

if __name__ == "__main__":
    main()