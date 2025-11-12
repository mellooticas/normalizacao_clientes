#!/usr/bin/env python3
"""
Normalização da coluna Nro.operação nos arquivos trans_financ
Remove prefixos 48 e 42, mantendo apenas os números das OSs
"""

import pandas as pd
import numpy as np
from datetime import datetime

def normalizar_nro_operacao():
    print("=== NORMALIZAÇÃO NÚMEROS DE OPERAÇÃO ===\n")
    
    # Arquivos para processar
    arquivos = [
        {
            'nome': 'OUTROS PAGAMENTOS',
            'arquivo': 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/ordem_servico_pdv_outros_pagamentos_com_uuid.csv',
            'arquivo_saida': 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/ordem_servico_pdv_outros_pagamentos_com_uuid_normalizado.csv'
        },
        {
            'nome': 'REC. CORRENTISTA',
            'arquivo': 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/rec_correntista_com_uuid.csv',
            'arquivo_saida': 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/rec_correntista_com_uuid_normalizado.csv'
        }
    ]
    
    estatisticas_geral = {}
    
    for item in arquivos:
        print(f"📁 Processando: {item['nome']}")
        print("-" * 50)
        
        # Carregar arquivo
        df = pd.read_csv(item['arquivo'], encoding='utf-8-sig')
        print(f"✅ {len(df):,} registros carregados")
        
        # Analisar coluna Nro.operação antes da normalização
        print("\n🔍 ANÁLISE ANTES DA NORMALIZAÇÃO:")
        nro_operacao_original = df['Nro.operação'].dropna()
        
        print(f"Valores não nulos: {len(nro_operacao_original):,}")
        print(f"Valores únicos: {nro_operacao_original.nunique():,}")
        
        if len(nro_operacao_original) > 0:
            print("Exemplos originais:")
            for i, valor in enumerate(nro_operacao_original.head(5)):
                print(f"  {i+1}. {valor}")
        
        # Função para normalizar números de operação
        def normalizar_operacao(valor):
            if pd.isna(valor):
                return valor
            
            # Converter para string
            str_valor = str(valor)
            
            # Remover .0 se existir
            if str_valor.endswith('.0'):
                str_valor = str_valor[:-2]
            
            # Verificar se começa com 48 ou 42 e remover
            if str_valor.startswith('48') and len(str_valor) > 2:
                return str_valor[2:]  # Remove os primeiros 2 caracteres (48)
            elif str_valor.startswith('42') and len(str_valor) > 2:
                return str_valor[2:]  # Remove os primeiros 2 caracteres (42)
            else:
                return str_valor
        
        # Aplicar normalização
        print("\n🔧 APLICANDO NORMALIZAÇÃO...")
        df['Nro.operacao_original'] = df['Nro.operação'].copy()  # Backup
        df['Nro.operação'] = df['Nro.operação'].apply(normalizar_operacao)
        
        # Converter para numérico quando possível
        df['Nro.operacao_normalizado'] = pd.to_numeric(df['Nro.operação'], errors='coerce')
        
        # Analisar depois da normalização
        print("\n📊 ANÁLISE APÓS NORMALIZAÇÃO:")
        nro_operacao_normalizado = df['Nro.operação'].dropna()
        
        print(f"Valores não nulos: {len(nro_operacao_normalizado):,}")
        print(f"Valores únicos: {nro_operacao_normalizado.nunique():,}")
        
        if len(nro_operacao_normalizado) > 0:
            print("Exemplos normalizados:")
            for i, valor in enumerate(nro_operacao_normalizado.head(5)):
                print(f"  {i+1}. {valor}")
        
        # Estatísticas de transformação
        transformados = 0
        nao_transformados = 0
        
        for orig, norm in zip(df['Nro.operacao_original'], df['Nro.operação']):
            if pd.notna(orig) and pd.notna(norm):
                if str(orig) != str(norm):
                    transformados += 1
                else:
                    nao_transformados += 1
        
        print(f"\n📈 ESTATÍSTICAS DE TRANSFORMAÇÃO:")
        print(f"Registros transformados: {transformados:,}")
        print(f"Registros não alterados: {nao_transformados:,}")
        
        # Salvar arquivo normalizado
        print(f"\n💾 Salvando arquivo normalizado...")
        df.to_csv(item['arquivo_saida'], index=False, encoding='utf-8-sig')
        print(f"✅ Salvo: {item['arquivo_saida']}")
        
        # Guardar estatísticas
        estatisticas_geral[item['nome']] = {
            'total_registros': len(df),
            'valores_originais_nao_nulos': len(nro_operacao_original),
            'valores_normalizados_nao_nulos': len(nro_operacao_normalizado),
            'valores_unicos_original': nro_operacao_original.nunique() if len(nro_operacao_original) > 0 else 0,
            'valores_unicos_normalizado': nro_operacao_normalizado.nunique() if len(nro_operacao_normalizado) > 0 else 0,
            'transformados': transformados,
            'nao_transformados': nao_transformados
        }
        
        print("\n" + "="*60 + "\n")
    
    # Relatório consolidado
    print("📋 RELATÓRIO CONSOLIDADO DA NORMALIZAÇÃO:")
    print("="*60)
    
    for nome, stats in estatisticas_geral.items():
        print(f"\n{nome}:")
        print(f"  • Total de registros: {stats['total_registros']:,}")
        print(f"  • Valores originais: {stats['valores_originais_nao_nulos']:,} únicos: {stats['valores_unicos_original']:,}")
        print(f"  • Valores normalizados: {stats['valores_normalizados_nao_nulos']:,} únicos: {stats['valores_unicos_normalizado']:,}")
        print(f"  • Transformações: {stats['transformados']:,}")
    
    # Salvar relatório
    import json
    relatorio = {
        'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'descricao': 'Normalização de números de operação - remoção de prefixos 48 e 42',
        'arquivos_processados': len(arquivos),
        'estatisticas': estatisticas_geral
    }
    
    arquivo_relatorio = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/relatorio_normalizacao_nro_operacao.json'
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Relatório salvo: {arquivo_relatorio}")
    
    # Resumo executivo
    resumo = f"""
=== NORMALIZAÇÃO NRO.OPERAÇÃO CONCLUÍDA ===
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

📊 ARQUIVOS PROCESSADOS: {len(arquivos)}

🔧 TRANSFORMAÇÕES REALIZADAS:
"""
    
    for nome, stats in estatisticas_geral.items():
        resumo += f"\n• {nome}:\n"
        resumo += f"  - {stats['transformados']:,} registros normalizados\n"
        resumo += f"  - Prefixos 48/42 removidos dos números de OS\n"
    
    resumo += f"""
📁 ARQUIVOS GERADOS:
• ordem_servico_pdv_outros_pagamentos_com_uuid_normalizado.csv
• rec_correntista_com_uuid_normalizado.csv
• {arquivo_relatorio}

✅ Normalização concluída com sucesso!
Os números de OS agora estão padronizados sem prefixos.
"""
    
    arquivo_resumo = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/RESUMO_NORMALIZACAO_OS.txt'
    with open(arquivo_resumo, 'w', encoding='utf-8') as f:
        f.write(resumo)
    
    print(resumo)
    print(f"📋 Resumo salvo: {arquivo_resumo}")

if __name__ == "__main__":
    normalizar_nro_operacao()