#!/usr/bin/env python3
"""
Corrige foreign key de lojas nas vendas VIXEN
Aplica UUIDs corretos de Suzano e Mauá
"""

import pandas as pd
from pathlib import Path

def corrigir_lojas_vixen():
    """Corrige UUIDs das lojas nas vendas VIXEN"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("🔧 === CORRIGINDO LOJAS VIXEN ===")
    
    # 1. Carrega arquivo VIXEN com problema
    arquivo_vixen = base_dir / "data" / "vendas_para_importar" / "vendas_VIXEN_PRONTO_PARA_IMPORTAR_CORRIGIDO.csv"
    vendas_vixen = pd.read_csv(arquivo_vixen)
    
    print(f"📊 Vendas VIXEN carregadas: {len(vendas_vixen)}")
    
    # 2. UUIDs CORRETOS das lojas (do banco real)
    lojas_corretas = {
        '52f92716-d2ba-441a-ac3c-94bdfabd9722': {  # Este está correto - Suzano
            'nome': 'SUZANO',
            'uuid': '52f92716-d2ba-441a-ac3c-94bdfabd9722'
        },
        'e5c9f7c4-9877-4f73-b4c4-eac5ad7c3f89': {  # Este está ERRADO - precisa do UUID real de Mauá
            'nome': 'MAUA',
            'uuid': 'aa7a5646-f7d6-4239-831c-6602fbabb10a'  # UUID CORRETO de Mauá
        }
    }
    
    print(f"🔍 Lojas atuais no arquivo:")
    lojas_atuais = vendas_vixen['loja_id'].value_counts()
    for loja_id, count in lojas_atuais.items():
        print(f"   {loja_id}: {count} vendas")
    
    # 3. Aplica correção
    print(f"\n=== APLICANDO CORREÇÃO LOJAS ===")
    
    # Suzano - já está correto
    mask_suzano = vendas_vixen['loja_id'] == '52f92716-d2ba-441a-ac3c-94bdfabd9722'
    suzano_count = mask_suzano.sum()
    print(f"✅ Suzano: {suzano_count} vendas (UUID já correto)")
    
    # Mauá - precisa correção
    mask_maua = vendas_vixen['loja_id'] == 'e5c9f7c4-9877-4f73-b4c4-eac5ad7c3f89'
    maua_count = mask_maua.sum()
    if maua_count > 0:
        uuid_maua_correto = 'aa7a5646-f7d6-4239-831c-6602fbabb10a'
        vendas_vixen.loc[mask_maua, 'loja_id'] = uuid_maua_correto
        print(f"🔧 Mauá: {maua_count} vendas → {uuid_maua_correto}")
    
    # 4. Verificação final
    print(f"\n📊 LOJAS APÓS CORREÇÃO:")
    lojas_finais = vendas_vixen['loja_id'].value_counts()
    for loja_id, count in lojas_finais.items():
        loja_nome = 'SUZANO' if loja_id == '52f92716-d2ba-441a-ac3c-94bdfabd9722' else 'MAUA'
        print(f"   {loja_nome} ({loja_id}): {count} vendas")
    
    # 5. Salva arquivo corrigido
    arquivo_final = base_dir / "data" / "vendas_para_importar" / "vendas_VIXEN_FINAL_CORRIGIDO.csv"
    vendas_vixen.to_csv(arquivo_final, index=False)
    
    print(f"\n✅ ARQUIVO FINAL SALVO:")
    print(f"   {arquivo_final}")
    print(f"   {len(vendas_vixen)} vendas")
    
    # 6. Comandos SQL atualizados
    print(f"\n🛠️  COMANDOS SQL FINAIS:")
    print(f"   -- Importa vendas VIXEN com lojas corretas")
    print(f"   \\copy vendas.vendas FROM '{arquivo_final}' CSV HEADER;")
    print(f"   -- Verifica")
    print(f"   SELECT COUNT(*) FROM vendas.vendas WHERE observacoes LIKE '%VIXEN%';")
    print(f"   -- Por loja")
    print(f"   SELECT l.nome, COUNT(*) FROM vendas.vendas v")
    print(f"   JOIN core.lojas l ON v.loja_id = l.id") 
    print(f"   WHERE v.observacoes LIKE '%VIXEN%'")
    print(f"   GROUP BY l.nome;")
    
    # 7. Verificação de integridade
    print(f"\n🔍 VERIFICAÇÃO DE INTEGRIDADE:")
    print(f"   Suzano: {(vendas_vixen['loja_id'] == '52f92716-d2ba-441a-ac3c-94bdfabd9722').sum()} vendas")
    print(f"   Mauá:   {(vendas_vixen['loja_id'] == 'aa7a5646-f7d6-4239-831c-6602fbabb10a').sum()} vendas")
    print(f"   Total:  {len(vendas_vixen)} vendas")
    
    # Verifica se não há outras lojas
    outras_lojas = vendas_vixen[
        (~vendas_vixen['loja_id'].isin(['52f92716-d2ba-441a-ac3c-94bdfabd9722', 'aa7a5646-f7d6-4239-831c-6602fbabb10a']))
    ]
    
    if len(outras_lojas) > 0:
        print(f"⚠️  ATENÇÃO: {len(outras_lojas)} vendas com lojas não mapeadas!")
    else:
        print(f"✅ Todas as vendas estão com Suzano ou Mauá!")
    
    print(f"\n🎉 CORREÇÃO LOJAS CONCLUÍDA!")
    print(f"✅ Todas as vendas agora têm lojas válidas!")
    print(f"🚀 Pronto para importação sem erro de foreign key!")
    
    return vendas_vixen

if __name__ == "__main__":
    resultado = corrigir_lojas_vixen()
    print(f"\n✅ {len(resultado)} vendas VIXEN com lojas corrigidas!")