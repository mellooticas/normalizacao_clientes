#!/usr/bin/env python3
"""
Aplicar UUIDs de Canais de Aquisição VIXEN
==========================================

Aplica os UUIDs dos canais de aquisição nos arquivos finais VIXEN.
"""

import pandas as pd
import json
from pathlib import Path

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    vixen_dir = base_dir / "data" / "originais" / "vixen"
    vixen_finais_dir = vixen_dir / "finais_postgresql_prontos"
    
    print("📞 APLICANDO UUIDs DE CANAIS DE AQUISIÇÃO VIXEN")
    print("=" * 60)
    
    # Carregar mapeamento de canais
    mapeamento_file = vixen_dir / "mapeamento_canais_vixen.json"
    
    if not mapeamento_file.exists():
        print(f"❌ Mapeamento não encontrado: {mapeamento_file}")
        return
    
    with open(mapeamento_file, 'r', encoding='utf-8') as f:
        mapeamento_canais = json.load(f)
    
    print(f"📊 Mapeamento carregado: {len(mapeamento_canais)} canais")
    
    # Arquivos para processar
    arquivos_vixen = [
        'clientes_maua_final.csv',
        'clientes_suzano_final.csv'
    ]
    
    total_processados = 0
    canais_aplicados = 0
    
    for arquivo_nome in arquivos_vixen:
        arquivo_path = vixen_finais_dir / arquivo_nome
        
        if arquivo_path.exists():
            loja = arquivo_nome.replace('clientes_', '').replace('_final.csv', '').upper()
            
            print(f"\n🏪 Processando {loja}:")
            print(f"   📄 Arquivo: {arquivo_nome}")
            
            # Carregar dados
            df = pd.read_csv(arquivo_path)
            registros_antes = len(df)
            print(f"   📊 Registros: {registros_antes:,}")
            
            # Aplicar UUIDs de canais
            if 'Como nos conheceu' in df.columns:
                # Inicializar novas colunas
                df['canal_uuid'] = None
                df['canal_codigo'] = None
                df['canal_categoria'] = None
                df['canal_nome'] = None
                
                canais_encontrados = 0
                canais_nao_encontrados = 0
                
                for index, row in df.iterrows():
                    canal_original = row['Como nos conheceu']
                    
                    if canal_original in mapeamento_canais:
                        canal_info = mapeamento_canais[canal_original]
                        
                        df.at[index, 'canal_uuid'] = canal_info['canal_uuid']
                        df.at[index, 'canal_codigo'] = canal_info['canal_codigo']
                        df.at[index, 'canal_categoria'] = canal_info['canal_categoria']
                        df.at[index, 'canal_nome'] = canal_original
                        
                        canais_encontrados += 1
                    else:
                        # Canal não encontrado - usar padrão
                        df.at[index, 'canal_uuid'] = None
                        df.at[index, 'canal_codigo'] = 'NAO_MAPEADO'
                        df.at[index, 'canal_categoria'] = 'OUTROS'
                        df.at[index, 'canal_nome'] = canal_original
                        
                        canais_nao_encontrados += 1
                
                print(f"   ✅ Canais mapeados: {canais_encontrados:,}")
                print(f"   ⚠️  Canais não mapeados: {canais_nao_encontrados:,}")
                
                canais_aplicados += canais_encontrados
                
                # Adicionar metadados
                df['data_normalizacao_canais'] = pd.Timestamp.now()
                df['etapa_processamento'] = 'NORMALIZADO_CANAIS'
                
                # Salvar arquivo atualizado
                df.to_csv(arquivo_path, index=False)
                
                print(f"   📊 Colunas após: {len(df.columns)}")
                print(f"   ✅ Arquivo atualizado!")
                
                total_processados += len(df)
                
            else:
                print(f"   ❌ Coluna 'Como nos conheceu' não encontrada!")
        else:
            print(f"❌ Arquivo não encontrado: {arquivo_nome}")
    
    print(f"\n🎯 RESUMO DA APLICAÇÃO DE CANAIS:")
    print(f"   📁 Arquivos processados: {len([a for a in arquivos_vixen if (vixen_finais_dir / a).exists()])}")
    print(f"   📊 Total de registros: {total_processados:,}")
    print(f"   📞 Canais aplicados: {canais_aplicados:,}")
    
    # Verificar resultado
    print(f"\n📋 VERIFICAÇÃO FINAL:")
    
    for arquivo_nome in arquivos_vixen:
        arquivo_path = vixen_finais_dir / arquivo_nome
        
        if arquivo_path.exists():
            try:
                df_check = pd.read_csv(arquivo_path)
                loja = arquivo_nome.replace('clientes_', '').replace('_final.csv', '').upper()
                
                print(f"   ✅ {loja}: {len(df_check):,} registros")
                
                # Verificar colunas de canais
                colunas_canais = ['canal_uuid', 'canal_codigo', 'canal_categoria', 'canal_nome']
                for col in colunas_canais:
                    if col in df_check.columns:
                        valores_nao_nulos = df_check[col].notna().sum()
                        print(f"      🔹 {col}: {valores_nao_nulos:,} preenchidos")
                    else:
                        print(f"      🔹 {col}: ❌ não encontrada")
                
                # Resumo de categorias
                if 'canal_categoria' in df_check.columns:
                    categorias = df_check['canal_categoria'].value_counts()
                    print(f"      📊 Categorias:")
                    for categoria, count in categorias.head(5).items():
                        print(f"         • {categoria}: {count:,}")
                        
            except Exception as e:
                print(f"   ❌ Erro ao verificar {arquivo_nome}: {e}")
    
    print(f"\n🚀 CANAIS NORMALIZADOS COM SUCESSO!")
    print(f"   📞 UUIDs aplicados nos arquivos VIXEN")
    print(f"   🗃️  Estrutura compatível com marketing.canais_aquisicao")
    print(f"   👥 Próximo: Normalizar vendedores")

if __name__ == "__main__":
    main()