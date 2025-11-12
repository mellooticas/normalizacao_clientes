#!/usr/bin/env python3
"""
Unir dados OSS + LOJA para criar vendas completas
"""

import pandas as pd
from pathlib import Path

def listar_arquivos_finais():
    """Lista arquivos em finais_postgresql_prontos"""
    print("📂 ARQUIVOS EM finais_postgresql_prontos")
    print("=" * 50)
    
    path = Path("data/originais/oss/finais_postgresql_prontos")
    
    arquivos_oss = []
    arquivos_loja = []
    
    for arquivo in path.glob("*.csv"):
        if arquivo.name.startswith("oss_"):
            arquivos_oss.append(arquivo.name)
        elif not arquivo.name.startswith("oss_"):
            arquivos_loja.append(arquivo.name)
    
    print(f"📋 Arquivos OSS (cliente_id):")
    for arq in sorted(arquivos_oss):
        print(f"   - {arq}")
    
    print(f"\n📋 Arquivos LOJA (UUIDs):")
    for arq in sorted(arquivos_loja):
        print(f"   - {arq}")
    
    return arquivos_oss, arquivos_loja

def processar_loja(nome_loja):
    """Processa uma loja específica unindo OSS + LOJA"""
    print(f"\n🔄 PROCESSANDO LOJA: {nome_loja.upper()}")
    print("=" * 40)
    
    path = Path("data/originais/oss/finais_postgresql_prontos")
    
    # Encontrar arquivos da loja
    arquivo_oss = None
    arquivo_loja = None
    
    for arquivo in path.glob("*.csv"):
        if arquivo.name == f"oss_{nome_loja}_clientes_ids.csv":
            arquivo_oss = arquivo
        elif arquivo.name == f"{nome_loja.upper()}_postgresql_pronto.csv":
            arquivo_loja = arquivo
    
    if not arquivo_oss or not arquivo_loja:
        print(f"❌ Arquivos não encontrados para {nome_loja}")
        print(f"   OSS: {arquivo_oss}")
        print(f"   LOJA: {arquivo_loja}")
        return None
    
    # Carregar dados
    print(f"📥 Carregando OSS: {arquivo_oss.name}")
    oss_df = pd.read_csv(arquivo_oss)
    print(f"   Registros: {len(oss_df):,}")
    print(f"   Colunas: {list(oss_df.columns)}")
    
    print(f"📥 Carregando LOJA: {arquivo_loja.name}")
    loja_df = pd.read_csv(arquivo_loja)
    print(f"   Registros: {len(loja_df):,}")
    print(f"   Colunas: {list(loja_df.columns)}")
    
    # Verificar coluna de ligação
    coluna_ligacao = None
    if 'numero_os' in oss_df.columns and 'numero_os' in loja_df.columns:
        coluna_ligacao = 'numero_os'
    elif 'OS Lancaster' in oss_df.columns and 'OS Lancaster' in loja_df.columns:
        coluna_ligacao = 'OS Lancaster'
    elif 'OS N°' in oss_df.columns and 'OS N°' in loja_df.columns:
        coluna_ligacao = 'OS N°'
    
    if not coluna_ligacao:
        print("❌ Nenhuma coluna de ligação encontrada")
        return None
    
    print(f"🔗 Usando coluna de ligação: '{coluna_ligacao}'")
    
    # Preparar dados para merge
    oss_prep = oss_df.dropna(subset=[coluna_ligacao])
    loja_prep = loja_df.dropna(subset=[coluna_ligacao])
    
    print(f"OSS válidos: {len(oss_prep):,}")
    print(f"LOJA válidos: {len(loja_prep):,}")
    
    # Fazer merge
    resultado = pd.merge(
        oss_prep,
        loja_prep,
        on=coluna_ligacao,
        how='inner',
        suffixes=('_oss', '_loja')
    )
    
    print(f"✅ Registros unidos: {len(resultado):,}")
    
    if len(resultado) > 0:
        # Verificar UUIDs
        cliente_ids = resultado['cliente_id'].notna().sum() if 'cliente_id' in resultado.columns else 0
        vendedor_uuids = 0
        loja_uuids = 0
        canal_uuids = 0
        
        # Procurar colunas de UUID
        for col in resultado.columns:
            if 'vendedor_uuid' in col.lower() or 'vendedor_id' in col.lower():
                vendedor_uuids = resultado[col].notna().sum()
            elif 'loja_uuid' in col.lower() or 'loja_id' in col.lower():
                loja_uuids = resultado[col].notna().sum()
            elif 'canal' in col.lower() and 'uuid' in col.lower():
                canal_uuids = resultado[col].notna().sum()
        
        print(f"📊 Cliente IDs: {cliente_ids:,}")
        print(f"📊 Vendedor UUIDs: {vendedor_uuids:,}")
        print(f"📊 Loja UUIDs: {loja_uuids:,}")
        print(f"📊 Canal UUIDs: {canal_uuids:,}")
    
    return resultado

def main():
    print("🚀 UNIÃO OSS + LOJA → VENDAS COMPLETAS")
    print("=" * 50)
    
    # 1. Listar arquivos
    arquivos_oss, arquivos_loja = listar_arquivos_finais()
    
    # 2. Identificar lojas
    lojas = []
    for arq in arquivos_oss:
        if arq.startswith("oss_") and arq.endswith("_clientes_ids.csv"):
            loja = arq.replace("oss_", "").replace("_clientes_ids.csv", "")
            lojas.append(loja)
    
    print(f"\n🏪 LOJAS IDENTIFICADAS: {lojas}")
    
    # 3. Processar cada loja
    resultados_finais = []
    
    for loja in lojas:
        resultado_loja = processar_loja(loja)
        if resultado_loja is not None:
            # Adicionar identificação da loja
            resultado_loja['loja_processada'] = loja
            resultados_finais.append(resultado_loja)
    
    # 4. Consolidar resultados
    if resultados_finais:
        vendas_completas = pd.concat(resultados_finais, ignore_index=True)
        
        print(f"\n📊 RESULTADO CONSOLIDADO")
        print("=" * 30)
        print(f"Total de vendas: {len(vendas_completas):,}")
        print(f"Lojas processadas: {vendas_completas['loja_processada'].nunique()}")
        
        # Estatísticas gerais
        total_clientes = vendas_completas['cliente_id'].notna().sum() if 'cliente_id' in vendas_completas.columns else 0
        print(f"Cliente IDs: {total_clientes:,}")
        
        # Salvar resultado
        output_path = Path("data/vendas_para_importar/vendas_oss_loja_unidas.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        vendas_completas.to_csv(output_path, index=False)
        
        print(f"\n💾 ARQUIVO SALVO: {output_path}")
        print(f"📂 Pronto para próximo passo: mapear cliente_uuid")
        
        # Mostrar amostra
        print(f"\n📋 Amostra das colunas:")
        print(f"Colunas disponíveis: {list(vendas_completas.columns)}")
        
    else:
        print("\n❌ Nenhum resultado para consolidar")

if __name__ == "__main__":
    main()