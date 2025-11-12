#!/usr/bin/env python3
"""
Verificação final: quão próximos estamos dos 100%?
Combina todas as estratégias desenvolvidas
"""

import pandas as pd
from pathlib import Path

def verificar_cobertura_total():
    """Verifica a cobertura total combinando todas as estratégias"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("🎯 === VERIFICAÇÃO FINAL DE COBERTURA === 🎯")
    
    # 1. Carrega vendas base
    vendas_df = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_corrigido_com_os_originais.csv")
    vendas_df['cliente_id_str'] = vendas_df['cliente_id'].astype(str).str.replace('.0', '')
    
    total_vendas = len(vendas_df)
    print(f"📊 Total vendas: {total_vendas}")
    
    # 2. ESTRATÉGIA 1: UUIDs reais do banco (da análise anterior)
    # Simulando resultado da análise anterior: ~58%
    # (usaremos o arquivo final que já tínhamos)
    
    if (base_dir / "data" / "vendas_para_importar" / "vendas_final_uuids_banco.csv").exists():
        vendas_banco = pd.read_csv(base_dir / "data" / "vendas_para_importar" / "vendas_final_uuids_banco.csv")
        com_uuid_banco = vendas_banco['cliente_id'].notna().sum()
        print(f"✅ ESTRATÉGIA 1 - UUIDs reais banco: {com_uuid_banco} vendas")
    else:
        com_uuid_banco = int(total_vendas * 0.58)  # Estimativa baseada na análise anterior
        print(f"✅ ESTRATÉGIA 1 - UUIDs reais banco: ~{com_uuid_banco} vendas (estimativa)")
    
    # 3. ESTRATÉGIA 2: Matches por variações de nomes (acabamos de fazer!)
    matches_nomes = pd.read_csv(base_dir / "data" / "matches_nomes_variacoes.csv")
    matches_nomes['oss_cliente_id_str'] = matches_nomes['oss_cliente_id'].astype(str)
    
    # IDs que têm match por nomes
    ids_com_match_nomes = set(matches_nomes['oss_cliente_id_str'])
    
    # Conta vendas com match por nomes
    vendas_com_nomes = vendas_df[vendas_df['cliente_id_str'].isin(ids_com_match_nomes)]
    com_uuid_nomes = len(vendas_com_nomes)
    
    print(f"✅ ESTRATÉGIA 2 - Matches variações nomes: {com_uuid_nomes} vendas")
    
    # 4. ESTRATÉGIA 3: Lookup tradicional
    # Para IDs que não foram cobertos pelas estratégias anteriores
    uuid_consolidado = pd.read_csv(base_dir / "data" / "clientes_uuid" / "todos_clientes_uuid_consolidado.csv")
    uuid_consolidado['id_legado_str'] = uuid_consolidado['id_legado'].astype(str).str.replace('.0', '')
    ids_com_uuid_lookup = set(uuid_consolidado['id_legado_str'])
    
    # IDs que já foram cobertos
    ids_ja_cobertos = ids_com_match_nomes  # Começamos com os matches de nomes
    
    # IDs ainda descobertos que estão no lookup
    ids_restantes = set(vendas_df['cliente_id_str']) - ids_ja_cobertos
    ids_lookup_restantes = ids_restantes & ids_com_uuid_lookup
    
    vendas_lookup_restantes = vendas_df[vendas_df['cliente_id_str'].isin(ids_lookup_restantes)]
    com_uuid_lookup = len(vendas_lookup_restantes)
    
    print(f"✅ ESTRATÉGIA 3 - Lookup tradicional restante: {com_uuid_lookup} vendas")
    
    # 5. TOTAL COMBINADO
    ids_total_cobertos = ids_com_match_nomes | ids_lookup_restantes
    vendas_total_cobertas = vendas_df[vendas_df['cliente_id_str'].isin(ids_total_cobertos)]
    total_com_uuid = len(vendas_total_cobertas)
    
    # IDs ainda sem cobertura
    ids_sem_uuid = set(vendas_df['cliente_id_str']) - ids_total_cobertos
    vendas_sem_uuid = len(ids_sem_uuid)
    
    # 6. RESULTADO FINAL
    print(f"\n🚀 === RESULTADO FINAL COMBINADO === 🚀")
    print(f"📊 Total vendas: {total_vendas}")
    print(f"✅ COM UUID (estratégias 2+3): {total_com_uuid} ({total_com_uuid/total_vendas*100:.1f}%)")
    print(f"❌ SEM UUID: {vendas_sem_uuid} ({vendas_sem_uuid/total_vendas*100:.1f}%)")
    
    print(f"\n📈 Detalhamento:")
    print(f"  🎯 Matches variações nomes: {com_uuid_nomes} vendas")
    print(f"  📋 Lookup tradicional: {com_uuid_lookup} vendas")
    print(f"  🆕 Precisam UUID novo: {vendas_sem_uuid} vendas")
    
    # 7. Análise dos IDs sem UUID
    if vendas_sem_uuid > 0:
        print(f"\n🔍 === ANÁLISE DOS IDs SEM UUID ===")
        vendas_sem_uuid_df = vendas_df[vendas_df['cliente_id_str'].isin(ids_sem_uuid)]
        
        print(f"Amostra IDs sem UUID:")
        amostra = vendas_sem_uuid_df.head(10)
        for _, row in amostra.iterrows():
            print(f"  ID: {row['cliente_id']}, Nome: {row['nome_cliente_temp']}")
        
        # Padrões dos IDs sem UUID
        padroes_sem_uuid = {}
        for id_sem in ids_sem_uuid:
            if id_sem.startswith('5000'):
                padroes_sem_uuid['5000xxx'] = padroes_sem_uuid.get('5000xxx', 0) + 1
            elif id_sem.startswith('6000'):
                padroes_sem_uuid['6000xxx'] = padroes_sem_uuid.get('6000xxx', 0) + 1
            elif id_sem.startswith('2'):
                padroes_sem_uuid['2xxxxxx'] = padroes_sem_uuid.get('2xxxxxx', 0) + 1
            else:
                padroes_sem_uuid['outros'] = padroes_sem_uuid.get('outros', 0) + 1
        
        print(f"\nPadrões IDs sem UUID:")
        for padrao, count in padroes_sem_uuid.items():
            print(f"  {padrao}: {count} IDs")
    
    # 8. PROJEÇÃO PARA 100%
    if vendas_sem_uuid <= total_vendas * 0.05:  # Se menos de 5% sem UUID
        print(f"\n🎉 === MUITO PRÓXIMO DOS 100%! ===")
        print(f"🚀 Apenas {vendas_sem_uuid} vendas ({vendas_sem_uuid/total_vendas*100:.1f}%) precisam de UUID novo!")
        print(f"✅ Podemos facilmente chegar a 100% criando UUIDs para os restantes!")
    
    return {
        'total_vendas': total_vendas,
        'com_uuid': total_com_uuid,
        'sem_uuid': vendas_sem_uuid,
        'percentual': total_com_uuid/total_vendas*100,
        'ids_sem_uuid': ids_sem_uuid
    }

if __name__ == "__main__":
    resultado = verificar_cobertura_total()
    print(f"\n📊 RESUMO FINAL:")
    print(f"🎯 {resultado['percentual']:.1f}% de cobertura alcançada!")
    print(f"🚀 Faltam apenas {resultado['sem_uuid']} vendas para 100%!")