#!/usr/bin/env python3
"""
Aplicar UUIDs dos vendedores com base no mapeamento fornecido
Executa após o preenchimento do arquivo mapeamento_vendedores_uuid.txt
"""

import pandas as pd
import glob
import uuid
import re
from pathlib import Path

def carregar_mapeamento_vendedores():
    """Carrega mapeamento de vendedores do arquivo de configuração"""
    print("📁 CARREGANDO MAPEAMENTO DE VENDEDORES...")
    
    mapeamento = {}
    novos_uuids = {}
    
    try:
        with open('mapeamento_vendedores_uuid.txt', 'r', encoding='utf-8') as f:
            for linha_num, linha in enumerate(f, 1):
                linha = linha.strip()
                
                # Ignorar comentários e linhas vazias
                if not linha or linha.startswith('#') or '=' not in linha:
                    continue
                
                # Extrair nome e valor
                partes = linha.split('=', 1)
                if len(partes) != 2:
                    continue
                
                nome = partes[0].strip()
                valor = partes[1].strip()
                
                if not nome or not valor:
                    continue
                
                # Processar comandos especiais
                if valor == 'NOVO':
                    if nome not in novos_uuids:
                        novos_uuids[nome] = str(uuid.uuid4())
                        print(f"   🆕 Novo UUID para {nome}: {novos_uuids[nome]}")
                    mapeamento[nome] = novos_uuids[nome]
                
                elif valor == 'IGNORAR':
                    print(f"   🚫 Ignorando: {nome}")
                    continue
                
                elif re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', valor):
                    mapeamento[nome] = valor
                    print(f"   ✅ Mapeado {nome}: {valor}")
                
                else:
                    print(f"   ⚠️  Linha {linha_num}: Valor inválido para {nome}: {valor}")
        
        print(f"\n✅ Carregados {len(mapeamento)} mapeamentos de vendedores")
        return mapeamento
    
    except FileNotFoundError:
        print("❌ Arquivo mapeamento_vendedores_uuid.txt não encontrado!")
        print("   Preencha o arquivo antes de executar este script.")
        return None
    except Exception as e:
        print(f"❌ Erro ao carregar mapeamento: {e}")
        return None

def aplicar_uuids_vendedores(mapeamento):
    """Aplica UUIDs de vendedores em todos os arquivos"""
    print(f"\n🔄 APLICANDO UUIDs DE VENDEDORES...")
    print("="*50)
    
    if not mapeamento:
        print("❌ Nenhum mapeamento disponível")
        return
    
    # Tabelas para processar
    tabelas = ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']
    
    estatisticas_geral = {}
    
    for tabela in tabelas:
        print(f"\n📋 PROCESSANDO: {tabela.upper()}")
        print("-" * 30)
        
        caminho = f"data/originais/cxs/extraidos_corrigidos/{tabela}/*_enriquecido_completo.csv"
        arquivos = glob.glob(caminho)
        arquivos_lojas = [a for a in arquivos if 'todas_lojas' not in a]
        
        estatisticas_tabela = {}
        
        for arquivo in arquivos_lojas:
            nome_arquivo = Path(arquivo).stem
            loja = nome_arquivo.split('_')[1] if '_' in nome_arquivo else 'DESCONHECIDA'
            
            print(f"\n📁 {nome_arquivo}")
            
            try:
                df = pd.read_csv(arquivo)
                total_registros = len(df)
                
                # Identificar campo de vendedor
                campo_vendedor = None
                if 'vendedor' in df.columns:
                    campo_vendedor = 'vendedor'
                elif 'vendedor_nome_normalizado' in df.columns:
                    campo_vendedor = 'vendedor_nome_normalizado'
                
                if not campo_vendedor:
                    print("   ⚠️  Campo vendedor não encontrado")
                    continue
                
                # Contar antes da aplicação
                antes_com_uuid = df['vendedor_uuid'].notna().sum()
                antes_sem_uuid = df['vendedor_uuid'].isna().sum()
                
                print(f"   📊 Antes: {antes_com_uuid} com UUID, {antes_sem_uuid} sem UUID")
                
                # Aplicar mapeamento
                aplicados = 0
                for nome_vendedor, uuid_vendedor in mapeamento.items():
                    # Encontrar registros com este vendedor sem UUID
                    mask = (df[campo_vendedor] == nome_vendedor) & (df['vendedor_uuid'].isna())
                    registros_encontrados = mask.sum()
                    
                    if registros_encontrados > 0:
                        df.loc[mask, 'vendedor_uuid'] = uuid_vendedor
                        df.loc[mask, 'vendedor_nome_normalizado'] = nome_vendedor
                        aplicados += registros_encontrados
                        print(f"   ✅ {nome_vendedor}: {registros_encontrados} registros atualizados")
                
                # Contar depois da aplicação
                depois_com_uuid = df['vendedor_uuid'].notna().sum()
                depois_sem_uuid = df['vendedor_uuid'].isna().sum()
                
                print(f"   📊 Depois: {depois_com_uuid} com UUID, {depois_sem_uuid} sem UUID")
                print(f"   🎯 Aplicados: {aplicados} novos UUIDs")
                
                # Salvar arquivo atualizado
                if aplicados > 0:
                    df.to_csv(arquivo, index=False)
                    print(f"   💾 Arquivo salvo com atualizações")
                
                # Estatísticas
                estatisticas_tabela[loja] = {
                    'total_registros': total_registros,
                    'antes_com_uuid': antes_com_uuid,
                    'depois_com_uuid': depois_com_uuid,
                    'aplicados': aplicados
                }
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
        
        estatisticas_geral[tabela] = estatisticas_tabela
    
    return estatisticas_geral

