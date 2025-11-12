#!/usr/bin/env python3
"""
Script de normalização completa de vendedores
Aplica todas as correções e unificações identificadas
"""

import pandas as pd
import json
from pathlib import Path
from collections import defaultdict, Counter

def criar_mapeamento_normalizacao():
    """
    Cria o mapeamento completo de normalização de vendedores
    """
    # Mapeamento de normalização - todos os nomes devem virar o nome padrão
    normalizacao = {
        # ROGÉRIO (unificar com/sem acento)
        'ROGERIO': 'ROGÉRIO',
        'ROGÉRIO': 'ROGÉRIO',
        'ROGERIO APARECIDO DE MORAIS': 'ROGÉRIO APARECIDO DE MORAIS',
        
        # ROSÂNGELA (unificar com/sem acento)  
        'ROSANGELA': 'ROSÂNGELA',
        'ROSÂNGELA': 'ROSÂNGELA',
        
        # ARIANI DIAS FERNANDES CARDOSO (nome completo correto)
        'ARIANI': 'ARIANI DIAS FERNANDES CARDOSO',
        'ARIANE DIAS FERNANDES CARDOSO': 'ARIANI DIAS FERNANDES CARDOSO',
        'ARIANI DIAS': 'ARIANI DIAS FERNANDES CARDOSO',
        
        # JOCICREIDE BARBOSA (nome completo correto)
        'JOCY': 'JOCICREIDE BARBOSA',
        'JOCI': 'JOCICREIDE BARBOSA',  
        'JOCXY': 'JOCICREIDE BARBOSA',
        'JOCICREIDE BARBOSA': 'JOCICREIDE BARBOSA',
        
        # KAYLLAINE (manter este nome)
        'KAYLANE': 'KAYLLAINE',
        'KAYLLAINE': 'KAYLLAINE',
        
        # THIAGO VINICIUS (nome completo)
        'THIAGO': 'THIAGO VINICIUS',
        
        # Outros vendedores principais (manter nomes atuais)
        'BETH': 'BETH',
        'FELIPE': 'FELIPE',
        'LARISSA': 'LARISSA',
        'TATY': 'TATY',
        'WEVILLY': 'WEVILLY',
        'ERIKA': 'ERIKA',
        'LUANA': 'LUANA',
        'BRUNA': 'BRUNA',
        'BRUNO': 'BRUNO',
        'MARIA': 'MARIA',
        'SAMUEL': 'SAMUEL',
        'SANDY': 'SANDY',
        'ZAINE': 'ZAINE',
        'YASMIN': 'YASMIN',
        'WILLIAN': 'WILLIAN',
        'VANESSA': 'VANESSA',
        'ROGER': 'ROGER',  # Pessoa diferente do ROGÉRIO
        'MIRIAM': 'MIRIAM',
        'LUCAS': 'LUCAS',
        'KEREM': 'KEREM',
        'JOANA': 'JOANA',
        'GISLANIA': 'GISLANIA'
    }
    
    return normalizacao

def normalizar_vendedor(nome_original, mapeamento):
    """
    Normaliza um nome de vendedor baseado no mapeamento
    """
    if not nome_original or str(nome_original).strip() == '' or str(nome_original) == 'nan':
        return None
    
    nome_clean = str(nome_original).strip().upper()
    
    # Busca no mapeamento
    if nome_clean in mapeamento:
        return mapeamento[nome_clean]
    
    # Se não encontrou, retorna o nome original limpo
    return nome_clean

def processar_arquivo_vendedores(arquivo_path, mapeamento, stats):
    """
    Processa um arquivo aplicando a normalização de vendedores
    """
    try:
        df = pd.read_csv(arquivo_path)
        
        # Encontrar coluna do consultor
        coluna_consultor = None
        for col in df.columns:
            if 'CONSULTOR' in col.upper():
                coluna_consultor = col
                break
        
        if not coluna_consultor:
            stats['erros'].append(f"Coluna CONSULTOR não encontrada em {arquivo_path.name}")
            return None
        
        # Aplicar normalização
        df_normalizado = df.copy()
        df_normalizado['consultor_original'] = df_normalizado[coluna_consultor].copy()
        
        df_normalizado[coluna_consultor] = df_normalizado[coluna_consultor].apply(
            lambda x: normalizar_vendedor(x, mapeamento)
        )
        
        # Estatísticas
        total_registros = len(df_normalizado)
        registros_alterados = len(df_normalizado[
            df_normalizado[coluna_consultor] != df_normalizado['consultor_original']
        ])
        
        stats['arquivos_processados'] += 1
        stats['total_registros'] += total_registros
        stats['registros_alterados'] += registros_alterados
        
        # Contar vendedores únicos
        vendedores_antes = set(df_normalizado['consultor_original'].dropna().unique())
        vendedores_depois = set(df_normalizado[coluna_consultor].dropna().unique())
        
        stats['vendedores_antes'].update(vendedores_antes)
        stats['vendedores_depois'].update(vendedores_depois)
        
        print(f"  {arquivo_path.name}:")
        print(f"    Total: {total_registros} registros")
        print(f"    Alterados: {registros_alterados} registros")
        print(f"    Vendedores antes: {len(vendedores_antes)}")
        print(f"    Vendedores depois: {len(vendedores_depois)}")
        
        # Mostrar mudanças
        mudancas = df_normalizado[
            df_normalizado[coluna_consultor] != df_normalizado['consultor_original']
        ][['consultor_original', coluna_consultor]].drop_duplicates()
        
        if len(mudancas) > 0:
            print(f"    Normalizações aplicadas:")
            for _, row in mudancas.iterrows():
                original = row['consultor_original']
                normalizado = row[coluna_consultor]
                count = len(df_normalizado[df_normalizado['consultor_original'] == original])
                print(f"      {original} → {normalizado} ({count} registros)")
        
        return df_normalizado
        
    except Exception as e:
        stats['erros'].append(f"Erro em {arquivo_path.name}: {str(e)}")
        return None

