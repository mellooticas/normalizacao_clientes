#!/usr/bin/env python3
"""
Normalização da coluna Nro.operação apenas no arquivo ordem_servico_pdv_outros_pagamentos_com_uuid
Remove prefixo 48, mantendo apenas os números das OSs
A ligação com REC. CORRENTISTA será feita através do campo ID.2 (cliente)
"""

import pandas as pd
import numpy as np
from datetime import datetime

def normalizar_nro_operacao_outros_pagamentos():
    print("=== NORMALIZAÇÃO NRO.OPERAÇÃO - OUTROS PAGAMENTOS ===\n")
    
    # Arquivo para processar
    arquivo_entrada = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/ordem_servico_pdv_outros_pagamentos_com_uuid.csv'
    arquivo_saida = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/ordem_servico_pdv_outros_pagamentos_com_uuid_normalizado.csv'
    
    print("📁 Carregando OUTROS PAGAMENTOS...")
    df = pd.read_csv(arquivo_entrada, encoding='utf-8-sig')
    print(f"✅ {len(df):,} registros carregados")
    print()
    
    # Analisar coluna Nro.operação antes da normalização
    print("🔍 ANÁLISE ANTES DA NORMALIZAÇÃO:")
    nro_operacao_original = df['Nro.operação'].dropna()
    
    print(f"Valores não nulos: {len(nro_operacao_original):,}")
    print(f"Valores únicos: {nro_operacao_original.nunique():,}")
    
    print("Exemplos originais:")
    for i, valor in enumerate(nro_operacao_original.head(10)):
        print(f"  {i+1:2d}. {valor}")
    print()
    
    # Função para normalizar números de operação
    def normalizar_operacao(valor):
        if pd.isna(valor):
            return valor
        
        # Converter para string
        str_valor = str(valor)
        
        # Remover .0 se existir
        if str_valor.endswith('.0'):
            str_valor = str_valor[:-2]
        
        # Verificar se começa com 48 e remover
        if str_valor.startswith('48') and len(str_valor) > 2:
            return str_valor[2:]  # Remove os primeiros 2 caracteres (48)
        else:
            return str_valor
    
    # Criar backup da coluna original
    df['Nro.operacao_original'] = df['Nro.operação'].copy()
    
    # Aplicar normalização
    print("🔧 APLICANDO NORMALIZAÇÃO...")
    df['Nro.operação'] = df['Nro.operação'].apply(normalizar_operacao)
    
    # Analisar depois da normalização
    print("\n📊 ANÁLISE APÓS NORMALIZAÇÃO:")
    nro_operacao_normalizado = df['Nro.operação'].dropna()
    
    print(f"Valores não nulos: {len(nro_operacao_normalizado):,}")
    print(f"Valores únicos: {nro_operacao_normalizado.nunique():,}")
    
    print("Exemplos normalizados:")
    for i, valor in enumerate(nro_operacao_normalizado.head(10)):
        print(f"  {i+1:2d}. {valor}")
    print()
    
    # Estatísticas de transformação
    transformados = 0
    nao_transformados = 0
    
    for orig, norm in zip(df['Nro.operacao_original'], df['Nro.operação']):
        if pd.notna(orig) and pd.notna(norm):
            if str(orig) != str(norm):
                transformados += 1
            else:
                nao_transformados += 1
    
    print("📈 ESTATÍSTICAS DE TRANSFORMAÇÃO:")
    print(f"Registros transformados: {transformados:,}")
    print(f"Registros não alterados: {nao_transformados:,}")
    print(f"Taxa de transformação: {(transformados/(transformados+nao_transformados))*100:.1f}%")
    print()
    
    # Analisar campo ID.2 para confirmar ligação com REC. CORRENTISTA
    print("🔗 ANÁLISE DO CAMPO ID.2 (LIGAÇÃO COM REC. CORRENTISTA):")
    id2_nao_nulos = df['ID.2'].dropna()
    id2_nao_zeros = df[(df['ID.2'].notna()) & (df['ID.2'] != 0)]
    
    print(f"Total ID.2 não nulos: {len(id2_nao_nulos):,}")
    print(f"Total ID.2 não nulos e ≠ 0: {len(id2_nao_zeros):,}")
    print(f"ID.2 únicos: {id2_nao_zeros['ID.2'].nunique():,}")
    
    if len(id2_nao_zeros) > 0:
        print("Exemplos de ID.2 para ligação:")
        for i, valor in enumerate(id2_nao_zeros['ID.2'].head(5)):
            print(f"  {i+1}. {valor}")
    print()
    
    # Salvar arquivo normalizado
    print("💾 Salvando arquivo normalizado...")
    df.to_csv(arquivo_saida, index=False, encoding='utf-8-sig')
    print(f"✅ Arquivo salvo: {arquivo_saida}")
    print()
    
    # Relatório
    import json
    relatorio = {
        'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'arquivo_origem': arquivo_entrada,
        'arquivo_destino': arquivo_saida,
        'descricao': 'Normalização de Nro.operação - remoção do prefixo 48',
        'total_registros': len(df),
        'valores_originais': {
            'nao_nulos': len(nro_operacao_original),
            'unicos': nro_operacao_original.nunique()
        },
        'valores_normalizados': {
            'nao_nulos': len(nro_operacao_normalizado),
            'unicos': nro_operacao_normalizado.nunique()
        },
        'transformacoes': {
            'registros_transformados': transformados,
            'registros_nao_alterados': nao_transformados,
            'taxa_transformacao': round((transformados/(transformados+nao_transformados))*100, 2) if (transformados+nao_transformados) > 0 else 0
        },
        'ligacao_rec_correntista': {
            'campo_ligacao': 'ID.2',
            'id2_nao_nulos': len(id2_nao_nulos),
            'id2_validos': len(id2_nao_zeros),
            'id2_unicos': id2_nao_zeros['ID.2'].nunique() if len(id2_nao_zeros) > 0 else 0
        }
    }
    
    arquivo_relatorio = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/relatorio_normalizacao_outros_pagamentos.json'
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print(f"📋 Relatório salvo: {arquivo_relatorio}")
    
    # Resumo executivo
    resumo = f"""
=== NORMALIZAÇÃO NRO.OPERAÇÃO - OUTROS PAGAMENTOS ===
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

📊 PROCESSAMENTO:
• Total de registros: {len(df):,}
• Nro.operação transformados: {transformados:,}
• Taxa de transformação: {(transformados/(transformados+nao_transformados))*100:.1f}%

🔧 NORMALIZAÇÃO APLICADA:
• Removido prefixo "48" dos números de operação
• Mantidos apenas os números das OSs
• Coluna original preservada como backup

🔗 LIGAÇÃO COM REC. CORRENTISTA:
• Campo de ligação: ID.2 (cliente)
• ID.2 válidos disponíveis: {len(id2_nao_zeros):,}
• Clientes únicos: {id2_nao_zeros['ID.2'].nunique() if len(id2_nao_zeros) > 0 else 0:,}

📁 ARQUIVOS GERADOS:
• {arquivo_saida}
• {arquivo_relatorio}

✅ Normalização concluída!
REC. CORRENTISTA mantido inalterado - ligação via ID.2
"""
    
    arquivo_resumo = 'data/originais/controles_gerais/trans_financ/separados_por_pagamento/RESUMO_NORMALIZACAO_OUTROS_PAGAMENTOS.txt'
    with open(arquivo_resumo, 'w', encoding='utf-8') as f:
        f.write(resumo)
    
    print(resumo)
    print(f"📄 Resumo salvo: {arquivo_resumo}")
    
    return df

if __name__ == "__main__":
    df_normalizado = normalizar_nro_operacao_outros_pagamentos()