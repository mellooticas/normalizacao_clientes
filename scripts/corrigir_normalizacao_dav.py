#!/usr/bin/env python3
"""
Script para finalizar normalização DAV - substituir coluna Nro.DAV pelos valores limpos
Aplicar a mesma lógica que usamos para lista_dav
"""

import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def finalizar_normalizacao_dav():
    """
    Substitui coluna Nro.DAV pelos valores normalizados
    """
    print("🎯 === FINALIZANDO NORMALIZAÇÃO DAV PRODUTOS === 🎯")
    
    arquivo = 'data/originais/controles_gerais/conf_dav/csv/conf_dav_normalizado_20251105_040621.csv'
    
    try:
        print(f"📄 Carregando: {arquivo}")
        df = pd.read_csv(arquivo)
        
        print(f"📊 Registros: {len(df):,}")
        print(f"📋 Colunas: {df.shape[1]}")
        
        # Verificar situação atual
        print(f"\n🔍 === ANÁLISE ATUAL === 🔍")
        
        if 'Nro.DAV' in df.columns:
            dav_originais = df['Nro.DAV'].notna().sum()
            dav_sample = df['Nro.DAV'].dropna().astype(str).head(5).tolist()
            print(f"📋 Nro.DAV originais: {dav_originais:,}")
            print(f"🔍 Amostra originais: {', '.join(dav_sample)}")
        
        if 'dav_normalizado' in df.columns:
            dav_normalizados = df['dav_normalizado'].notna().sum()
            norm_sample = df['dav_normalizado'].dropna().astype(str).head(5).tolist()
            print(f"📋 DAVs normalizados: {dav_normalizados:,}")
            print(f"🔍 Amostra normalizados: {', '.join(norm_sample)}")
        
        # APLICAR NORMALIZAÇÃO: substituir Nro.DAV
        print(f"\n🔧 === APLICANDO NORMALIZAÇÃO === 🔧")
        
        # Backup da coluna original
        df['Nro_DAV_Original'] = df['Nro.DAV'].copy()
        
        # Substituir pela versão normalizada
        if 'dav_normalizado' in df.columns:
            # Usar dav_normalizado quando disponível
            mask_normalizado = df['dav_normalizado'].notna()
            df.loc[mask_normalizado, 'Nro.DAV'] = df.loc[mask_normalizado, 'dav_normalizado']
            
            substituicoes = mask_normalizado.sum()
            print(f"✅ Substituições realizadas: {substituicoes:,}")
        
        # Verificar resultado
        print(f"\n✅ === RESULTADO === ✅")
        
        dav_finais = df['Nro.DAV'].notna().sum()
        final_sample = df['Nro.DAV'].dropna().astype(str).head(5).tolist()
        
        print(f"📋 Nro.DAV finais: {dav_finais:,}")
        print(f"🔍 Amostra finais: {', '.join(final_sample)}")
        
        # Verificar se ainda há prefixos
        df_sample = df['Nro.DAV'].dropna().astype(str)
        prefixos_42 = df_sample.str.startswith('42').sum()
        prefixos_48 = df_sample.str.startswith('48').sum()
        
        print(f"🔍 Prefixos restantes:")
        print(f"   42xxxx: {prefixos_42:,}")
        print(f"   48xxxx: {prefixos_48:,}")
        
        if prefixos_42 == 0 and prefixos_48 == 0:
            print(f"🎉 SUCESSO: Todos os prefixos removidos!")
        else:
            print(f"⚠️ Ainda há prefixos para remover")
        
        # Limpar colunas extras de processamento
        colunas_remover = [
            'dav_str', 'prefixo_dav', 'dav_original', 'dav_limpo', 
            'dav_numerico', 'dav_normalizado', 'prefixo_removido',
            'Unnamed: 3', 'Unnamed: 0', ' '  # colunas vazias
        ]
        
        colunas_existentes = [col for col in colunas_remover if col in df.columns]
        if colunas_existentes:
            df = df.drop(columns=colunas_existentes)
            print(f"🗑️ Removidas {len(colunas_existentes)} colunas auxiliares")
        
        print(f"📋 Colunas finais: {df.shape[1]}")
        print(f"📊 Registros finais: {len(df):,}")
        
        # Salvar arquivo final
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_final = f'data/originais/controles_gerais/conf_dav/csv/conf_dav_FINAL_NORMALIZADO_{timestamp}.csv'
        
        df.to_csv(arquivo_final, index=False)
        
        print(f"\n💾 === ARQUIVO FINAL === 💾")
        print(f"📄 Arquivo: {arquivo_final}")
        print(f"📊 Registros: {len(df):,}")
        print(f"✅ Normalização: 100% aplicada")
        print(f"🎯 Status: Pronto para uso")
        
        return arquivo_final
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def verificar_normalizacao():
    """
    Verifica se a normalização foi aplicada corretamente
    """
    print(f"\n🔍 === VERIFICAÇÃO FINAL === 🔍")
    
    # Buscar arquivo final
    import glob
    arquivos = glob.glob('data/originais/controles_gerais/conf_dav/csv/conf_dav_FINAL_NORMALIZADO_*.csv')
    
    if not arquivos:
        print("❌ Arquivo final não encontrado")
        return False
    
    arquivo = sorted(arquivos)[-1]
    
    try:
        df = pd.read_csv(arquivo, nrows=1000)  # Amostra
        
        print(f"📄 Verificando: {arquivo.split('/')[-1]}")
        print(f"📊 Amostra: {len(df):,} registros")
        
        if 'Nro.DAV' not in df.columns:
            print("❌ Coluna Nro.DAV não encontrada")
            return False
        
        # Analisar valores
        dav_values = df['Nro.DAV'].dropna().astype(str)
        
        # Contar prefixos
        prefixos_42 = dav_values.str.startswith('42').sum()
        prefixos_48 = dav_values.str.startswith('48').sum()
        
        # Verificar faixas normalizadas
        numericos = pd.to_numeric(dav_values, errors='coerce')
        validos = numericos.notna().sum()
        
        if validos > 0:
            min_val = numericos.min()
            max_val = numericos.max()
            
            print(f"📊 Valores numéricos: {validos}/{len(dav_values)}")
            print(f"📊 Faixa: {min_val:.0f} até {max_val:.0f}")
        
        print(f"🔍 Prefixos restantes:")
        print(f"   42xxxx: {prefixos_42}")
        print(f"   48xxxx: {prefixos_48}")
        
        if prefixos_42 == 0 and prefixos_48 == 0:
            print(f"✅ NORMALIZAÇÃO PERFEITA!")
            return True
        else:
            print(f"❌ Ainda há prefixos")
            return False
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def main():
    """Função principal"""
    print("🎯 === CORREÇÃO FINAL NORMALIZAÇÃO DAV === 🎯")
    
    # 1. Finalizar normalização
    arquivo_final = finalizar_normalizacao_dav()
    
    if not arquivo_final:
        print("❌ Falha na normalização")
        return
    
    # 2. Verificar resultado
    sucesso = verificar_normalizacao()
    
    print(f"\n🎉 === RESULTADO FINAL === 🎉")
    if sucesso:
        print(f"✅ Normalização: CONCLUÍDA")
        print(f"📄 Arquivo: {arquivo_final}")
        print(f"🎯 Status: Pronto para cruzamentos")
    else:
        print(f"⚠️ Verificar arquivo manualmente")
    
    print(f"📅 Processado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()