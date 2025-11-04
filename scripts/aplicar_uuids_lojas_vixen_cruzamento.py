#!/usr/bin/env python3
"""
Aplicar UUIDs de Lojas - VIXEN Cruzamento
=========================================

Aplica UUIDs das lojas MAUA e SUZANO nos arquivos VIXEN do cruzamento.
"""

import pandas as pd
from pathlib import Path

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    cruzamento_dir = base_dir / "data" / "originais" / "cruzamento_vixen_oss"
    
    print("🔗 APLICANDO UUIDs DE LOJAS - VIXEN CRUZAMENTO")
    print("=" * 60)
    
    # UUIDs das lojas (mesmos usados em CXS e OSS)
    uuids_lojas = {
        'MAUA': '7f9d4c6e-8b3a-4d2c-9f1e-6a5b8c7d9e0f',
        'SUZANO': '52f92716-d2ba-441a-ac3c-94bdfabd9722'
    }
    
    # Arquivos para processar
    arquivos_vixen = [
        ('clientes_vixen_maua_original.csv', 'MAUA'),
        ('clientes_vixen_suzano_original.csv', 'SUZANO')
    ]
    
    total_processados = 0
    
    for arquivo_nome, loja in arquivos_vixen:
        arquivo_path = cruzamento_dir / arquivo_nome
        
        if arquivo_path.exists():
            print(f"\n🏪 Processando {loja}:")
            print(f"   📄 Arquivo: {arquivo_nome}")
            
            # Carregar dados
            df = pd.read_csv(arquivo_path)
            registros_antes = len(df)
            print(f"   📊 Registros: {registros_antes:,}")
            
            # Aplicar UUID da loja
            loja_uuid = uuids_lojas[loja]
            
            # Verificar se já tem a coluna
            if 'loja_uuid' not in df.columns:
                df['loja_uuid'] = loja_uuid
                print(f"   ✅ Adicionada coluna loja_uuid")
            else:
                df['loja_uuid'] = loja_uuid  # Atualizar se já existir
                print(f"   🔄 Atualizada coluna loja_uuid")
            
            # Verificar/atualizar outras colunas de loja
            if 'loja_id' in df.columns:
                # Mapear loja_id correto
                loja_ids = {'MAUA': 48, 'SUZANO': 42}  # Baseado na análise anterior
                df['loja_id'] = loja_ids[loja]
                print(f"   🔄 Atualizada loja_id: {loja_ids[loja]}")
            
            if 'loja_nome' in df.columns:
                df['loja_nome'] = loja
                print(f"   🔄 Atualizada loja_nome: {loja}")
            
            # Adicionar metadados de processamento
            df['data_processamento_uuid'] = pd.Timestamp.now()
            df['origem_dados'] = 'VIXEN_CRUZAMENTO'
            
            # Salvar arquivo atualizado
            df.to_csv(arquivo_path, index=False)
            registros_depois = len(df)
            
            print(f"   📊 UUID aplicado: {loja_uuid}")
            print(f"   📊 Registros após: {registros_depois:,}")
            print(f"   ✅ Arquivo atualizado!")
            
            total_processados += registros_depois
            
        else:
            print(f"❌ Arquivo não encontrado: {arquivo_nome}")
    
    print(f"\n🎯 RESUMO DA APLICAÇÃO DE UUIDs:")
    print(f"   📁 Arquivos processados: {len(arquivos_vixen)}")
    print(f"   📊 Total de registros: {total_processados:,}")
    print(f"   🔗 UUIDs aplicados:")
    
    for loja, uuid in uuids_lojas.items():
        print(f"      🏪 {loja}: {uuid}")
    
    # Verificar estrutura final
    print(f"\n📋 ESTRUTURA FINAL COM UUIDs:")
    
    for arquivo_nome, loja in arquivos_vixen:
        arquivo_path = cruzamento_dir / arquivo_nome
        
        if arquivo_path.exists():
            try:
                df_check = pd.read_csv(arquivo_path)
                
                # Verificar colunas de loja
                colunas_loja = []
                for col in ['loja_uuid', 'loja_id', 'loja_nome']:
                    if col in df_check.columns:
                        valor_exemplo = df_check[col].iloc[0] if len(df_check) > 0 else "N/A"
                        colunas_loja.append(f"{col}={valor_exemplo}")
                
                print(f"   ✅ {loja}: {len(df_check):,} registros")
                print(f"      🔹 {' | '.join(colunas_loja)}")
                
            except Exception as e:
                print(f"   ❌ Erro ao verificar {arquivo_nome}: {e}")
    
    print(f"\n🚀 UUIDs DE LOJAS APLICADOS COM SUCESSO!")
    print(f"   🔗 Arquivos prontos para próxima etapa do cruzamento")
    print(f"   📂 Localização: {cruzamento_dir}")

if __name__ == "__main__":
    main()