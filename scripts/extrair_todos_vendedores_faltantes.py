#!/usr/bin/env python3
"""
EXTRATOR COMPLETO DE VENDEDORES FALTANTES - 100% REAL
================================================================
Extrai TODOS os vendedores sem UUID de TODAS as tabelas
para mapeamento completo e cobertura 100% verdadeira.
================================================================
"""

import pandas as pd
import os
from collections import defaultdict

def extrair_todos_vendedores_faltantes():
    """Extrai TODOS os vendedores sem UUID de todas as tabelas"""
    
    base_dir = "data/originais/cxs/extraidos_corrigidos"
    tabelas = ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano2', 'suzano']
    
    vendedores_faltantes = defaultdict(lambda: defaultdict(list))
    estatisticas = defaultdict(lambda: defaultdict(dict))
    total_vendedores_unicos = set()
    total_registros_sem_uuid = 0
    
    print("🔍 EXTRAINDO TODOS OS VENDEDORES FALTANTES")
    print("=" * 60)
    
    for tabela in tabelas:
        print(f"\n📋 TABELA: {tabela.upper()}")
        print("-" * 50)
        
        for loja in lojas:
            arquivo = f"{base_dir}/{tabela}/{tabela}_{loja}_com_uuids_enriquecido_completo.csv"
            
            if os.path.exists(arquivo):
                try:
                    df = pd.read_csv(arquivo)
                    
                    # Identifica qual coluna usar para vendedor
                    coluna_vendedor = None
                    if 'vendedor' in df.columns:
                        coluna_vendedor = 'vendedor'
                    elif 'vendedor_nome_normalizado' in df.columns:
                        coluna_vendedor = 'vendedor_nome_normalizado'
                    
                    if coluna_vendedor and 'vendedor_uuid' in df.columns:
                        # Identifica registros sem UUID
                        sem_uuid = df[
                            (df['vendedor_uuid'].isna() | 
                             (df['vendedor_uuid'] == '') | 
                             (df['vendedor_uuid'] == 'N/A')) &
                            (df[coluna_vendedor].notna() & 
                             (df[coluna_vendedor] != ''))
                        ]
                        
                        if not sem_uuid.empty:
                            # Vendedores únicos sem UUID
                            vendedores_unicos = sem_uuid[coluna_vendedor].unique()
                            vendedores_limpos = [str(v).strip() for v in vendedores_unicos if str(v).strip() != '' and str(v) != 'nan']
                            
                            if vendedores_limpos:
                                for vendedor in vendedores_limpos:
                                    count = len(sem_uuid[sem_uuid[coluna_vendedor] == vendedor])
                                    vendedores_faltantes[tabela][loja].append({
                                        'vendedor': vendedor,
                                        'registros': count,
                                        'coluna_origem': coluna_vendedor
                                    })
                                    total_vendedores_unicos.add(f"{tabela}_{loja}_{vendedor}")
                                
                                total_registros_sem_uuid += len(sem_uuid)
                                
                                print(f"🏪 {loja}: {len(vendedores_limpos)} vendedores únicos sem UUID ({len(sem_uuid)} registros)")
                                
                                estatisticas[tabela][loja] = {
                                    'vendedores_unicos': len(vendedores_limpos),
                                    'registros_sem_uuid': len(sem_uuid),
                                    'total_registros': len(df),
                                    'coluna_vendedor': coluna_vendedor
                                }
                            else:
                                print(f"✅ {loja}: Todos vendedores têm UUID ({len(df)} registros)")
                        else:
                            print(f"✅ {loja}: Todos vendedores têm UUID ({len(df)} registros)")
                    else:
                        if coluna_vendedor is None:
                            print(f"⚠️ {loja}: Coluna de vendedor não encontrada")
                        else:
                            print(f"⚠️ {loja}: Coluna vendedor_uuid não encontrada")
                        
                except Exception as e:
                    print(f"❌ {loja}: Erro - {e}")
            else:
                print(f"⚠️ {loja}: Arquivo não encontrado")
    
    return vendedores_faltantes, estatisticas, len(total_vendedores_unicos), total_registros_sem_uuid

