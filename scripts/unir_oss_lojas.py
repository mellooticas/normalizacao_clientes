#!/usr/bin/env python3
"""
Unir dados de OSS com dados de lojas usando os_chave
"""

import pandas as pd
from pathlib import Path

def carregar_arquivos_oss():
    """Carrega arquivos oss_*.csv com cliente_id"""
    print("📊 CARREGANDO ARQUIVOS OSS (cliente_id)")
    print("=" * 45)
    
    oss_path = Path("data/originais/oss/finais_postgresql_prontos")
    oss_dados = []
    
    for arquivo in oss_path.glob("oss_*.csv"):
        print(f"📥 {arquivo.name}")
        df = pd.read_csv(arquivo)
        
        # Verificar colunas principais
        tem_os_chave = 'os_chave' in df.columns
        tem_cliente_id = 'cliente_id' in df.columns
        
        print(f"   Registros: {len(df):,}")
        print(f"   os_chave: {'✅' if tem_os_chave else '❌'}")
        print(f"   cliente_id: {'✅' if tem_cliente_id else '❌'}")
        
        if tem_os_chave and tem_cliente_id:
            # Adicionar identificador da loja
            loja_nome = arquivo.name.replace("oss_", "").replace("_clientes_ids.csv", "")
            df['loja_origem'] = loja_nome
            oss_dados.append(df)
        else:
            print(f"   ⚠️ Colunas necessárias não encontradas")
    
    if oss_dados:
        oss_final = pd.concat(oss_dados, ignore_index=True)
        print(f"\n✅ Total OSS: {len(oss_final):,}")
        return oss_final
    else:
        return None

def carregar_arquivos_lojas():
    """Carrega arquivos LOJA_*.csv com UUIDs"""
    print("\n📊 CARREGANDO ARQUIVOS LOJAS (UUIDs)")
    print("=" * 40)
    
    oss_path = Path("data/originais/oss/finais_postgresql_prontos")
    lojas_dados = []
    
    # Padrões de nomes de lojas
    padroes_lojas = ["MAUA_", "PERUS_", "RIO_PEQUENO_", "SAO_MATEUS_", "SUZANO_", "SUZANO2_"]
    
    for padrao in padroes_lojas:
        for arquivo in oss_path.glob(f"{padrao}*.csv"):
            print(f"📥 {arquivo.name}")
            df = pd.read_csv(arquivo)
            
            # Verificar colunas principais
            tem_os_chave = 'os_chave' in df.columns
            
            # Procurar colunas com OS
            colunas_os = [col for col in df.columns if 'os' in col.lower()]
            print(f"   Colunas com 'os': {colunas_os}")
            
            if not tem_os_chave and colunas_os:
                # Tentar usar primeira coluna com OS
                coluna_os = colunas_os[0]
                df = df.rename(columns={coluna_os: 'os_chave'})
                tem_os_chave = True
                print(f"   🔄 Usando '{coluna_os}' como os_chave")
            
            # Verificar UUIDs
            tem_loja_uuid = any('loja' in col.lower() and 'uuid' in col.lower() for col in df.columns)
            tem_vendedor_uuid = any('vendedor' in col.lower() and 'uuid' in col.lower() for col in df.columns)
            
            print(f"   Registros: {len(df):,}")
            print(f"   os_chave: {'✅' if tem_os_chave else '❌'}")
            print(f"   loja_uuid: {'✅' if tem_loja_uuid else '❌'}")
            print(f"   vendedor_uuid: {'✅' if tem_vendedor_uuid else '❌'}")
            
            if tem_os_chave:
                # Adicionar identificador da loja
                loja_nome = arquivo.name.split("_")[0].lower()
                df['loja_origem'] = loja_nome
                lojas_dados.append(df)
            else:
                print(f"   ⚠️ Coluna os_chave não encontrada")
    
    if lojas_dados:
        lojas_final = pd.concat(lojas_dados, ignore_index=True)
        print(f"\n✅ Total LOJAS: {len(lojas_final):,}")
        return lojas_final
    else:
        return None

