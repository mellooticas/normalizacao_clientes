#!/usr/bin/env python3
"""
Verifica e remove duplicatas do arquivo de vendas
"""

import pandas as pd
from pathlib import Path

def verificar_e_limpar_duplicatas():
    """Verifica duplicatas no arquivo de importação"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("🔍 === VERIFICANDO DUPLICATAS NO ARQUIVO ===")
    
    # Carrega arquivo de importação
    arquivo_importar = base_dir / "data" / "vendas_para_importar" / "vendas_PRONTO_PARA_IMPORTAR_97pct.csv"
    vendas_df = pd.read_csv(arquivo_importar)
    
    print(f"📊 Total registros no arquivo: {len(vendas_df)}")
    
    # 1. Verifica duplicatas por loja_id + numero_venda
    print(f"\n=== VERIFICAÇÃO DUPLICATAS ===")
    
    # Identifica duplicatas
    duplicatas_mask = vendas_df.duplicated(subset=['loja_id', 'numero_venda'], keep=False)
    duplicatas_df = vendas_df[duplicatas_mask].copy()
    
    if len(duplicatas_df) > 0:
        print(f"🚨 DUPLICATAS ENCONTRADAS: {len(duplicatas_df)} registros")
        
        # Agrupa duplicatas
        duplicatas_agrupadas = duplicatas_df.groupby(['loja_id', 'numero_venda']).size().reset_index(name='count')
        print(f"📊 Pares (loja_id, numero_venda) duplicados: {len(duplicatas_agrupadas)}")
        
        # Mostra exemplos
        print(f"\n🔍 EXEMPLOS DE DUPLICATAS:")
        for i, (_, row) in enumerate(duplicatas_agrupadas.head(10).iterrows()):
            print(f"  {i+1}. Loja: {row['loja_id'][:8]}..., Número: {row['numero_venda']}, Repetições: {row['count']}")
        
        # Mostra detalhes de uma duplicata específica
        primeira_duplicata = duplicatas_agrupadas.iloc[0]
        exemplo_duplicatas = vendas_df[
            (vendas_df['loja_id'] == primeira_duplicata['loja_id']) & 
            (vendas_df['numero_venda'] == primeira_duplicata['numero_venda'])
        ]
        
        print(f"\n📋 DETALHES DA PRIMEIRA DUPLICATA:")
        print(f"   Loja: {primeira_duplicata['loja_id']}")
        print(f"   Número venda: {primeira_duplicata['numero_venda']}")
        print(f"   Registros encontrados: {len(exemplo_duplicatas)}")
        
        for i, (_, row) in enumerate(exemplo_duplicatas.iterrows()):
            print(f"   Registro {i+1}:")
            print(f"     Cliente ID: {row['cliente_id']}")
            print(f"     Data: {row['data_venda']}")
            print(f"     Valor: {row['valor_total']}")
            print(f"     Nome: {row['nome_cliente_temp']}")
        
        # 2. ESTRATÉGIA DE LIMPEZA
        print(f"\n🧹 === LIMPEZA DE DUPLICATAS ===")
        
        # Mantém apenas o primeiro registro de cada duplicata
        vendas_limpo = vendas_df.drop_duplicates(subset=['loja_id', 'numero_venda'], keep='first')
        
        registros_removidos = len(vendas_df) - len(vendas_limpo)
        print(f"📊 Registros removidos: {registros_removidos}")
        print(f"📊 Registros restantes: {len(vendas_limpo)}")
        
        # 3. SALVA ARQUIVO LIMPO
        arquivo_limpo = base_dir / "data" / "vendas_para_importar" / "vendas_PRONTO_PARA_IMPORTAR_97pct_LIMPO.csv"
        vendas_limpo.to_csv(arquivo_limpo, index=False)
        
        print(f"\n✅ ARQUIVO LIMPO SALVO:")
        print(f"   Arquivo: {arquivo_limpo}")
        print(f"   Registros: {len(vendas_limpo)}")
        
        # 4. VERIFICA SE AINDA TEM DUPLICATAS
        duplicatas_pos_limpeza = vendas_limpo.duplicated(subset=['loja_id', 'numero_venda']).sum()
        
        if duplicatas_pos_limpeza == 0:
            print(f"✅ SEM DUPLICATAS: Arquivo limpo pronto para importação!")
        else:
            print(f"🚨 AINDA TEM {duplicatas_pos_limpeza} DUPLICATAS!")
        
        # 5. NOVOS COMANDOS SQL
        print(f"\n🛠️  NOVOS COMANDOS PARA IMPORTAÇÃO:")
        print(f"   1. TRUNCATE TABLE vendas.vendas;")
        print(f"   2. \\copy vendas.vendas FROM '{arquivo_limpo}' CSV HEADER;")
        print(f"   3. SELECT COUNT(*) FROM vendas.vendas; -- Deve retornar {len(vendas_limpo)}")
        
        return vendas_limpo
        
    else:
        print(f"✅ NENHUMA DUPLICATA ENCONTRADA!")
        print(f"📄 O arquivo está pronto para importação.")
        return vendas_df

if __name__ == "__main__":
    resultado = verificar_e_limpar_duplicatas()
    print(f"\n✅ Verificação concluída! {len(resultado)} registros finais.")