#!/usr/bin/env python3
"""
Script final para integrar UUIDs da estrutura de canais de aquisição nos CSVs
"""

import pandas as pd
import json
import os

def integrar_canais_aquisicao_final():
    """Integra UUIDs da estrutura completa de canais de aquisição nos CSVs finais"""
    
    print("🏆 INTEGRAÇÃO FINAL - CANAIS DE AQUISIÇÃO UUID")
    print("=" * 60)
    
    # Carregar mapeamento CSV → Estrutura
    with open('mapeamento_canais_csv_para_estrutura.json', 'r', encoding='utf-8') as f:
        mapeamento = json.load(f)
    
    mapeamento_uuids = {}
    for canal_csv, info in mapeamento['mapeamento'].items():
        mapeamento_uuids[canal_csv] = info['uuid']
    
    print(f"📊 MAPEAMENTO CARREGADO:")
    print(f"   • Canais mapeados: {len(mapeamento_uuids)}")
    print(f"   • Taxa de sucesso: {mapeamento['taxa_sucesso']:.1f}%")
    
    # Diretórios
    dir_entrada = 'data/originais/oss/finais_com_uuids'
    dir_saida = 'data/originais/oss/finais_canais_aquisicao_uuid'
    
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
        
        # Tratar valores nulos e vazios primeiro
        def tratar_canal(valor):
            if pd.isna(valor) or str(valor).strip() == '' or str(valor).strip() == 'nan':
                return 'NÃO INFORMADO'
            return str(valor).strip()
        
        df['canal_tratado'] = df['COMO CONHECEU '].apply(tratar_canal)
        
        # Mapear para UUIDs da estrutura de aquisição
        df['canal_aquisicao_uuid'] = df['canal_tratado'].map(mapeamento_uuids)
        df['canal_aquisicao_nome'] = df['canal_tratado']
        
        # Verificar mapeamentos
        sem_uuid = df['canal_aquisicao_uuid'].isna().sum()
        com_uuid = len(df) - sem_uuid
        
        print(f"   • Registros originais: {registros_original:,}")
        print(f"   • Com canal UUID: {com_uuid:,}")
        print(f"   • Sem canal UUID: {sem_uuid:,}")
        
        if sem_uuid > 0:
            canais_faltantes = df[df['canal_aquisicao_uuid'].isna()]['canal_tratado'].unique()
            print(f"   ⚠️  Canais sem UUID: {list(canais_faltantes)}")
        
        # Reorganizar colunas para estrutura final
        colunas_finais = [
            # IDs principais
            'loja_id', 'loja_nome',
            'vendedor_uuid', 'vendedor_nome_normalizado',
            'canal_aquisicao_uuid', 'canal_aquisicao_nome',
            
            # Dados da OS
            'OS', 'NUMERO_OS', 'CLIENTE', 'CPF',
            'DATA_VENDA', 'VALOR_VENDA', 'FORMA_PAGAMENTO',
            
            # Demais colunas (se existirem)
        ] + [col for col in df.columns if col not in [
            'loja_id', 'loja_nome', 'vendedor_uuid', 'vendedor_nome_normalizado',
            'canal_aquisicao_uuid', 'canal_aquisicao_nome', 'canal_tratado',
            'OS', 'NUMERO_OS', 'CLIENTE', 'CPF', 'DATA_VENDA', 'VALOR_VENDA', 'FORMA_PAGAMENTO'
        ]]
        
        # Selecionar apenas colunas que existem no DataFrame
        colunas_existentes = [col for col in colunas_finais if col in df.columns]
        df_final = df[colunas_existentes]
        
        # Salvar arquivo final
        nome_saida = arquivo.replace('_final_completo.csv', '_aquisicao_uuid_final.csv')
        caminho_saida = os.path.join(dir_saida, nome_saida)
        
        df_final.to_csv(caminho_saida, index=False)
        
        print(f"   ✅ Salvo: {nome_saida}")
        print(f"   📊 Colunas: {len(colunas_existentes)}")
        
        total_registros += registros_original
        total_integracoes += com_uuid
    
    print(f"\n🎉 INTEGRAÇÃO FINAL COMPLETA!")
    print(f"📊 ESTATÍSTICAS GLOBAIS:")
    print(f"   • Arquivos processados: {len(arquivos_entrada)}")
    print(f"   • Total de registros: {total_registros:,}")
    print(f"   • Integrações de canais: {total_integracoes:,}")
    print(f"   • Taxa de sucesso: {(total_integracoes/total_registros)*100:.1f}%")
    print(f"   • Diretório de saída: {dir_saida}")
    
    # Listar arquivos criados
    print(f"\n📁 ARQUIVOS FINAIS CRIADOS:")
    arquivos_criados = [f for f in os.listdir(dir_saida) if f.endswith('.csv')]
    total_size = 0
    
    for arquivo in sorted(arquivos_criados):
        size_kb = os.path.getsize(os.path.join(dir_saida, arquivo)) / 1024
        total_size += size_kb
        print(f"   • {arquivo} ({size_kb:.1f} KB)")
    
    print(f"   📦 Total: {total_size:.1f} KB")
    
    # Análise de distribuição por categoria
    print(f"\n📈 DISTRIBUIÇÃO POR CATEGORIA DE CANAL:")
    
    categorias_totais = {}
    for arquivo in sorted(arquivos_entrada):
        caminho = os.path.join(dir_saida, arquivo.replace('_final_completo.csv', '_aquisicao_uuid_final.csv'))
        if os.path.exists(caminho):
            df_analise = pd.read_csv(caminho)
            
            # Adicionar informação de categoria
            for canal_nome in df_analise['canal_aquisicao_nome'].unique():
                if canal_nome in mapeamento['mapeamento']:
                    categoria = mapeamento['mapeamento'][canal_nome]['categoria']
                    qtd = len(df_analise[df_analise['canal_aquisicao_nome'] == canal_nome])
                    categorias_totais[categoria] = categorias_totais.get(categoria, 0) + qtd
    
    for categoria, qtd in sorted(categorias_totais.items(), key=lambda x: x[1], reverse=True):
        perc = (qtd / total_registros) * 100
        print(f"   • {categoria:15}: {qtd:4,} ({perc:5.1f}%)")
    
    # Estrutura final dos arquivos
    print(f"\n🗂️  ESTRUTURA FINAL DOS CSVS:")
    print(f"   📄 Colunas principais:")
    print(f"      • loja_id (UUID) - Referência da loja")
    print(f"      • loja_nome - Nome da loja") 
    print(f"      • vendedor_uuid (UUID) - Referência do vendedor")
    print(f"      • vendedor_nome_normalizado - Nome normalizado do vendedor")
    print(f"      • canal_aquisicao_uuid (UUID) - Referência do canal de aquisição")
    print(f"      • canal_aquisicao_nome - Nome do canal de aquisição")
    print(f"      • [demais colunas da OS...]")
    
    print(f"\n✅ INTEGRAÇÃO COM ESTRUTURA COMPLETA FINALIZADA!")
    print(f"🎯 PRÓXIMOS PASSOS:")
    print(f"   1. Executar SQL da estrutura: database/12_estrutura_canais_aquisicao.sql")
    print(f"   2. Importar dados dos CSVs finais para o banco")
    print(f"   3. Criar relacionamento entre OS e canais de aquisição")
    print(f"   4. Validar integridade referencial completa")

if __name__ == "__main__":
    integrar_canais_aquisicao_final()