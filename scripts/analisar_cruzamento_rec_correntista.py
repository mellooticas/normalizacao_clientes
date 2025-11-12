#!/usr/bin/env python3
"""
Análise do arquivo REC. CORRENTISTA.csv e cruzamento com ordem_servico_pdv_outros_pagamentos_com_uuid.csv
Investigar coluna Nr.identificação para fazer o cruzamento correto
"""

import pandas as pd
import numpy as np
from datetime import datetime

def analisar_cruzamento_rec_correntista():
    print("=== ANÁLISE E CRUZAMENTO: REC. CORRENTISTA ===\n")
    
    # Carregar arquivo REC. CORRENTISTA
    arquivo_rec = 'data/originais/controles_gerais/trans_financ/trans_financ_consolidado/por_origem/REC. CORRENTISTA.csv'
    
    print("📁 Carregando REC. CORRENTISTA...")
    df_rec = pd.read_csv(arquivo_rec, encoding='utf-8-sig')
    print(f"✅ {len(df_rec):,} registros carregados")
    print()
    
    # Carregar arquivo OUTROS PAGAMENTOS com UUID
    arquivo_outros = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/ordem_servico_pdv_outros_pagamentos_com_uuid.csv'
    
    print("📁 Carregando OUTROS PAGAMENTOS com UUID...")
    df_outros = pd.read_csv(arquivo_outros, encoding='utf-8-sig')
    print(f"✅ {len(df_outros):,} registros carregados")
    print()
    
    # Análise da coluna Nr.identificação em REC. CORRENTISTA
    print("🔍 ANÁLISE DA COLUNA Nr.identificação em REC. CORRENTISTA:")
    
    # Verificar valores únicos
    nr_identificacao_rec = df_rec['Nr.identificação'].dropna()
    print(f"Total de Nr.identificação não nulos: {len(nr_identificacao_rec):,}")
    print(f"Valores únicos: {nr_identificacao_rec.nunique():,}")
    
    # Mostrar alguns exemplos
    print("Exemplos de Nr.identificação:")
    for i, valor in enumerate(nr_identificacao_rec.head(10)):
        print(f"  {i+1:2d}. {valor}")
    print()
    
    # Análise da coluna Nr.identificação em OUTROS PAGAMENTOS
    print("🔍 ANÁLISE DA COLUNA Nr.identificação em OUTROS PAGAMENTOS:")
    
    nr_identificacao_outros = df_outros['Nr.identificação'].dropna()
    print(f"Total de Nr.identificação não nulos: {len(nr_identificacao_outros):,}")
    print(f"Valores únicos: {nr_identificacao_outros.nunique():,}")
    
    # Mostrar alguns exemplos
    print("Exemplos de Nr.identificação:")
    for i, valor in enumerate(nr_identificacao_outros.head(10)):
        print(f"  {i+1:2d}. {valor}")
    print()
    
    # CRUZAMENTO: Verificar interseção
    print("🔗 CRUZAMENTO DAS COLUNAS Nr.identificação:")
    
    # Converter para string para comparação
    set_rec = set(nr_identificacao_rec.astype(str))
    set_outros = set(nr_identificacao_outros.astype(str))
    
    # Interseção
    intersecao = set_rec.intersection(set_outros)
    
    print(f"Valores únicos em REC. CORRENTISTA: {len(set_rec):,}")
    print(f"Valores únicos em OUTROS PAGAMENTOS: {len(set_outros):,}")
    print(f"Valores em comum (interseção): {len(intersecao):,}")
    
    if len(intersecao) > 0:
        percentual_rec = (len(intersecao) / len(set_rec)) * 100
        percentual_outros = (len(intersecao) / len(set_outros)) * 100
        print(f"Cobertura REC. CORRENTISTA: {percentual_rec:.1f}%")
        print(f"Cobertura OUTROS PAGAMENTOS: {percentual_outros:.1f}%")
    print()
    
    # Se há interseção, fazer o cruzamento detalhado
    if len(intersecao) > 0:
        print("✅ ENCONTRADA CORRESPONDÊNCIA! Fazendo cruzamento detalhado...")
        
        # Preparar dados para cruzamento
        df_rec['Nr.identificacao_str'] = df_rec['Nr.identificação'].astype(str)
        df_outros['Nr.identificacao_str'] = df_outros['Nr.identificação'].astype(str)
        
        # Fazer merge
        df_cruzado = df_rec.merge(
            df_outros[['Nr.identificacao_str', 'uuid_forma_pagamento', 'tipo_pagamento_normalizado']],
            on='Nr.identificacao_str',
            how='left',
            suffixes=('_rec', '_outros')
        )
        
        # Estatísticas do cruzamento
        registros_com_uuid = df_cruzado['uuid_forma_pagamento'].notna().sum()
        registros_sem_uuid = len(df_cruzado) - registros_com_uuid
        
        print(f"📊 RESULTADO DO CRUZAMENTO:")
        print(f"Registros REC. CORRENTISTA com UUID: {registros_com_uuid:,}")
        print(f"Registros REC. CORRENTISTA sem UUID: {registros_sem_uuid:,}")
        print(f"Taxa de correspondência: {(registros_com_uuid/len(df_cruzado))*100:.1f}%")
        print()
        
        # Análise dos UUIDs encontrados
        if registros_com_uuid > 0:
            print("📋 UUIDs ENCONTRADOS NO CRUZAMENTO:")
            uuid_stats = df_cruzado[df_cruzado['uuid_forma_pagamento'].notna()].groupby(['uuid_forma_pagamento', 'tipo_pagamento_normalizado']).size().reset_index(name='quantidade')
            uuid_stats = uuid_stats.sort_values('quantidade', ascending=False)
            
            for _, row in uuid_stats.iterrows():
                print(f"  {row['uuid_forma_pagamento']} | {row['tipo_pagamento_normalizado']:25} | {row['quantidade']:,}")
        print()
        
        # Salvar resultado do cruzamento
        print("💾 SALVANDO RESULTADO DO CRUZAMENTO...")
        
        arquivo_cruzado = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/rec_correntista_com_uuid_cruzado.csv'
        df_cruzado.to_csv(arquivo_cruzado, index=False, encoding='utf-8-sig')
        
        print(f"✅ Arquivo salvo: {arquivo_cruzado}")
        
        # Relatório
        relatorio = {
            'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'arquivo_rec_correntista': arquivo_rec,
            'arquivo_outros_pagamentos': arquivo_outros,
            'arquivo_resultado': arquivo_cruzado,
            'total_registros_rec': int(len(df_rec)),
            'total_registros_outros': int(len(df_outros)),
            'valores_unicos_rec': len(set_rec),
            'valores_unicos_outros': len(set_outros),
            'intersecao_valores': len(intersecao),
            'registros_com_uuid': int(registros_com_uuid),
            'registros_sem_uuid': int(registros_sem_uuid),
            'taxa_correspondencia': round((registros_com_uuid/len(df_cruzado))*100, 2),
            'uuids_encontrados': [
                {
                    'uuid': row['uuid_forma_pagamento'],
                    'tipo': row['tipo_pagamento_normalizado'],
                    'quantidade': int(row['quantidade'])
                }
                for _, row in uuid_stats.iterrows()
            ] if registros_com_uuid > 0 else []
        }
        
        import json
        arquivo_relatorio = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/relatorio_cruzamento_rec_correntista.json'
        with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Relatório salvo: {arquivo_relatorio}")
        
    else:
        print("❌ NENHUMA CORRESPONDÊNCIA ENCONTRADA")
        print("As colunas Nr.identificação não têm valores em comum.")
        
        # Verificar se existe outro campo de ligação
        print("\n🔍 INVESTIGANDO OUTRAS POSSIBILIDADES DE CRUZAMENTO...")
        
        # Verificar se ID fin. ou Nro.operação podem ser usados
        print("Campos disponíveis para cruzamento:")
        print("REC. CORRENTISTA:")
        print(f"  - ID fin.: {df_rec['ID fin.'].nunique():,} valores únicos")
        print(f"  - Nro.operação: {df_rec['Nro.operação'].nunique():,} valores únicos")
        print(f"  - ID operação: {df_rec['ID operação'].nunique():,} valores únicos")
        
        print("OUTROS PAGAMENTOS:")
        print(f"  - ID fin.: {df_outros['ID fin.'].nunique():,} valores únicos")
        print(f"  - Nro.operação: {df_outros['Nro.operação'].nunique():,} valores únicos")
        print(f"  - ID operação: {df_outros['ID operação'].nunique():,} valores únicos")
    
    # Resumo executivo
    resumo = f"""
=== ANÁLISE DE CRUZAMENTO: REC. CORRENTISTA ===
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

📊 DADOS ANALISADOS:
• REC. CORRENTISTA: {len(df_rec):,} registros
• OUTROS PAGAMENTOS: {len(df_outros):,} registros

🔗 CRUZAMENTO POR Nr.identificação:
• Valores únicos REC: {len(set_rec):,}
• Valores únicos OUTROS: {len(set_outros):,}
• Interseção: {len(intersecao):,}

"""
    
    if len(intersecao) > 0:
        resumo += f"""✅ CRUZAMENTO REALIZADO:
• Registros com UUID: {registros_com_uuid:,}
• Taxa de correspondência: {(registros_com_uuid/len(df_cruzado))*100:.1f}%

📁 ARQUIVOS GERADOS:
• {arquivo_cruzado}
• {arquivo_relatorio}
"""
    else:
        resumo += "❌ Nenhuma correspondência encontrada"
    
    arquivo_resumo = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/RESUMO_CRUZAMENTO_REC_CORRENTISTA.txt'
    with open(arquivo_resumo, 'w', encoding='utf-8') as f:
        f.write(resumo)
    
    print(resumo)
    print(f"📄 Resumo salvo: {arquivo_resumo}")

if __name__ == "__main__":
    analisar_cruzamento_rec_correntista()