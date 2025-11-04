#!/usr/bin/env python3
"""
EXTRATOR DOS VENDEDORES REAIS FALTANTES - 10.498 REGISTROS
================================================================
Extrai EXATAMENTE os vendedores que estão nos registros
sem UUID para mapeamento e cobertura 100% verdadeira.
================================================================
"""

import pandas as pd
import os
from collections import defaultdict

def extrair_vendedores_reais_faltantes():
    """Extrai vendedores dos registros que realmente não têm UUID"""
    
    base_dir = "data/originais/cxs/extraidos_corrigidos"
    tabelas = ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano2', 'suzano']
    
    vendedores_faltantes = defaultdict(lambda: defaultdict(list))
    estatisticas_detalhadas = defaultdict(lambda: defaultdict(dict))
    todos_vendedores_unicos = set()
    total_registros_sem_uuid = 0
    
    print("🔍 EXTRAINDO VENDEDORES DOS 10.498 REGISTROS SEM UUID")
    print("=" * 70)
    
    for tabela in tabelas:
        print(f"\n📋 TABELA: {tabela.upper()}")
        print("-" * 50)
        
        for loja in lojas:
            arquivo = f"{base_dir}/{tabela}/{tabela}_{loja}_com_uuids_enriquecido_completo.csv"
            
            if os.path.exists(arquivo):
                try:
                    df = pd.read_csv(arquivo)
                    
                    if 'vendedor_uuid' in df.columns:
                        # Identifica registros SEM UUID (nulos)
                        sem_uuid = df[df['vendedor_uuid'].isna()]
                        
                        if not sem_uuid.empty:
                            print(f"🏪 {loja}: {len(sem_uuid)} registros sem UUID")
                            
                            # Busca colunas de vendedor para estes registros
                            colunas_vendedor = [col for col in df.columns if 'vendedor' in col.lower() and col != 'vendedor_uuid']
                            
                            vendedores_encontrados = []
                            
                            for col_vendedor in colunas_vendedor:
                                # Vendedores válidos nos registros sem UUID
                                vendedores_sem_uuid = sem_uuid[col_vendedor].dropna()
                                vendedores_sem_uuid = vendedores_sem_uuid[vendedores_sem_uuid != '']
                                
                                if not vendedores_sem_uuid.empty:
                                    vendedores_unicos = vendedores_sem_uuid.unique()
                                    
                                    print(f"   📊 {col_vendedor}: {len(vendedores_unicos)} vendedores únicos")
                                    
                                    for vendedor in vendedores_unicos:
                                        vendedor_limpo = str(vendedor).strip()
                                        if vendedor_limpo and vendedor_limpo != 'nan':
                                            # Conta quantos registros sem UUID este vendedor tem
                                            count = len(sem_uuid[sem_uuid[col_vendedor] == vendedor])
                                            
                                            vendedores_encontrados.append({
                                                'vendedor': vendedor_limpo,
                                                'registros': count,
                                                'coluna_origem': col_vendedor
                                            })
                                            
                                            todos_vendedores_unicos.add(vendedor_limpo)
                            
                            if vendedores_encontrados:
                                vendedores_faltantes[tabela][loja] = vendedores_encontrados
                                total_registros_sem_uuid += len(sem_uuid)
                                
                                estatisticas_detalhadas[tabela][loja] = {
                                    'registros_sem_uuid': len(sem_uuid),
                                    'total_registros': len(df),
                                    'vendedores_unicos': len(set(v['vendedor'] for v in vendedores_encontrados)),
                                    'percentual_faltante': len(sem_uuid) / len(df) * 100
                                }
                                
                                print(f"   ✅ {len(set(v['vendedor'] for v in vendedores_encontrados))} vendedores únicos identificados")
                            else:
                                print(f"   ⚠️ Registros sem UUID não têm vendedores válidos")
                        else:
                            print(f"✅ {loja}: Todos os {len(df)} registros têm UUID")
                    else:
                        print(f"⚠️ {loja}: Coluna vendedor_uuid não existe")
                        
                except Exception as e:
                    print(f"❌ {loja}: Erro - {e}")
            else:
                print(f"⚠️ {loja}: Arquivo não encontrado")
    
    return vendedores_faltantes, estatisticas_detalhadas, len(todos_vendedores_unicos), total_registros_sem_uuid

