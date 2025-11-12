#!/usr/bin/env python3
"""
Análise detalhada dos dados normalizados para vendas
"""

import pandas as pd
import json
from pathlib import Path

def analisar_dados_normalizados():
    print("🔍 ANÁLISE DOS DADOS NORMALIZADOS DISPONÍVEIS")
    print("=" * 70)
    
    # 1. Analisar arquivo de clientes UUID (para cliente_id)
    print("\n📋 1. CLIENTES UUID (para cliente_id)")
    clientes_file = "data/importacao_clientes/modelo_tabela/clientes_uuid_banco_completo.csv"
    
    if Path(clientes_file).exists():
        df_clientes = pd.read_csv(clientes_file)
        print(f"   ✅ Arquivo: {clientes_file}")
        print(f"   📊 Total clientes: {len(df_clientes):,}")
        print(f"   🔑 Colunas principais: {['id', 'id_legado', 'nome', 'cpf']}")
        print(f"   📝 Exemplo id_legado: {df_clientes['id_legado'].iloc[:3].tolist()}")
    else:
        print(f"   ❌ Arquivo não encontrado: {clientes_file}")
    
    # 2. Analisar vendedores UUID (para vendedor_id)
    print("\n📋 2. VENDEDORES UUID (para vendedor_id)")
    vendedores_file = "VENDEDORES_UNICOS_UUID.csv"
    
    if Path(vendedores_file).exists():
        df_vendedores = pd.read_csv(vendedores_file)
        print(f"   ✅ Arquivo: {vendedores_file}")
        print(f"   📊 Total vendedores: {len(df_vendedores):,}")
        print(f"   🔑 Colunas: {list(df_vendedores.columns)}")
        print(f"   📝 Exemplos:")
        for i in range(min(5, len(df_vendedores))):
            row = df_vendedores.iloc[i]
            print(f"      - {row['nome_padronizado']} -> {row['uuid']}")
    else:
        print(f"   ❌ Arquivo não encontrado: {vendedores_file}")
    
    # 3. Analisar OSs com UUIDs (para relação venda->OS->vendedor)
    print("\n📋 3. ORDENS DE SERVIÇO COM UUID (para vendedor_id)")
    oss_dir = Path("data/originais/oss/finais_postgresql_prontos")
    
    if oss_dir.exists():
        oss_files = list(oss_dir.glob("*_postgresql_pronto.csv"))
        print(f"   ✅ Arquivos OSs: {len(oss_files)}")
        
        # Analisar um arquivo de exemplo
        if oss_files:
            exemplo_file = oss_files[0]
            df_os = pd.read_csv(exemplo_file, nrows=3)
            print(f"   📄 Exemplo ({exemplo_file.name}):")
            print(f"   🔑 Colunas relevantes:")
            colunas_relevantes = [col for col in df_os.columns if any(x in col.lower() for x in ['vendedor', 'consultor', 'numero_os', 'os', 'nome'])]
            for col in colunas_relevantes[:10]:
                print(f"      - {col}")
    else:
        print(f"   ❌ Diretório não encontrado: {oss_dir}")
    
    # 4. Analisar estrutura das vendas de caixa
    print("\n📋 4. VENDAS DE CAIXA (origem dos dados)")
    vendas_dir = Path("data/originais/cxs/finais_postgresql_prontos")
    
    if vendas_dir.exists():
        vendas_files = list(vendas_dir.glob("vendas_*_final.csv"))
        print(f"   ✅ Arquivos vendas: {len(vendas_files)}")
        
        if vendas_files:
            exemplo_file = vendas_files[0]
            df_vendas = pd.read_csv(exemplo_file, nrows=3)
            print(f"   📄 Exemplo ({exemplo_file.name}):")
            print(f"   🔑 Colunas: {list(df_vendas.columns)}")
            print(f"   📊 Dados de exemplo:")
            for i, row in df_vendas.iterrows():
                print(f"      Venda {row['nn_venda']}: {row['cliente']} - R$ {row.get('valor_venda', 'N/A')}")
    else:
        print(f"   ❌ Diretório não encontrado: {vendas_dir}")
    
    # 5. Verificar se há relação entre vendas e OSs
    print("\n📋 5. CRUZAMENTO VENDAS <-> ORDENS DE SERVIÇO")
    
    # Tentar encontrar padrões de relação
    if oss_dir.exists() and vendas_dir.exists():
        try:
            # Carregar uma amostra de cada
            os_file = list(oss_dir.glob("SUZANO_postgresql_pronto.csv"))[0]
            venda_file = list(vendas_dir.glob("vendas_suzano_final.csv"))[0]
            
            df_os_sample = pd.read_csv(os_file, nrows=10)
            df_venda_sample = pd.read_csv(venda_file, nrows=10)
            
            print(f"   🔍 Campos OS que podem relacionar com vendas:")
            for col in df_os_sample.columns:
                if any(word in col.lower() for word in ['numero', 'os', 'n°', 'lancaster', 'valor', 'total']):
                    valores = df_os_sample[col].dropna().astype(str).head(3).tolist()
                    print(f"      - {col}: {valores}")
            
            print(f"   🔍 Campos Vendas:")
            for col in df_venda_sample.columns:
                valores = df_venda_sample[col].dropna().astype(str).head(3).tolist()
                print(f"      - {col}: {valores}")
                
        except Exception as e:
            print(f"   ⚠️  Erro ao fazer cruzamento: {e}")
    
    # 6. Estratégia recomendada
    print("\n📋 6. ESTRATÉGIA RECOMENDADA PARA VENDAS")
    print("=" * 70)
    print("✅ CLIENTE_ID:")
    print("   - Usar: data/importacao_clientes/modelo_tabela/clientes_uuid_banco_completo.csv")
    print("   - Cruzar por: nome do cliente (fuzzy match) ou id_legado se disponível")
    print("   - Campo resultado: 'id' -> vendas.cliente_id")
    
    print("\n✅ VENDEDOR_ID:")
    print("   - Opção 1: Usar OSs com vendedor_uuid (mais preciso)")
    print("   - Opção 2: Usar VENDEDORES_UNICOS_UUID.csv (mapeamento manual)")
    print("   - Cruzar por: nome do consultor/vendedor")
    print("   - Campo resultado: 'uuid' -> vendas.vendedor_id")
    
    print("\n✅ TIPO_OPERACAO:")
    print("   - 'GARANTIA' se forma_de_pgto = 'GARANTIA'")
    print("   - 'VENDA' para todos os outros casos")
    print("   - Verificar campo 'VENDA' nas OSs (SIM/NÃO)")
    
    print("\n🔄 PRÓXIMOS PASSOS:")
    print("1. Criar script de cruzamento cliente por nome (fuzzy)")
    print("2. Criar mapeamento vendedor usando OSs como referência")
    print("3. Gerar vendas finais com todos os UUIDs corretos")
    print("4. Validar constraints da tabela vendas.vendas")

if __name__ == "__main__":
    analisar_dados_normalizados()