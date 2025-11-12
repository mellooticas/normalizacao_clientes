#!/usr/bin/env python3
"""
Script final para integrar todos os UUIDs com tratamento de valores nulos
"""

import pandas as pd
import json
import os
import uuid

def integrar_todos_uuids_final():
    """Integra todos os UUIDs com tratamento completo de valores nulos"""
    
    print("🎯 INTEGRAÇÃO FINAL DE TODOS OS UUIDS")
    print("=" * 50)
    
    # Carregar mapeamento dos canais
    with open('mapeamento_canais_captacao_uuid.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    canais_uuid = data['canais_captacao_uuid']
    
    # Adicionar UUID para "NÃO INFORMADO" (para valores nulos/vazios)
    uuid_nao_informado = str(uuid.uuid4())
    canais_uuid['NÃO INFORMADO'] = uuid_nao_informado
    
    # Diretórios
    dir_entrada = 'data/originais/oss/finais_com_uuids'
    dir_saida = 'data/originais/oss/finais_todos_uuids_final'
    
    # Criar diretório de saída
    os.makedirs(dir_saida, exist_ok=True)
    
    # Listar arquivos de entrada
    arquivos_entrada = [f for f in os.listdir(dir_entrada) if f.endswith('_final_completo.csv')]
    
    total_registros = 0
    total_integracoes = 0
    total_nao_informados = 0
    
    for arquivo in sorted(arquivos_entrada):
        print(f"\n📄 Processando: {arquivo}")
        
        # Ler arquivo
        caminho_entrada = os.path.join(dir_entrada, arquivo)
        df = pd.read_csv(caminho_entrada)
        
        registros_original = len(df)
        
        # Tratar valores nulos e vazios
        def tratar_canal(valor):
            if pd.isna(valor) or str(valor).strip() == '' or str(valor).strip() == 'nan':
                return 'NÃO INFORMADO'
            return str(valor).strip()
        
        df['canal_tratado'] = df['COMO CONHECEU '].apply(tratar_canal)
        
        # Mapear canais de captação para UUIDs
        df['canal_captacao_uuid'] = df['canal_tratado'].map(canais_uuid)
        df['canal_captacao_nome'] = df['canal_tratado']
        
        # Verificar mapeamentos
        sem_uuid = df['canal_captacao_uuid'].isna().sum()
        com_uuid = len(df) - sem_uuid
        nao_informados = (df['canal_captacao_nome'] == 'NÃO INFORMADO').sum()
        
        print(f"   • Registros originais: {registros_original:,}")
        print(f"   • Com canal UUID: {com_uuid:,}")
        print(f"   • Sem canal UUID: {sem_uuid:,}")
        print(f"   • Não informados: {nao_informados:,}")
        
        if sem_uuid > 0:
            canais_faltantes = df[df['canal_captacao_uuid'].isna()]['canal_tratado'].unique()
            print(f"   ⚠️  Canais sem UUID: {list(canais_faltantes)}")
        
        # Reorganizar colunas
        colunas_finais = [
            'loja_id', 'loja_nome',
            'vendedor_uuid', 'vendedor_nome_normalizado', 
            'canal_captacao_uuid', 'canal_captacao_nome'
        ] + [col for col in df.columns if col not in [
            'loja_id', 'loja_nome', 'vendedor_uuid', 'vendedor_nome_normalizado',
            'canal_captacao_uuid', 'canal_captacao_nome', 'canal_tratado'
        ]]
        
        df_final = df[colunas_finais]
        
        # Salvar arquivo final
        nome_saida = arquivo.replace('_final_completo.csv', '_todos_uuids_final.csv')
        caminho_saida = os.path.join(dir_saida, nome_saida)
        
        df_final.to_csv(caminho_saida, index=False)
        
        print(f"   ✅ Salvo: {nome_saida}")
        
        total_registros += registros_original
        total_integracoes += com_uuid
        total_nao_informados += nao_informados
    
    print(f"\n🎉 INTEGRAÇÃO FINAL COMPLETA!")
    print(f"📊 ESTATÍSTICAS FINAIS:")
    print(f"   • Arquivos processados: {len(arquivos_entrada)}")
    print(f"   • Total de registros: {total_registros:,}")
    print(f"   • Integrações de canais: {total_integracoes:,}")
    print(f"   • Taxa de sucesso: {(total_integracoes/total_registros)*100:.1f}%")
    print(f"   • Não informados: {total_nao_informados:,}")
    print(f"   • Diretório de saída: {dir_saida}")
    
    # Salvar mapeamento completo com "NÃO INFORMADO"
    data_completa = data.copy()
    data_completa['canais_captacao_uuid'] = canais_uuid
    data_completa['total_canais'] = len(canais_uuid)
    
    with open('mapeamento_canais_captacao_uuid_final.json', 'w', encoding='utf-8') as f:
        json.dump(data_completa, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 MAPEAMENTO FINAL SALVO:")
    print(f"   • Arquivo: mapeamento_canais_captacao_uuid_final.json")
    print(f"   • Total de canais: {len(canais_uuid)} (incluindo 'NÃO INFORMADO')")
    
    # Listar arquivos criados
    print(f"\n📁 ARQUIVOS FINAIS CRIADOS:")
    arquivos_criados = [f for f in os.listdir(dir_saida) if f.endswith('.csv')]
    total_size = 0
    for arquivo in sorted(arquivos_criados):
        size_kb = os.path.getsize(os.path.join(dir_saida, arquivo)) / 1024
        total_size += size_kb
        print(f"   • {arquivo} ({size_kb:.1f} KB)")
    
    print(f"   📦 Total: {total_size:.1f} KB")
    
    # Resumo dos canais por loja
    print(f"\n📈 TOP 3 CANAIS POR LOJA:")
    for arquivo in sorted(arquivos_entrada):
        caminho = os.path.join(dir_saida, arquivo.replace('_final_completo.csv', '_todos_uuids_final.csv'))
        if os.path.exists(caminho):
            df_analise = pd.read_csv(caminho)
            distribuicao = df_analise['canal_captacao_nome'].value_counts()
            loja = arquivo.replace('_final_completo.csv', '')
            print(f"\n   📍 {loja} ({len(df_analise):,} registros):")
            for canal, qtd in distribuicao.head(3).items():
                perc = (qtd / len(df_analise)) * 100
                print(f"     • {canal}: {qtd:,} ({perc:.1f}%)")

if __name__ == "__main__":
    integrar_todos_uuids_final()