def gerar_mapeamento_final_100(vendedores_faltantes, estatisticas):
    """Gera arquivo final para atingir 100% de cobertura"""
    
    print(f"\n🎯 GERANDO MAPEAMENTO FINAL PARA 100% REAL")
    print("=" * 50)
    
    # Coleta todos os vendedores únicos com contexto
    vendedores_contexto = defaultdict(list)
    total_vendedores_unicos = set()
    
    for tabela, lojas_data in vendedores_faltantes.items():
        for loja, vendedores_lista in lojas_data.items():
            for vendedor_info in vendedores_lista:
                vendedor = vendedor_info['vendedor']
                total_vendedores_unicos.add(vendedor)
                
                vendedores_contexto[vendedor].append({
                    'tabela': tabela,
                    'loja': loja,
                    'registros': vendedor_info['registros'],
                    'coluna': vendedor_info['coluna_origem']
                })
    
    # Cria arquivo de mapeamento final
    with open('mapeamento_final_100_real.txt', 'w', encoding='utf-8') as f:
        f.write("# MAPEAMENTO FINAL PARA 100% DE COBERTURA REAL\n")
        f.write("# ============================================\n")
        f.write("# ESTES SÃO OS VENDEDORES DOS 10.498 REGISTROS SEM UUID\n")
        f.write("# INSTRUÇÕES:\n")
        f.write("# 1. Para cada vendedor, adicione o UUID correspondente\n")
        f.write("# 2. Formato: NOME_VENDEDOR = uuid_aqui\n")
        f.write("# 3. Se não deve ter UUID: NOME_VENDEDOR = IGNORAR\n\n")
        
        f.write(f"# TOTAL DE VENDEDORES ÚNICOS: {len(total_vendedores_unicos)}\n")
        f.write(f"# TOTAL DE REGISTROS AFETADOS: {sum(sum(ctx['registros'] for ctx in contextos) for contextos in vendedores_contexto.values())}\n\n")
        
        # Agrupa por similaridade
        grupos = {}
        for vendedor in sorted(total_vendedores_unicos):
            # Normaliza para agrupamento
            chave = vendedor.lower().replace('ã', 'a').replace('ê', 'e').replace('ô', 'o').replace('ç', 'c')
            chave = ''.join(c for c in chave if c.isalnum())
            
            if not chave:  # Se ficou vazio após limpeza
                chave = 'especiais'
            
            if chave not in grupos:
                grupos[chave] = []
            grupos[chave].append(vendedor)
        
        # Escreve por grupos
        for i, (chave, vendedores_grupo) in enumerate(sorted(grupos.items()), 1):
            f.write(f"# GRUPO {i} - {len(vendedores_grupo)} vendedor(es)\n")
            f.write("# " + "-" * 40 + "\n")
            
            for vendedor in sorted(vendedores_grupo):
                contextos = vendedores_contexto[vendedor]
                total_registros = sum(ctx['registros'] for ctx in contextos)
                
                f.write(f"# {vendedor} ({total_registros} registros)\n")
                f.write(f"# Aparece em:\n")
                for ctx in contextos:
                    f.write(f"#   {ctx['tabela']}/{ctx['loja']}: {ctx['registros']} registros ({ctx['coluna']})\n")
                
                f.write(f"{vendedor} = \n\n")
            
            f.write("\n")
    
    print(f"📝 Arquivo criado: mapeamento_final_100_real.txt")
    print(f"👥 Total de vendedores únicos: {len(total_vendedores_unicos)}")
    print(f"📊 Total de registros que ganharão UUID: {sum(sum(ctx['registros'] for ctx in contextos) for contextos in vendedores_contexto.values())}")
    
    return len(total_vendedores_unicos)

def main():
    print("🚀 INICIANDO EXTRAÇÃO FINAL PARA 100% REAL")
    print("=" * 60)
    
    # Extrai os vendedores reais dos registros sem UUID
    vendedores_faltantes, estatisticas, vendedores_unicos, total_registros = extrair_vendedores_reais_faltantes()
    
    print(f"\n📊 RESUMO DA EXTRAÇÃO REAL")
    print("=" * 40)
    print(f"📋 Registros sem UUID processados: {total_registros:,}")
    print(f"👥 Vendedores únicos encontrados: {vendedores_unicos}")
    
    if vendedores_faltantes:
        # Mostra estatísticas por tabela
        print(f"\n📈 ESTATÍSTICAS POR TABELA:")
        for tabela, lojas_data in estatisticas.items():
            total_tabela = sum(dados['registros_sem_uuid'] for dados in lojas_data.values())
            if total_tabela > 0:
                print(f"   📋 {tabela}: {total_tabela} registros sem UUID")
                for loja, dados in lojas_data.items():
                    print(f"      🏪 {loja}: {dados['registros_sem_uuid']} registros ({dados['percentual_faltante']:.1f}% da loja)")
        
        # Gera mapeamento final
        total_vendedores = gerar_mapeamento_final_100(vendedores_faltantes, estatisticas)
        
        print(f"\n🎯 PRÓXIMOS PASSOS PARA 100% REAL:")
        print(f"1. Abra: mapeamento_final_100_real.txt")
        print(f"2. Complete {total_vendedores} mapeamentos de UUID")
        print(f"3. Execute aplicação final")
        print(f"4. ALCANCE 100% DE COBERTURA REAL!")
        print(f"\n✅ EXTRAÇÃO DOS REGISTROS SEM UUID CONCLUÍDA!")
    else:
        print(f"\n🎉 IMPOSSÍVEL! Não há registros sem UUID (mas sabemos que há 10.498!)")

if __name__ == "__main__":
    main()