def gerar_mapeamento_100_completo(vendedores_faltantes, estatisticas):
    """Gera arquivo de mapeamento completo para 100%"""
    
    print(f"\n🎯 GERANDO MAPEAMENTO COMPLETO PARA 100%")
    print("=" * 50)
    
    # Agrupa todos os vendedores únicos
    todos_vendedores_globais = set()
    vendedores_por_contexto = defaultdict(list)
    
    for tabela, lojas_data in vendedores_faltantes.items():
        for loja, vendedores_lista in lojas_data.items():
            for vendedor_info in vendedores_lista:
                vendedor = vendedor_info['vendedor']
                todos_vendedores_globais.add(vendedor)
                vendedores_por_contexto[vendedor].append({
                    'tabela': tabela,
                    'loja': loja,
                    'registros': vendedor_info['registros'],
                    'coluna': vendedor_info['coluna_origem']
                })
    
    # Cria arquivo de mapeamento
    with open('mapeamento_vendedores_100_real.txt', 'w', encoding='utf-8') as f:
        f.write("# MAPEAMENTO COMPLETO DE VENDEDORES - 100% REAL\n")
        f.write("# ==============================================\n")
        f.write("# INSTRUÇÕES:\n")
        f.write("# 1. Para cada vendedor abaixo, adicione o UUID correspondente\n")
        f.write("# 2. Formato: NOME_VENDEDOR = uuid_aqui\n")
        f.write("# 3. Se não deve ter UUID: NOME_VENDEDOR = IGNORAR\n")
        f.write("# 4. Vendedores aparecem em múltiplas tabelas/lojas\n\n")
        
        f.write(f"# TOTAL DE VENDEDORES ÚNICOS: {len(todos_vendedores_globais)}\n\n")
        
        # Agrupa por similaridade para facilitar mapeamento
        grupos = {}
        for vendedor in sorted(todos_vendedores_globais):
            # Cria chave de agrupamento
            chave_base = vendedor.lower().replace('ã', 'a').replace('ê', 'e').replace('ô', 'o').replace('ç', 'c')
            chave_base = ''.join(c for c in chave_base if c.isalnum())
            
            if chave_base not in grupos:
                grupos[chave_base] = []
            grupos[chave_base].append(vendedor)
        
        # Escreve agrupado
        for i, (chave, vendedores_grupo) in enumerate(sorted(grupos.items()), 1):
            f.write(f"# GRUPO {i} - {len(vendedores_grupo)} vendedor(es)\n")
            f.write("# " + "-" * 40 + "\n")
            
            for vendedor in sorted(vendedores_grupo):
                # Mostra contexto onde aparece
                contextos = vendedores_por_contexto[vendedor]
                total_registros_vendedor = sum(ctx['registros'] for ctx in contextos)
                
                f.write(f"# {vendedor} - {total_registros_vendedor} registros em:\n")
                for ctx in contextos:
                    f.write(f"#   {ctx['tabela']}/{ctx['loja']}: {ctx['registros']} registros ({ctx['coluna']})\n")
                
                f.write(f"{vendedor} = \n\n")
            
            f.write("\n")
    
    print(f"📝 Arquivo criado: mapeamento_vendedores_100_real.txt")
    print(f"📊 Total de vendedores únicos: {len(todos_vendedores_globais)}")
    
    return len(todos_vendedores_globais)

def main():
    print("🚀 INICIANDO EXTRAÇÃO COMPLETA PARA 100% REAL")
    print("=" * 60)
    
    # Extrai todos os vendedores faltantes
    vendedores_faltantes, estatisticas, combinacoes_unicas, total_registros = extrair_todos_vendedores_faltantes()
    
    print(f"\n📊 RESUMO DA EXTRAÇÃO")
    print("=" * 40)
    print(f"📋 Total de registros sem UUID: {total_registros:,}")
    print(f"🔗 Combinações únicas (tabela_loja_vendedor): {combinacoes_unicas:,}")
    
    if vendedores_faltantes:
        # Gera mapeamento completo
        total_vendedores = gerar_mapeamento_100_completo(vendedores_faltantes, estatisticas)
        
        print(f"\n🎯 PRÓXIMOS PASSOS PARA 100%:")
        print(f"1. Abra: mapeamento_vendedores_100_real.txt")
        print(f"2. Complete {total_vendedores} mapeamentos de UUID")
        print(f"3. Execute aplicação final para atingir 100%")
        print(f"\n✅ EXTRAÇÃO PARA 100% REAL CONCLUÍDA!")
    else:
        print(f"\n🎉 INCRÍVEL! JÁ TEMOS 100% DE COBERTURA EM TODAS AS TABELAS!")

if __name__ == "__main__":
    main()