#!/usr/bin/env python3
"""
Extrair vendedores únicos que precisam de UUID
"""

import pandas as pd
import glob
from pathlib import Path

def extrair_vendedores_sem_uuid():
    """Extrai todos os vendedores únicos que não têm UUID"""
    print("🔍 EXTRAINDO VENDEDORES ÚNICOS SEM UUID")
    print("="*50)
    
    vendedores_sem_uuid = set()
    estatisticas = {}
    
    # Buscar em todas as tabelas
    tabelas = ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']
    
    for tabela in tabelas:
        print(f"\n📋 {tabela.upper()}:")
        
        caminho = f"data/originais/cxs/extraidos_corrigidos/{tabela}/*_enriquecido_completo.csv"
        arquivos = glob.glob(caminho)
        arquivos_lojas = [a for a in arquivos if 'todas_lojas' not in a]
        
        for arquivo in arquivos_lojas:
            loja = Path(arquivo).stem.split('_')[1]
            
            try:
                df = pd.read_csv(arquivo)
                
                # Registros sem vendedor UUID
                sem_uuid = df[df['vendedor_uuid'].isna()]
                
                # Identificar campo de vendedor
                campo_vendedor = None
                if 'vendedor' in df.columns:
                    campo_vendedor = 'vendedor'
                elif 'vendedor_nome_normalizado' in df.columns:
                    campo_vendedor = 'vendedor_nome_normalizado'
                
                if campo_vendedor and len(sem_uuid) > 0:
                    vendedores_unicos = sem_uuid[campo_vendedor].dropna().unique()
                    
                    # Filtrar vendedores válidos (não números ou valores estranhos)
                    vendedores_validos = []
                    for v in vendedores_unicos:
                        v_str = str(v).strip()
                        if (len(v_str) > 1 and 
                            not v_str.isdigit() and 
                            v_str.upper() not in ['NAN', 'NULL', 'NONE']):
                            vendedores_validos.append(v_str)
                    
                    if vendedores_validos:
                        vendedores_sem_uuid.update(vendedores_validos)
                        print(f"   🏪 {loja}: {len(vendedores_validos)} vendedores únicos")
                        estatisticas[f"{tabela}_{loja}"] = len(vendedores_validos)
                
            except Exception as e:
                print(f"   ❌ Erro {arquivo}: {e}")
    
    return vendedores_sem_uuid, estatisticas

def exibir_vendedores_para_uuid(vendedores_sem_uuid):
    """Exibe lista de vendedores que precisam de UUID"""
    print(f"\n" + "="*60)
    print(f"👥 VENDEDORES QUE PRECISAM DE UUID")
    print("="*60)
    
    vendedores_ordenados = sorted(list(vendedores_sem_uuid))
    
    print(f"📊 Total de vendedores únicos sem UUID: {len(vendedores_ordenados)}")
    print()
    
    print("📋 LISTA COMPLETA (para você mapear UUIDs):")
    print("-" * 50)
    
    for i, vendedor in enumerate(vendedores_ordenados, 1):
        print(f"{i:3d}. {vendedor}")
    
    print(f"\n🎯 PRÓXIMO PASSO:")
    print("Para cada vendedor acima, você precisa fornecer:")
    print("- Nome normalizado (se necessário)")
    print("- UUID correspondente")
    print("- Ou indicar se deve ser criado novo UUID")

if __name__ == "__main__":
    vendedores, stats = extrair_vendedores_sem_uuid()
    exibir_vendedores_para_uuid(vendedores)