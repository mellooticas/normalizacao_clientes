#!/usr/bin/env python3
"""
Normalizar VIXEN - Aplicar UUIDs de Lojas
==========================================

Aplica UUIDs de lojas nos arquivos finais do VIXEN (finais_postgresql_prontos).
"""

import pandas as pd
from pathlib import Path

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    vixen_finais_dir = base_dir / "data" / "originais" / "vixen" / "finais_postgresql_prontos"
    
    print("🔗 NORMALIZANDO VIXEN - APLICANDO UUIDs DE LOJAS")
    print("=" * 60)
    
    # UUIDs das lojas (mesmos usados em CXS e OSS)
    uuids_lojas = {
        'maua': {
            'loja_id': 48,
            'loja_nome': 'MAUA',
            'loja_uuid': '7f9d4c6e-8b3a-4d2c-9f1e-6a5b8c7d9e0f'
        },
        'suzano': {
            'loja_id': 42,
            'loja_nome': 'SUZANO', 
            'loja_uuid': '52f92716-d2ba-441a-ac3c-94bdfabd9722'
        }
    }
    
    # Arquivos para processar
    arquivos_vixen = [
        'clientes_maua_final.csv',
        'clientes_suzano_final.csv'
    ]
    
    total_processados = 0
    
    for arquivo_nome in arquivos_vixen:
        arquivo_path = vixen_finais_dir / arquivo_nome
        
        if arquivo_path.exists():
            # Extrair loja do nome do arquivo
            loja_key = arquivo_nome.replace('clientes_', '').replace('_final.csv', '')
            
            if loja_key in uuids_lojas:
                loja_info = uuids_lojas[loja_key]
                
                print(f"\n🏪 Processando {loja_info['loja_nome']}:")
                print(f"   📄 Arquivo: {arquivo_nome}")
                
                # Carregar dados
                df = pd.read_csv(arquivo_path)
                registros_antes = len(df)
                print(f"   📊 Registros: {registros_antes:,}")
                print(f"   📊 Colunas antes: {len(df.columns)}")
                
                # Aplicar UUIDs e informações da loja
                df['loja_uuid'] = loja_info['loja_uuid']
                
                # Atualizar/verificar loja_id e loja_nome se existirem
                if 'loja_id' in df.columns:
                    df['loja_id'] = loja_info['loja_id']
                else:
                    df['loja_id'] = loja_info['loja_id']
                
                if 'loja_nome' in df.columns:
                    df['loja_nome'] = loja_info['loja_nome']
                else:
                    df['loja_nome'] = loja_info['loja_nome']
                
                # Adicionar metadados
                df['data_normalizacao'] = pd.Timestamp.now()
                df['etapa_processamento'] = 'NORMALIZADO_UUIDS_LOJAS'
                
                print(f"   ✅ UUID aplicado: {loja_info['loja_uuid']}")
                print(f"   ✅ Loja ID: {loja_info['loja_id']}")
                print(f"   ✅ Loja Nome: {loja_info['loja_nome']}")
                
                # Mostrar estrutura de colunas
                print(f"   📊 Colunas após: {len(df.columns)}")
                
                # Salvar arquivo atualizado
                df.to_csv(arquivo_path, index=False)
                
                total_processados += len(df)
                print(f"   ✅ Arquivo normalizado!")
                
            else:
                print(f"⚠️  Loja não mapeada: {loja_key}")
        else:
            print(f"❌ Arquivo não encontrado: {arquivo_nome}")
    
    print(f"\n🎯 RESUMO DA NORMALIZAÇÃO:")
    print(f"   📁 Arquivos processados: {len([a for a in arquivos_vixen if (vixen_finais_dir / a).exists()])}")
    print(f"   📊 Total de registros: {total_processados:,}")
    
    print(f"\n🔗 UUIDs DE LOJAS APLICADOS:")
    for loja_key, info in uuids_lojas.items():
        print(f"   🏪 {info['loja_nome']}: {info['loja_uuid']}")
    
    # Verificar estrutura final
    print(f"\n📋 VERIFICAÇÃO FINAL:")
    
    for arquivo_nome in arquivos_vixen:
        arquivo_path = vixen_finais_dir / arquivo_nome
        
        if arquivo_path.exists():
            try:
                df_check = pd.read_csv(arquivo_path)
                loja = arquivo_nome.replace('clientes_', '').replace('_final.csv', '').upper()
                
                print(f"   ✅ {loja}: {len(df_check):,} registros")
                
                # Verificar se tem as colunas necessárias
                colunas_necessarias = ['loja_uuid', 'loja_id', 'loja_nome']
                for col in colunas_necessarias:
                    if col in df_check.columns:
                        print(f"      🔹 {col}: ✓")
                    else:
                        print(f"      🔹 {col}: ❌")
                        
            except Exception as e:
                print(f"   ❌ Erro ao verificar {arquivo_nome}: {e}")
    
    print(f"\n🚀 PRÓXIMO PASSO:")
    print(f"   📞 Normalizar canais de aquisição ('Como nos conheceu')")
    print(f"   👥 Normalizar vendedores")
    print(f"   🔗 Criar estrutura para cruzamentos")

if __name__ == "__main__":
    main()