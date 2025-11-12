#!/usr/bin/env python3
"""
Script para mapear vendedores das vendas com vendedores normalizados
"""

import pandas as pd
from pathlib import Path

def mapear_vendedores():
    """Mapeia vendedores das vendas com os normalizados"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== MAPEAMENTO DE VENDEDORES ===")
    
    # 1. Carrega vendedores normalizados
    vendedores_uuid = pd.read_csv(base_dir / "VENDEDORES_UNICOS_UUID.csv")
    print(f"Vendedores normalizados disponíveis: {len(vendedores_uuid)}")
    
    # 2. Carrega vendas originais para ver nomes
    vendas_orig = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_oss_lojas_unidas.csv", low_memory=False)
    
    # 3. Cria mapeamento nome -> UUID das vendas
    mapeamento_vendas = vendas_orig[['vendedor_nome_normalizado_loja', 'vendedor_uuid_loja']].drop_duplicates()
    mapeamento_vendas = mapeamento_vendas.dropna()
    
    print(f"\nVendedores nas vendas: {len(mapeamento_vendas)}")
    
    # 4. Tenta mapear cada vendedor
    mapeamento_correto = {}
    vendedores_nao_encontrados = []
    
    for _, row in mapeamento_vendas.iterrows():
        nome_vendedor = row['vendedor_nome_normalizado_loja']
        uuid_antigo = row['vendedor_uuid_loja']
        
        # Busca exata
        encontrado = vendedores_uuid[vendedores_uuid['nome_padronizado'] == nome_vendedor]
        
        if len(encontrado) > 0:
            uuid_correto = encontrado.iloc[0]['uuid']
            mapeamento_correto[uuid_antigo] = uuid_correto
            print(f"✅ {nome_vendedor}: {uuid_antigo} -> {uuid_correto}")
        else:
            # Busca parcial por palavras
            palavras = nome_vendedor.split()
            encontrado_parcial = None
            
            for palavra in palavras:
                if len(palavra) > 3:  # Evita palavras muito pequenas
                    parcial = vendedores_uuid[vendedores_uuid['nome_padronizado'].str.contains(palavra, case=False, na=False)]
                    if len(parcial) > 0:
                        encontrado_parcial = parcial.iloc[0]
                        break
            
            if encontrado_parcial is not None:
                uuid_correto = encontrado_parcial['uuid']
                mapeamento_correto[uuid_antigo] = uuid_correto
                print(f"📝 {nome_vendedor}: {uuid_antigo} -> {uuid_correto} ({encontrado_parcial['nome_padronizado']})")
            else:
                vendedores_nao_encontrados.append((nome_vendedor, uuid_antigo))
                print(f"❌ {nome_vendedor}: {uuid_antigo} -> NÃO ENCONTRADO")
    
    # 5. Estatísticas
    print(f"\n=== ESTATÍSTICAS ===")
    print(f"Vendedores mapeados: {len(mapeamento_correto)}")
    print(f"Vendedores não encontrados: {len(vendedores_nao_encontrados)}")
    
    # 6. Para vendedores não encontrados, usa um vendedor genérico
    if len(vendedores_nao_encontrados) > 0:
        print(f"\n=== VENDEDORES NÃO ENCONTRADOS ===")
        
        # Procura por vendedor genérico tipo "NAN" ou cria um mapeamento padrão
        vendedor_generico = vendedores_uuid[vendedores_uuid['nome_padronizado'].str.contains('NAN|GENERICO|PADRAO', case=False, na=False)]
        
        if len(vendedor_generico) > 0:
            uuid_generico = vendedor_generico.iloc[0]['uuid']
            nome_generico = vendedor_generico.iloc[0]['nome_padronizado']
            print(f"Usando vendedor genérico: {nome_generico} ({uuid_generico})")
            
            for nome_vendedor, uuid_antigo in vendedores_nao_encontrados:
                mapeamento_correto[uuid_antigo] = uuid_generico
                print(f"  {nome_vendedor}: {uuid_antigo} -> {uuid_generico}")
        else:
            # Usa o primeiro vendedor da lista como padrão
            uuid_generico = vendedores_uuid.iloc[0]['uuid']
            nome_generico = vendedores_uuid.iloc[0]['nome_padronizado']
            print(f"Usando primeiro vendedor como padrão: {nome_generico} ({uuid_generico})")
            
            for nome_vendedor, uuid_antigo in vendedores_nao_encontrados:
                mapeamento_correto[uuid_antigo] = uuid_generico
                print(f"  {nome_vendedor}: {uuid_antigo} -> {uuid_generico}")
    
    return mapeamento_correto

if __name__ == "__main__":
    mapeamento = mapear_vendedores()
    
    # Salva mapeamento para uso posterior
    import json
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    with open(base_dir / "mapeamento_vendedores_correto.json", 'w') as f:
        json.dump(mapeamento, f, indent=2)
    
    print(f"\n💾 Mapeamento salvo em mapeamento_vendedores_correto.json")
    print(f"📊 Total de mapeamentos: {len(mapeamento)}")