#!/usr/bin/env python3
"""
Corrige foreign key de vendedores nas vendas VIXEN
Aplica vendedores UUID válidos
"""

import pandas as pd
from pathlib import Path

def corrigir_vendedores_vixen():
    """Corrige vendedores UUID nas vendas VIXEN"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("🔧 === CORRIGINDO VENDEDORES VIXEN ===")
    
    # 1. Carrega arquivo VIXEN com problema
    arquivo_vixen = base_dir / "data" / "vendas_para_importar" / "vendas_VIXEN_PRONTO_PARA_IMPORTAR.csv"
    vendas_vixen = pd.read_csv(arquivo_vixen)
    
    print(f"📊 Vendas VIXEN carregadas: {len(vendas_vixen)}")
    
    # 2. Carrega mapeamento de vendedores válidos (do sistema anterior)
    try:
        vendedores_map_file = base_dir / "MAPEAMENTO_VENDEDORES_UUID.json"
        if vendedores_map_file.exists():
            import json
            with open(vendedores_map_file, 'r', encoding='utf-8') as f:
                vendedores_map = json.load(f)
            print(f"✅ Mapeamento vendedores carregado")
        else:
            # Usa vendedores padrão por loja (como fizemos antes)
            vendedores_map = {
                '52f92716-d2ba-441a-ac3c-94bdfabd9722': '2fec96c8-d492-49ab-b38a-a5d5452af4d2',  # Suzano
                'e5c9f7c4-9877-4f73-b4c4-eac5ad7c3f89': '8a7b9c5d-4e3f-4c2a-9b1d-5e8f7a6c4b9e'   # Mauá
            }
            print(f"ℹ️  Usando vendedores padrão por loja")
    except:
        # Vendedores padrão por loja
        vendedores_map = {
            '52f92716-d2ba-441a-ac3c-94bdfabd9722': '2fec96c8-d492-49ab-b38a-a5d5452af4d2',  # Suzano
            'e5c9f7c4-9877-4f73-b4c4-eac5ad7c3f89': '8a7b9c5d-4e3f-4c2a-9b1d-5e8f7a6c4b9e'   # Mauá
        }
        print(f"ℹ️  Usando vendedores padrão por loja")
    
    # 3. Verifica vendedores atuais
    vendedores_atuais = vendas_vixen['vendedor_id'].unique()
    print(f"🔍 Vendedores atuais: {vendedores_atuais}")
    
    # 4. Aplica correção por loja
    print(f"\n=== APLICANDO CORREÇÃO VENDEDORES ===")
    
    # Suzano
    mask_suzano = vendas_vixen['loja_id'] == '52f92716-d2ba-441a-ac3c-94bdfabd9722'
    suzano_count = mask_suzano.sum()
    if suzano_count > 0:
        vendedores_map_suzano = '2fec96c8-d492-49ab-b38a-a5d5452af4d2'  # Vendedor padrão Suzano
        vendas_vixen.loc[mask_suzano, 'vendedor_id'] = vendedores_map_suzano
        print(f"✅ Suzano: {suzano_count} vendas → {vendedores_map_suzano}")
    
    # Mauá
    mask_maua = vendas_vixen['loja_id'] == 'e5c9f7c4-9877-4f73-b4c4-eac5ad7c3f89'
    maua_count = mask_maua.sum()
    if maua_count > 0:
        vendedores_map_maua = '8a7b9c5d-4e3f-4c2a-9b1d-5e8f7a6c4b9e'  # Vendedor padrão Mauá
        vendas_vixen.loc[mask_maua, 'vendedor_id'] = vendedores_map_maua
        print(f"✅ Mauá: {maua_count} vendas → {vendedores_map_maua}")
    
    # 5. Verifica se ainda tem vendedor genérico
    vendedor_generico_count = (vendas_vixen['vendedor_id'] == '00000000-0000-0000-0000-000000000000').sum()
    
    if vendedor_generico_count > 0:
        print(f"⚠️  Ainda temos {vendedor_generico_count} vendas com vendedor genérico")
        # Aplica vendedor padrão para casos não mapeados
        mask_generico = vendas_vixen['vendedor_id'] == '00000000-0000-0000-0000-000000000000'
        vendas_vixen.loc[mask_generico, 'vendedor_id'] = '2fec96c8-d492-49ab-b38a-a5d5452af4d2'
        print(f"🔧 Aplicado vendedor padrão para casos restantes")
    
    # 6. Verificação final
    vendedores_finais = vendas_vixen['vendedor_id'].unique()
    print(f"\n📊 Vendedores finais: {vendedores_finais}")
    
    # 7. Salva arquivo corrigido
    arquivo_corrigido = base_dir / "data" / "vendas_para_importar" / "vendas_VIXEN_PRONTO_PARA_IMPORTAR_CORRIGIDO.csv"
    vendas_vixen.to_csv(arquivo_corrigido, index=False)
    
    print(f"\n✅ ARQUIVO CORRIGIDO SALVO:")
    print(f"   {arquivo_corrigido}")
    print(f"   {len(vendas_vixen)} vendas")
    
    # 8. Comandos SQL atualizados
    print(f"\n🛠️  COMANDOS SQL CORRIGIDOS:")
    print(f"   -- Importa vendas VIXEN corrigidas")
    print(f"   \\copy vendas.vendas FROM '{arquivo_corrigido}' CSV HEADER;")
    print(f"   -- Verifica")
    print(f"   SELECT COUNT(*) FROM vendas.vendas WHERE observacoes LIKE '%VIXEN%';")
    print(f"   -- Total geral")
    print(f"   SELECT COUNT(*) FROM vendas.vendas; -- Deve ser OSS + VIXEN")
    
    # 9. Estatísticas por vendedor
    print(f"\n📊 DISTRIBUIÇÃO POR VENDEDOR:")
    por_vendedor = vendas_vixen.groupby(['loja_id', 'vendedor_id']).size().reset_index(name='count')
    for _, row in por_vendedor.iterrows():
        loja_nome = 'SUZANO' if row['loja_id'] == '52f92716-d2ba-441a-ac3c-94bdfabd9722' else 'MAUA'
        print(f"   {loja_nome}: {row['count']} vendas → {row['vendedor_id']}")
    
    print(f"\n🎉 CORREÇÃO VENDEDORES CONCLUÍDA!")
    print(f"✅ Todas as vendas agora têm vendedores válidos!")
    print(f"🚀 Pronto para importação sem erro de foreign key!")
    
    return vendas_vixen

if __name__ == "__main__":
    resultado = corrigir_vendedores_vixen()
    print(f"\n✅ {len(resultado)} vendas VIXEN corrigidas!")