def normalizar_vendedores_completo():
    """
    Executa a normalização completa de todos os vendedores
    """
    print("🔧 NORMALIZAÇÃO COMPLETA DE VENDEDORES")
    print("="*60)
    
    # Criar mapeamento
    mapeamento = criar_mapeamento_normalizacao()
    
    print("📋 Regras de normalização:")
    for original, normalizado in sorted(mapeamento.items()):
        if original != normalizado:
            print(f"  {original} → {normalizado}")
    
    # Estatísticas
    stats = {
        'arquivos_processados': 0,
        'total_registros': 0,
        'registros_alterados': 0,
        'vendedores_antes': set(),
        'vendedores_depois': set(),
        'erros': []
    }
    
    # Processar OSs
    print(f"\n📊 Processando OSs normalizadas...")
    dir_oss = Path("data/originais/oss/normalizadas")
    dir_saida_oss = Path("data/originais/oss/normalizadas_vendedores")
    dir_saida_oss.mkdir(exist_ok=True)
    
    if dir_oss.exists():
        for arquivo in dir_oss.glob("*_normalizado.csv"):  # Só os principais, sem _uuid
            df_normalizado = processar_arquivo_vendedores(arquivo, mapeamento, stats)
            if df_normalizado is not None:
                # Salvar arquivo normalizado
                arquivo_saida = dir_saida_oss / arquivo.name.replace('_normalizado', '_vendedores_normalizados')
                df_normalizado.to_csv(arquivo_saida, index=False)
                print(f"    ✅ Salvo: {arquivo_saida.name}")
    
    # Processar Vixen
    print(f"\n📊 Processando Vixen...")
    arquivo_vixen = Path("data_backup/marketing_origens_vixen_correto.csv")
    
    if arquivo_vixen.exists():
        try:
            df_vixen = pd.read_csv(arquivo_vixen)
            
            df_vixen_normalizado = df_vixen.copy()
            df_vixen_normalizado['consultor_original'] = df_vixen_normalizado['consultor'].copy()
            
            df_vixen_normalizado['consultor'] = df_vixen_normalizado['consultor'].apply(
                lambda x: normalizar_vendedor(x, mapeamento)
            )
            
            # Estatísticas Vixen
            total_vixen = len(df_vixen_normalizado)
            alterados_vixen = len(df_vixen_normalizado[
                df_vixen_normalizado['consultor'] != df_vixen_normalizado['consultor_original']
            ])
            
            stats['arquivos_processados'] += 1
            stats['total_registros'] += total_vixen
            stats['registros_alterados'] += alterados_vixen
            
            print(f"  Vixen:")
            print(f"    Total: {total_vixen} registros")
            print(f"    Alterados: {alterados_vixen} registros")
            
            # Salvar Vixen normalizado
            arquivo_saida_vixen = Path("data_backup/marketing_origens_vixen_vendedores_normalizados.csv")
            df_vixen_normalizado.to_csv(arquivo_saida_vixen, index=False)
            print(f"    ✅ Salvo: {arquivo_saida_vixen.name}")
            
        except Exception as e:
            stats['erros'].append(f"Erro no Vixen: {str(e)}")
    
    # Relatório final
    print(f"\n" + "="*60)
    print("📈 RELATÓRIO FINAL DE NORMALIZAÇÃO")
    print(f"="*60)
    print(f"Arquivos processados: {stats['arquivos_processados']}")
    print(f"Total de registros: {stats['total_registros']}")
    print(f"Registros alterados: {stats['registros_alterados']}")
    print(f"Taxa de alteração: {(stats['registros_alterados']/stats['total_registros']*100):.1f}%")
    
    print(f"\nVendedores únicos antes: {len(stats['vendedores_antes'])}")
    print(f"Vendedores únicos depois: {len(stats['vendedores_depois'])}")
    print(f"Redução: {len(stats['vendedores_antes']) - len(stats['vendedores_depois'])} vendedores")
    
    print(f"\nVendedores finais normalizados:")
    for vendedor in sorted(stats['vendedores_depois']):
        if vendedor:  # Ignora nulos
            print(f"  ✅ {vendedor}")
    
    if stats['erros']:
        print(f"\n❌ Erros encontrados:")
        for erro in stats['erros']:
            print(f"  {erro}")
    
    # Salvar relatório
    relatorio = {
        'arquivos_processados': stats['arquivos_processados'],
        'total_registros': stats['total_registros'],
        'registros_alterados': stats['registros_alterados'],
        'vendedores_antes': sorted(list(stats['vendedores_antes'])),
        'vendedores_depois': sorted(list(stats['vendedores_depois'])),
        'mapeamento_usado': mapeamento,
        'erros': stats['erros']
    }
    
    with open('relatorio_normalizacao_vendedores.json', 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório salvo em: relatorio_normalizacao_vendedores.json")
    print(f"📂 Arquivos OSs salvos em: {dir_saida_oss}")
    print(f"📂 Arquivo Vixen salvo em: data_backup/")
    
    return stats

if __name__ == "__main__":
    print("SCRIPT DE NORMALIZAÇÃO DE VENDEDORES")
    print("="*50)
    
    resposta = input("Deseja executar a normalização completa? (s/n): ")
    
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        normalizar_vendedores_completo()
        print(f"\n✅ Normalização concluída!")
        print("Agora os vendedores estão unificados e prontos para o mapeamento UUID.")
    else:
        print("Normalização cancelada.")