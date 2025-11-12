#!/usr/bin/env python3
"""
Script para integrar UUIDs dos canais de captação nos arquivos finais
"""

import pandas as pd
import json
import os

def integrar_canais_captacao_uuid():
    """Integra UUIDs dos canais de captação nos arquivos finais"""
    
    print("🎯 INTEGRANDO CANAIS DE CAPTAÇÃO UUID")
    print("=" * 50)
    
    # Carregar mapeamento dos canais
    with open('mapeamento_canais_captacao_uuid.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    canais_uuid = data['canais_captacao_uuid']
    
    # Diretórios
    dir_entrada = 'data/originais/oss/finais_com_uuids'
    dir_saida = 'data/originais/oss/finais_completos_com_todos_uuids'
    
    # Criar diretório de saída
    os.makedirs(dir_saida, exist_ok=True)
    
    # Listar arquivos de entrada
    arquivos_entrada = [f for f in os.listdir(dir_entrada) if f.endswith('_final_completo.csv')]
    
    total_registros = 0
    total_integracoes = 0
    
    for arquivo in sorted(arquivos_entrada):
        print(f"\n📄 Processando: {arquivo}")
        
        # Ler arquivo
        caminho_entrada = os.path.join(dir_entrada, arquivo)
        df = pd.read_csv(caminho_entrada)
        
        registros_original = len(df)
        
        # Mapear canais de captação para UUIDs
        df['canal_captacao_uuid'] = df['COMO CONHECEU '].map(canais_uuid)
        df['canal_captacao_nome'] = df['COMO CONHECEU ']
        
        # Verificar mapeamentos
        sem_uuid = df['canal_captacao_uuid'].isna().sum()
        com_uuid = len(df) - sem_uuid
        
        print(f"   • Registros originais: {registros_original:,}")
        print(f"   • Com canal UUID: {com_uuid:,}")
        print(f"   • Sem canal UUID: {sem_uuid:,}")
        
        if sem_uuid > 0:
            canais_faltantes = df[df['canal_captacao_uuid'].isna()]['COMO CONHECEU '].unique()
            print(f"   ⚠️  Canais sem UUID: {list(canais_faltantes)}")
        
        # Reorganizar colunas
        colunas_finais = [
            'loja_id', 'loja_nome',
            'vendedor_uuid', 'vendedor_nome_normalizado', 
            'canal_captacao_uuid', 'canal_captacao_nome'
        ] + [col for col in df.columns if col not in [
            'loja_id', 'loja_nome', 'vendedor_uuid', 'vendedor_nome_normalizado',
            'canal_captacao_uuid', 'canal_captacao_nome'
        ]]
        
        df_final = df[colunas_finais]
        
        # Salvar arquivo final
        nome_saida = arquivo.replace('_final_completo.csv', '_final_todos_uuids.csv')
        caminho_saida = os.path.join(dir_saida, nome_saida)
        
        df_final.to_csv(caminho_saida, index=False)
        
        print(f"   ✅ Salvo: {nome_saida}")
        
        total_registros += registros_original
        total_integracoes += com_uuid
    
    print(f"\n🎉 INTEGRAÇÃO COMPLETA!")
    print(f"📊 ESTATÍSTICAS FINAIS:")
    print(f"   • Arquivos processados: {len(arquivos_entrada)}")
    print(f"   • Total de registros: {total_registros:,}")
    print(f"   • Integrações de canais: {total_integracoes:,}")
    print(f"   • Taxa de sucesso: {(total_integracoes/total_registros)*100:.1f}%")
    print(f"   • Diretório de saída: {dir_saida}")
    
    # Listar arquivos criados
    print(f"\n📁 ARQUIVOS CRIADOS:")
    arquivos_criados = [f for f in os.listdir(dir_saida) if f.endswith('.csv')]
    for arquivo in sorted(arquivos_criados):
        size_kb = os.path.getsize(os.path.join(dir_saida, arquivo)) / 1024
        print(f"   • {arquivo} ({size_kb:.1f} KB)")
    
    # Análise de distribuição dos canais
    print(f"\n📈 DISTRIBUIÇÃO DOS CANAIS:")
    for arquivo in sorted(arquivos_entrada):
        caminho = os.path.join(dir_saida, arquivo.replace('_final_completo.csv', '_final_todos_uuids.csv'))
        if os.path.exists(caminho):
            df_analise = pd.read_csv(caminho)
            distribuicao = df_analise['canal_captacao_nome'].value_counts()
            print(f"\n   {arquivo.replace('_final_completo.csv', '')}:")
            for canal, qtd in distribuicao.head(3).items():
                print(f"     • {canal}: {qtd:,}")

if __name__ == "__main__":
    integrar_canais_captacao_uuid()