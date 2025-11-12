#!/usr/bin/env python3
"""
EXTRATOR DE VENDEDORES SEM UUID POR LOJA
================================================================
Extrai vendedores sem UUID organizados por loja específica,
facilitando o mapeamento correto baseado no contexto da loja.
================================================================
"""

import pandas as pd
import os
from collections import defaultdict

def extrair_vendedores_por_loja():
    """Extrai vendedores sem UUID organizados por loja"""
    
    base_dir = "data/originais/cxs/extraidos_corrigidos"
    
    # Todas as tabelas e lojas
    tabelas = ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano2', 'suzano']
    
    vendedores_por_loja = defaultdict(lambda: defaultdict(set))
    estatisticas_detalhadas = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    print("🔍 EXTRAINDO VENDEDORES SEM UUID POR LOJA E TABELA")
    print("=" * 60)
    
    for loja in lojas:
        print(f"\n🏪 LOJA: {loja.upper()}")
        print("-" * 50)
        
        for tabela in tabelas:
            arquivo = f"{base_dir}/{tabela}/{tabela}_{loja}_com_uuids_enriquecido_completo.csv"
            
            if os.path.exists(arquivo):
                try:
                    df = pd.read_csv(arquivo)
                    
                    # Verifica se tem coluna vendedor_uuid e vendedor
                    if 'vendedor_uuid' in df.columns and 'vendedor' in df.columns:
                        # Registros sem UUID
                        sem_uuid = df[df['vendedor_uuid'].isna() | (df['vendedor_uuid'] == '') | (df['vendedor_uuid'] == 'N/A')]
                        
                        if not sem_uuid.empty:
                            # Vendedores únicos sem UUID nesta tabela/loja
                            vendedores_unicos = sem_uuid['vendedor'].dropna().unique()
                            vendedores_unicos = [v for v in vendedores_unicos if str(v).strip() != '' and str(v) != 'nan']
                            
                            if vendedores_unicos:
                                for vendedor in vendedores_unicos:
                                    vendedor_limpo = str(vendedor).strip()
                                    vendedores_por_loja[loja][tabela].add(vendedor_limpo)
                                    
                                    # Conta quantos registros este vendedor tem
                                    count_vendedor = len(sem_uuid[sem_uuid['vendedor'] == vendedor])
                                    estatisticas_detalhadas[loja][tabela][vendedor_limpo] = count_vendedor
                                
                                print(f"   📋 {tabela}: {len(vendedores_unicos)} vendedores únicos ({len(sem_uuid)} registros)")
                            else:
                                print(f"   ✅ {tabela}: Todos têm UUID")
                        else:
                            print(f"   ✅ {tabela}: Todos têm UUID")
                    else:
                        if 'vendedor' not in df.columns:
                            print(f"   ⚠️ {tabela}: Sem coluna vendedor")
                        else:
                            print(f"   ⚠️ {tabela}: Sem coluna vendedor_uuid")
                            
                except Exception as e:
                    print(f"   ❌ {tabela}: Erro - {e}")
            else:
                print(f"   ⚠️ {tabela}: Arquivo não encontrado")
    
    return vendedores_por_loja, estatisticas_detalhadas

def gerar_mapeamento_por_loja(vendedores_por_loja, estatisticas_detalhadas):
    """Gera arquivo de mapeamento organizado por loja"""
    
    print(f"\n🎯 GERANDO MAPEAMENTO ORGANIZADO POR LOJA")
    print("=" * 50)
    
    # Conta total de vendedores únicos
    todos_vendedores_globais = set()
    total_por_loja = {}
    
    for loja, tabelas in vendedores_por_loja.items():
        vendedores_loja = set()
        for tabela, vendedores in tabelas.items():
            vendedores_loja.update(vendedores)
            todos_vendedores_globais.update(vendedores)
        total_por_loja[loja] = len(vendedores_loja)
    
    # Cria arquivo de mapeamento
    with open('mapeamento_vendedores_por_loja.txt', 'w', encoding='utf-8') as f:
        f.write("# MAPEAMENTO DE VENDEDORES POR LOJA - CONTEXTO ESPECÍFICO\n")
        f.write("# ======================================================\n")
        f.write("# INSTRUÇÕES:\n")
        f.write("# 1. Cada vendedor está listado na loja onde aparece\n")
        f.write("# 2. Formato: NOME_VENDEDOR = uuid_aqui\n")
        f.write("# 3. Se não deve ter UUID: NOME_VENDEDOR = IGNORAR\n")
        f.write("# 4. Duplicatas entre lojas serão unificadas automaticamente\n\n")
        
        f.write(f"# TOTAL GERAL: {len(todos_vendedores_globais)} vendedores únicos em {len(vendedores_por_loja)} lojas\n\n")
        
        # Para cada loja
        for loja in ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano2', 'suzano']:
            if loja in vendedores_por_loja and vendedores_por_loja[loja]:
                f.write(f"# {'='*60}\n")
                f.write(f"# 🏪 LOJA: {loja.upper()}\n")
                f.write(f"# {'='*60}\n")
                f.write(f"# Total de vendedores únicos nesta loja: {total_por_loja.get(loja, 0)}\n\n")
                
                # Para cada tabela nesta loja
                for tabela in ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']:
                    if tabela in vendedores_por_loja[loja] and vendedores_por_loja[loja][tabela]:
                        f.write(f"# 📋 TABELA: {tabela.upper()}\n")
                        f.write(f"# {'-'*40}\n")
                        
                        # Vendedores ordenados
                        vendedores_ordenados = sorted(list(vendedores_por_loja[loja][tabela]))
                        
                        for vendedor in vendedores_ordenados:
                            count = estatisticas_detalhadas[loja][tabela].get(vendedor, 0)
                            f.write(f"# {vendedor} ({count} registros)\n")
                            f.write(f"{vendedor} = \n\n")
                        
                        f.write("\n")
                
                f.write("\n")
    
    print(f"📝 Arquivo criado: mapeamento_vendedores_por_loja.txt")
    print(f"📊 Total de vendedores únicos globais: {len(todos_vendedores_globais)}")
    
    # Estatísticas por loja
    print(f"\n📊 VENDEDORES SEM UUID POR LOJA:")
    for loja, total in total_por_loja.items():
        if total > 0:
            print(f"   🏪 {loja}: {total} vendedores únicos")
    
    return len(todos_vendedores_globais)

def main():
    print("🚀 INICIANDO EXTRAÇÃO DE VENDEDORES POR LOJA")
    print("=" * 60)
    
    # Extrai vendedores por loja
    vendedores_por_loja, estatisticas_detalhadas = extrair_vendedores_por_loja()
    
    if not vendedores_por_loja:
        print("\n🎉 PARABÉNS! TODOS OS VENDEDORES JÁ POSSUEM UUID!")
        return
    
    # Gera mapeamento por loja
    total_vendedores = gerar_mapeamento_por_loja(vendedores_por_loja, estatisticas_detalhadas)
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print(f"1. Abra: mapeamento_vendedores_por_loja.txt")
    print(f"2. Complete os UUIDs por contexto de loja")
    print(f"3. Execute aplicação para atingir cobertura máxima")
    print(f"\n✅ EXTRAÇÃO POR LOJA CONCLUÍDA!")

if __name__ == "__main__":
    main()