def gerar_relatorio_aplicacao(estatisticas_geral):
    """Gera relatório da aplicação de UUIDs"""
    print(f"\n" + "="*60)
    print("📊 RELATÓRIO DE APLICAÇÃO DE UUIDs")
    print("="*60)
    
    total_aplicados = 0
    total_registros = 0
    
    for tabela, lojas in estatisticas_geral.items():
        print(f"\n📋 {tabela.upper()}:")
        
        for loja, stats in lojas.items():
            aplicados = stats['aplicados']
            total_registros += stats['total_registros']
            total_aplicados += aplicados
            
            if aplicados > 0:
                print(f"   ✅ {loja}: {aplicados} UUIDs aplicados")
            else:
                print(f"   ➖ {loja}: Nenhum UUID aplicado")
    
    print(f"\n🎯 RESUMO GERAL:")
    print(f"   📊 Total de registros processados: {total_registros:,}")
    print(f"   ✅ Total de UUIDs aplicados: {total_aplicados:,}")
    
    if total_aplicados > 0:
        print(f"\n🎉 SUCESSO! {total_aplicados} vendedores agora têm UUID!")
    else:
        print(f"\n⚠️  Nenhum UUID foi aplicado. Verifique o mapeamento.")

def verificar_cobertura_final():
    """Verifica cobertura final após aplicação"""
    print(f"\n" + "="*60)
    print("🔍 VERIFICAÇÃO FINAL DE COBERTURA")
    print("="*60)
    
    # Executar auditoria rápida
    tabelas = ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']
    
    total_registros = 0
    total_com_uuid = 0
    
    for tabela in tabelas:
        caminho = f"data/originais/cxs/extraidos_corrigidos/{tabela}/*_enriquecido_completo.csv"
        arquivos = glob.glob(caminho)
        arquivos_lojas = [a for a in arquivos if 'todas_lojas' not in a]
        
        for arquivo in arquivos_lojas:
            try:
                df = pd.read_csv(arquivo)
                registros = len(df)
                com_uuid = df['vendedor_uuid'].notna().sum()
                
                total_registros += registros
                total_com_uuid += com_uuid
                
            except:
                continue
    
    if total_registros > 0:
        taxa_final = (total_com_uuid / total_registros * 100)
        print(f"📊 Cobertura Final de Vendedor UUID: {total_com_uuid:,}/{total_registros:,} ({taxa_final:.1f}%)")
        
        if taxa_final == 100:
            print("🎉 PARABÉNS! 100% DOS VENDEDORES AGORA TÊM UUID!")
        elif taxa_final >= 95:
            print("✅ Excelente cobertura! Quase todos os vendedores têm UUID.")
        else:
            print("⚠️  Ainda há vendedores sem UUID. Verifique se o mapeamento está completo.")

def executar_aplicacao_uuids():
    """Executa aplicação completa de UUIDs de vendedores"""
    print("🚀 APLICAÇÃO DE UUIDs DE VENDEDORES")
    print("="*60)
    
    # 1. Carregar mapeamento
    mapeamento = carregar_mapeamento_vendedores()
    if not mapeamento:
        return
    
    # 2. Aplicar UUIDs
    estatisticas = aplicar_uuids_vendedores(mapeamento)
    
    # 3. Gerar relatório
    gerar_relatorio_aplicacao(estatisticas)
    
    # 4. Verificar cobertura final
    verificar_cobertura_final()
    
    print("\n✅ APLICAÇÃO CONCLUÍDA!")

if __name__ == "__main__":
    executar_aplicacao_uuids()