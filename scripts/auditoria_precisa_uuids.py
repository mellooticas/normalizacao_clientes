#!/usr/bin/env python3
"""
AUDITORIA PRECISA DE UUIDs - VERSÃO CORRIGIDA
================================================================
Conta corretamente UUIDs considerando vazios, N/A e nulos.
================================================================
"""

import pandas as pd
import os

def auditoria_precisa_uuids():
    """Auditoria precisa que considera todos os tipos de valores vazios"""
    
    base_dir = "data/originais/cxs/extraidos_corrigidos"
    tabelas = ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano2', 'suzano']
    
    print("🔍 AUDITORIA PRECISA DE UUIDs")
    print("=" * 50)
    
    total_registros_global = 0
    total_com_vendedor_uuid = 0
    total_com_loja_uuid = 0
    total_com_pagamento_uuid = 0
    total_aplicavel_pagamento = 0
    
    detalhes_por_tabela = {}
    
    for tabela in tabelas:
        print(f"\n📋 TABELA: {tabela.upper()}")
        print("-" * 40)
        
        detalhes_tabela = {}
        
        for loja in lojas:
            arquivo = f"{base_dir}/{tabela}/{tabela}_{loja}_com_uuids_enriquecido_completo.csv"
            
            if os.path.exists(arquivo):
                try:
                    df = pd.read_csv(arquivo)
                    total_registros = len(df)
                    total_registros_global += total_registros
                    
                    # Função para contar UUIDs válidos
                    def contar_uuids_validos(coluna):
                        if coluna not in df.columns:
                            return 0, total_registros
                        
                        # UUIDs válidos: não nulos, não vazios, não 'N/A'
                        validos = df[coluna].notna() & (df[coluna] != '') & (df[coluna] != 'N/A')
                        return validos.sum(), total_registros
                    
                    # Contar UUIDs
                    loja_com, loja_total = contar_uuids_validos('loja_id')
                    vendedor_com, vendedor_total = contar_uuids_validos('vendedor_uuid')
                    
                    # Forma pagamento só existe em algumas tabelas
                    if 'forma_pagamento_uuid' in df.columns:
                        pagamento_com, pagamento_total = contar_uuids_validos('forma_pagamento_uuid')
                        total_aplicavel_pagamento += pagamento_total
                        total_com_pagamento_uuid += pagamento_com
                    else:
                        pagamento_com, pagamento_total = 0, 0
                    
                    total_com_loja_uuid += loja_com
                    total_com_vendedor_uuid += vendedor_com
                    
                    # Calcula percentuais
                    loja_pct = (loja_com / loja_total * 100) if loja_total > 0 else 0
                    vendedor_pct = (vendedor_com / vendedor_total * 100) if vendedor_total > 0 else 0
                    pagamento_pct = (pagamento_com / pagamento_total * 100) if pagamento_total > 0 else 0
                    
                    print(f"🏪 {loja}:")
                    print(f"   📊 Total: {total_registros}")
                    print(f"   🏢 Loja UUID: {loja_com}/{loja_total} ({loja_pct:.1f}%)")
                    if pagamento_total > 0:
                        print(f"   💳 Pagamento UUID: {pagamento_com}/{pagamento_total} ({pagamento_pct:.1f}%)")
                    else:
                        print(f"   💳 Pagamento UUID: Campo não existe")
                    print(f"   👤 Vendedor UUID: {vendedor_com}/{vendedor_total} ({vendedor_pct:.1f}%)")
                    
                    detalhes_tabela[loja] = {
                        'total': total_registros,
                        'loja_uuid': {'com': loja_com, 'total': loja_total, 'pct': loja_pct},
                        'vendedor_uuid': {'com': vendedor_com, 'total': vendedor_total, 'pct': vendedor_pct},
                        'pagamento_uuid': {'com': pagamento_com, 'total': pagamento_total, 'pct': pagamento_pct}
                    }
                    
                except Exception as e:
                    print(f"🏪 {loja}: ❌ Erro - {e}")
            else:
                print(f"🏪 {loja}: ⚠️ Arquivo não encontrado")
        
        detalhes_por_tabela[tabela] = detalhes_tabela
    
    # Resumo final
    print(f"\n🎯 RESUMO FINAL PRECISO")
    print("=" * 40)
    print(f"📊 Total de registros: {total_registros_global:,}")
    
    loja_pct_global = (total_com_loja_uuid / total_registros_global * 100) if total_registros_global > 0 else 0
    vendedor_pct_global = (total_com_vendedor_uuid / total_registros_global * 100) if total_registros_global > 0 else 0
    pagamento_pct_global = (total_com_pagamento_uuid / total_aplicavel_pagamento * 100) if total_aplicavel_pagamento > 0 else 0
    
    print(f"🏢 Loja UUID: {total_com_loja_uuid:,}/{total_registros_global:,} ({loja_pct_global:.1f}%)")
    print(f"👤 Vendedor UUID: {total_com_vendedor_uuid:,}/{total_registros_global:,} ({vendedor_pct_global:.1f}%)")
    print(f"💳 Pagamento UUID: {total_com_pagamento_uuid:,}/{total_aplicavel_pagamento:,} ({pagamento_pct_global:.1f}%)")
    
    # Verifica se é realmente 100% ou próximo
    if vendedor_pct_global >= 99.9:
        print(f"\n🎉 PARABÉNS! VENDEDOR UUID ESTÁ PRATICAMENTE 100%!")
        print(f"📊 Apenas {total_registros_global - total_com_vendedor_uuid} registros sem UUID de {total_registros_global:,}")
    elif vendedor_pct_global >= 95:
        print(f"\n✅ EXCELENTE! VENDEDOR UUID ACIMA DE 95%!")
    else:
        print(f"\n⚠️ VENDEDOR UUID AINDA PRECISA MELHORAR")
    
    return detalhes_por_tabela

def main():
    print("🚀 INICIANDO AUDITORIA PRECISA")
    print("=" * 50)
    
    detalhes = auditoria_precisa_uuids()
    
    print(f"\n✅ AUDITORIA PRECISA CONCLUÍDA!")

if __name__ == "__main__":
    main()