def unir_oss_com_lojas(oss_df, lojas_df):
    """Une dados OSS com dados de lojas via os_chave"""
    print("\n🔗 UNINDO OSS COM LOJAS VIA os_chave")
    print("=" * 40)
    
    # Verificar dados antes da união
    print(f"OSS registros: {len(oss_df):,}")
    print(f"Lojas registros: {len(lojas_df):,}")
    
    # Verificar os_chave válidos
    oss_chaves_validas = oss_df['os_chave'].notna().sum()
    lojas_chaves_validas = lojas_df['os_chave'].notna().sum()
    
    print(f"OSS os_chave válidas: {oss_chaves_validas:,}")
    print(f"Lojas os_chave válidas: {lojas_chaves_validas:,}")
    
    # Preparar dados para merge
    oss_prep = oss_df.dropna(subset=['os_chave'])
    lojas_prep = lojas_df.dropna(subset=['os_chave'])
    
    # Fazer a união
    resultado = pd.merge(
        oss_prep,
        lojas_prep,
        on='os_chave',
        how='inner',
        suffixes=('_oss', '_loja')
    )
    
    print(f"✅ União bem-sucedida: {len(resultado):,} registros")
    
    if len(resultado) > 0:
        # Verificar colunas resultantes
        print("\n📋 Colunas principais no resultado:")
        colunas_importantes = [col for col in resultado.columns if any(palavra in col.lower() 
                             for palavra in ['cliente_id', 'loja_uuid', 'vendedor_uuid', 'canal', 'os_chave', 'total'])]
        print(f"   {colunas_importantes}")
        
        # Estatísticas
        cliente_ids = resultado['cliente_id'].notna().sum()
        print(f"\n📊 Registros com cliente_id: {cliente_ids:,}")
        
        # Verificar se há colunas de valor
        colunas_valor = [col for col in resultado.columns if 'total' in col.lower() or 'valor' in col.lower()]
        if colunas_valor:
            print(f"📊 Colunas de valor encontradas: {colunas_valor}")
    
    return resultado

def processar_vendas_final(vendas_unidas_df):
    """Processa dados unidos para formato de vendas"""
    print("\n🔄 PROCESSANDO VENDAS FINAIS")
    print("=" * 35)
    
    # Colunas necessárias para vendas
    colunas_vendas = []
    
    # Identificar colunas principais
    mapeamento_colunas = {
        'os_chave': 'numero_os',
        'cliente_id': 'cliente_id',
        'data_compra': 'data_venda'
    }
    
    # Procurar UUIDs
    for col in vendas_unidas_df.columns:
        if 'loja' in col.lower() and 'uuid' in col.lower():
            mapeamento_colunas['loja_uuid'] = col
        elif 'vendedor' in col.lower() and 'uuid' in col.lower():
            mapeamento_colunas['vendedor_uuid'] = col
        elif 'canal' in col.lower() and 'uuid' in col.lower():
            mapeamento_colunas['canal_uuid'] = col
        elif 'total' in col.lower() and col.lower() != 'total_os':
            mapeamento_colunas['valor_total'] = col
    
    print("📋 Mapeamento de colunas:")
    for destino, origem in mapeamento_colunas.items():
        print(f"   {destino} ← {origem}")
    
    # Criar DataFrame de vendas
    vendas_final = vendas_unidas_df.copy()
    
    # Renomear colunas
    vendas_final = vendas_final.rename(columns={v: k for k, v in mapeamento_colunas.items()})
    
    print(f"\n✅ Vendas processadas: {len(vendas_final):,}")
    
    # Estatísticas finais
    stats = {
        'Total vendas': len(vendas_final),
        'Com cliente_id': vendas_final.get('cliente_id', pd.Series()).notna().sum(),
        'Com loja_uuid': vendas_final.get('loja_uuid', pd.Series()).notna().sum(),
        'Com vendedor_uuid': vendas_final.get('vendedor_uuid', pd.Series()).notna().sum()
    }
    
    print("\n📊 ESTATÍSTICAS FINAIS:")
    for chave, valor in stats.items():
        print(f"   {chave}: {valor:,}")
    
    return vendas_final

def main():
    print("🚀 UNIÃO OSS + LOJAS = VENDAS COMPLETAS")
    print("=" * 50)
    
    # 1. Carregar dados OSS
    oss_df = carregar_arquivos_oss()
    if oss_df is None:
        print("❌ Falha ao carregar dados OSS")
        return
    
    # 2. Carregar dados das lojas
    lojas_df = carregar_arquivos_lojas()
    if lojas_df is None:
        print("❌ Falha ao carregar dados das lojas")
        return
    
    # 3. Unir dados
    vendas_unidas = unir_oss_com_lojas(oss_df, lojas_df)
    if vendas_unidas is None or len(vendas_unidas) == 0:
        print("❌ Falha na união dos dados")
        return
    
    # 4. Processar vendas finais
    vendas_final = processar_vendas_final(vendas_unidas)
    
    # 5. Salvar resultado
    output_path = Path("data/vendas_para_importar/vendas_oss_lojas_unidas.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    vendas_final.to_csv(output_path, index=False)
    
    print(f"\n💾 ARQUIVO SALVO: {output_path}")
    print(f"📊 Total de vendas: {len(vendas_final):,}")
    
    if 'valor_total' in vendas_final.columns:
        valor_total = pd.to_numeric(vendas_final['valor_total'], errors='coerce').sum()
        print(f"💰 Valor total: R$ {valor_total:,.2f}")
    
    print("\n🎯 PRÓXIMO PASSO: Mapear cliente_uuid")

if __name__ == "__main__":
    main()