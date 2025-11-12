#!/usr/bin/env python3
"""
Processamento específico do arquivo ORDEM DE SERVIÇO PDV.csv
Separação por tipo de pagamento: CARNE LANCASTER vs OUTROS
"""

import pandas as pd
import json
from datetime import datetime

def processar_ordem_servico_pdv():
    arquivo_pdv = 'data/originais/controles_gerais/trans_financ/trans_financ_consolidado/por_origem/ORDEM DE SERVIÇO PDV.csv'
    
    print("=== PROCESSAMENTO: ORDEM DE SERVIÇO PDV ===\n")
    
    # Carregar dados
    print("📁 Carregando arquivo...")
    df = pd.read_csv(arquivo_pdv, encoding='utf-8-sig')
    print(f"✅ {len(df):,} registros carregados")
    print()
    
    # Identificar variações do CARNE LANCASTER
    carne_variants = df['Pagamento'].str.contains('CARNE LANCASTER', na=False, case=False)
    
    # Separar dados
    df_carne = df[carne_variants].copy()
    df_outros = df[~carne_variants].copy()
    
    print("📊 RESUMO DA SEPARAÇÃO:")
    print(f"🍖 CARNE LANCASTER: {len(df_carne):,} registros ({len(df_carne)/len(df)*100:.1f}%)")
    print(f"🔷 OUTROS PAGAMENTOS: {len(df_outros):,} registros ({len(df_outros)/len(df)*100:.1f}%)")
    print()
    
    # Análise dos tipos CARNE LANCASTER
    print("🍖 VARIAÇÕES DE CARNE LANCASTER:")
    carne_tipos = df_carne['Pagamento'].value_counts()
    for tipo, qtd in carne_tipos.items():
        print(f"  '{tipo}' -> {qtd:,}")
    print()
    
    # Análise dos OUTROS pagamentos (top 10)
    print("🔷 TOP 10 OUTROS TIPOS DE PAGAMENTO:")
    outros_tipos = df_outros['Pagamento'].value_counts().head(10)
    for tipo, qtd in outros_tipos.items():
        print(f"  {tipo:25} -> {qtd:,}")
    print()
    
    # Análise de clientes únicos
    print("👥 ANÁLISE DE CLIENTES ÚNICOS:")
    clientes_carne = set(df_carne['ID.2'].dropna().astype(str))
    clientes_outros = set(df_outros['ID.2'].dropna().astype(str))
    clientes_ambos = clientes_carne.intersection(clientes_outros)
    
    print(f"Clientes CARNE LANCASTER: {len(clientes_carne):,}")
    print(f"Clientes OUTROS: {len(clientes_outros):,}")
    print(f"Clientes que usam AMBOS: {len(clientes_ambos):,}")
    print()
    
    # Análise de valores
    print("💰 ANÁLISE DE VALORES:")
    valor_carne = df_carne['Vl.movimento'].sum()
    valor_outros = df_outros['Vl.movimento'].sum()
    valor_total = valor_carne + valor_outros
    
    print(f"Valor CARNE LANCASTER: R$ {valor_carne:,.2f} ({valor_carne/valor_total*100:.1f}%)")
    print(f"Valor OUTROS: R$ {valor_outros:,.2f} ({valor_outros/valor_total*100:.1f}%)")
    print(f"Valor TOTAL: R$ {valor_total:,.2f}")
    print()
    
    # Criar pasta de destino
    import os
    os.makedirs('data/originais/controles_gerais/trans_financ/separados_por_pagamento', exist_ok=True)
    
    # Salvar arquivos separados
    print("💾 SALVANDO ARQUIVOS SEPARADOS...")
    
    arquivo_carne = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/ordem_servico_pdv_carne_lancaster.csv'
    arquivo_outros = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/ordem_servico_pdv_outros_pagamentos.csv'
    
    df_carne.to_csv(arquivo_carne, index=False, encoding='utf-8-sig')
    df_outros.to_csv(arquivo_outros, index=False, encoding='utf-8-sig')
    
    print(f"✅ CARNE LANCASTER salvo: {arquivo_carne}")
    print(f"✅ OUTROS PAGAMENTOS salvo: {arquivo_outros}")
    print()
    
    # Relatório de processamento
    relatorio = {
        'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'arquivo_origem': arquivo_pdv,
        'total_registros': int(len(df)),
        'registros_carne_lancaster': int(len(df_carne)),
        'registros_outros_pagamentos': int(len(df_outros)),
        'percentual_carne': round(len(df_carne)/len(df)*100, 2),
        'percentual_outros': round(len(df_outros)/len(df)*100, 2),
        'valor_total': float(valor_total),
        'valor_carne_lancaster': float(valor_carne),
        'valor_outros_pagamentos': float(valor_outros),
        'clientes_unicos_carne': len(clientes_carne),
        'clientes_unicos_outros': len(clientes_outros),
        'clientes_ambos_tipos': len(clientes_ambos),
        'variantes_carne_lancaster': dict(carne_tipos),
        'top_outros_pagamentos': dict(outros_tipos)
    }
    
    # Converter tipos numpy para tipos Python básicos
    for key, value in relatorio.items():
        if hasattr(value, 'item'):  # numpy types
            relatorio[key] = value.item()
        elif isinstance(value, dict):
            # Converter valores do dict também
            for k, v in value.items():
                if hasattr(v, 'item'):
                    value[k] = v.item()
    
    arquivo_relatorio = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/relatorio_separacao_ordem_servico_pdv.json'
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print(f"📋 Relatório salvo: {arquivo_relatorio}")
    
    # Resumo executivo
    resumo = f"""
=== RESUMO EXECUTIVO: ORDEM DE SERVIÇO PDV ===
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

📊 TOTAIS:
• Total de registros: {len(df):,}
• CARNE LANCASTER: {len(df_carne):,} ({len(df_carne)/len(df)*100:.1f}%)
• OUTROS PAGAMENTOS: {len(df_outros):,} ({len(df_outros)/len(df)*100:.1f}%)

💰 VALORES:
• Total: R$ {valor_total:,.2f}
• Carne Lancaster: R$ {valor_carne:,.2f} ({valor_carne/valor_total*100:.1f}%)
• Outros: R$ {valor_outros:,.2f} ({valor_outros/valor_total*100:.1f}%)

👥 CLIENTES:
• Únicos Carne Lancaster: {len(clientes_carne):,}
• Únicos Outros: {len(clientes_outros):,}
• Clientes que usam ambos: {len(clientes_ambos):,}

📁 ARQUIVOS GERADOS:
• {arquivo_carne}
• {arquivo_outros}
• {arquivo_relatorio}

✅ Processamento concluído com sucesso!
"""
    
    arquivo_resumo = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/RESUMO_ORDEM_SERVICO_PDV.txt'
    with open(arquivo_resumo, 'w', encoding='utf-8') as f:
        f.write(resumo)
    
    print(resumo)
    print(f"📄 Resumo salvo: {arquivo_resumo}")
    
    return df_carne, df_outros

if __name__ == "__main__":
    df_carne, df_outros = processar_ordem_servico_pdv()