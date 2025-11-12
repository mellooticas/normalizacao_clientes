#!/usr/bin/env python3
"""
Script de emergência para resolver foreign key de vendedores
Cria solução temporária enquanto não temos vendedores reais do banco
"""

import pandas as pd
import uuid
from pathlib import Path
from datetime import datetime

def resolver_vendedores_emergencia():
    """Resolve problema de vendedores usando estratégia de emergência"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("=== RESOLUÇÃO EMERGENCIAL DE VENDEDORES ===")
    
    # 1. Carrega dados de vendas
    print("\n1. CARREGANDO DADOS DE VENDAS:")
    arquivo_vendas = base_dir / "data" / "vendas_para_importar" / "vendas_final_corrigido.csv"
    df = pd.read_csv(arquivo_vendas)
    print(f"Registros carregados: {len(df)}")
    
    # 2. Estratégias possíveis
    print("\n2. ESTRATÉGIAS DISPONÍVEIS:")
    print("A) Usar vendedor genérico único para todas as vendas")
    print("B) Usar NULL em vendedor_id (se o campo permitir NULL)")
    print("C) Aguardar consulta dos vendedores reais do banco")
    
    # 3. Implementa estratégia A - vendedor genérico
    print("\n3. IMPLEMENTANDO ESTRATÉGIA A - VENDEDOR GENÉRICO:")
    
    # Gera UUID fixo para vendedor genérico
    vendedor_generico_uuid = "00000000-0000-0000-0000-000000000001"
    
    print(f"UUID vendedor genérico: {vendedor_generico_uuid}")
    print("Nome sugerido: 'SISTEMA - IMPORTAÇÃO AUTOMÁTICA'")
    
    # 4. Aplica vendedor genérico
    df['vendedor_id'] = vendedor_generico_uuid
    
    # 5. Estatísticas
    print(f"\n=== ESTATÍSTICAS ===")
    print(f"Total de vendas: {len(df)}")
    print(f"Vendedor único aplicado: {vendedor_generico_uuid}")
    print(f"Valor total: R$ {df['valor_total'].sum():,.2f}")
    
    # 6. Salva versão com vendedor genérico
    arquivo_emergencia = base_dir / "data" / "vendas_para_importar" / "vendas_vendedor_generico.csv"
    df.to_csv(arquivo_emergencia, index=False)
    
    print(f"\n=== ARQUIVO GERADO ===")
    print(f"Arquivo: {arquivo_emergencia}")
    print(f"✅ Vendedor genérico aplicado a todas as vendas")
    print(f"⚠️  ATENÇÃO: Você precisará criar este vendedor no banco antes da importação!")
    
    # 7. SQL para criar vendedor genérico
    print(f"\n=== SQL PARA CRIAR VENDEDOR GENÉRICO ===")
    sql_create_vendedor = f"""
-- Execute este comando ANTES da importação das vendas
INSERT INTO vendas.vendedores (
    id, 
    nome, 
    codigo_vendedor, 
    ativo, 
    created_at, 
    updated_at
) VALUES (
    '{vendedor_generico_uuid}',
    'SISTEMA - IMPORTAÇÃO AUTOMÁTICA',
    'SYS001',
    true,
    NOW(),
    NOW()
) ON CONFLICT (id) DO NOTHING;
"""
    
    print(sql_create_vendedor)
    
    # Salva SQL em arquivo
    with open(base_dir / "criar_vendedor_generico.sql", 'w') as f:
        f.write(sql_create_vendedor)
    
    print(f"\n=== INSTRUÇÕES ===")
    print("1. Execute o SQL acima para criar o vendedor genérico")
    print("2. Faça TRUNCATE da tabela vendas")
    print("3. Importe o arquivo vendas_vendedor_generico.csv")
    print("4. Posteriormente, atualize os vendedores corretos quando tiver os dados reais")
    
    return df

if __name__ == "__main__":
    resultado = resolver_vendedores_emergencia()
    print("\n🚨 SOLUÇÃO TEMPORÁRIA APLICADA!")
    print("⚠️  Lembre-se de criar o vendedor genérico no banco primeiro!")