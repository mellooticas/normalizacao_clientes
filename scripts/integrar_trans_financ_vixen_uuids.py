#!/usr/bin/env python3
"""
Integração Trans Financ com VIXEN - UUIDs
Faz cruzamento dos clientes (ID.2) do Trans Financ com UUIDs do VIXEN
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

def integrar_trans_financ_vixen_uuids():
    """Integra dados financeiros com UUIDs de clientes e lojas do VIXEN"""
    
    print("🔗 INTEGRAÇÃO TRANS FINANC ↔ VIXEN UUIDs")
    print("=" * 60)
    
    # Carregar dados do Trans Financ
    pasta_trans = Path("data/originais/controles_gerais/trans_financ_final")
    
    # Carregar dados do VIXEN (assumindo que estão organizados)
    pasta_vixen = Path("data/originais")
    
    print("📊 1. ANALISANDO CLIENTES DO TRANS FINANC")
    print("-" * 45)
    
    # Analisar clientes em todos os arquivos Trans Financ
    clientes_trans_financ = analisar_clientes_trans_financ(pasta_trans)
    
    print("📊 2. CARREGANDO UUIDs DO VIXEN")
    print("-" * 35)
    
    # Carregar UUIDs do VIXEN
    uuids_vixen = carregar_uuids_vixen(pasta_vixen)
    
    print("🔗 3. FAZENDO CRUZAMENTO DE DADOS")
    print("-" * 35)
    
    # Fazer cruzamento
    resultado_cruzamento = fazer_cruzamento_uuids(clientes_trans_financ, uuids_vixen)
    
    print("💾 4. SALVANDO RESULTADOS")
    print("-" * 25)
    
    # Salvar resultados
    salvar_integracao_uuids(resultado_cruzamento, pasta_trans)
    
    return resultado_cruzamento

def analisar_clientes_trans_financ(pasta_trans):
    """Analisa todos os clientes presentes nos arquivos Trans Financ"""
    
    clientes_consolidados = {}
    total_registros = 0
    
    # Processar todos os arquivos Trans Financ
    arquivos_trans = list(pasta_trans.glob("trans_financ_*.csv"))
    
    print(f"📁 Encontrados {len(arquivos_trans)} arquivos Trans Financ")
    
    for arquivo in arquivos_trans:
        print(f"   📄 Processando: {arquivo.name}")
        
        try:
            df = pd.read_csv(arquivo, encoding='utf-8', low_memory=False)
            
            # Verificar colunas importantes para clientes
            colunas_cliente = ['ID.2', 'Cliente', 'Cliente.1', 'CPF/CNPJ']
            colunas_presentes = [col for col in colunas_cliente if col in df.columns]
            
            print(f"      📋 Colunas cliente encontradas: {colunas_presentes}")
            
            # Analisar clientes por ID.2 (principal identificador)
            if 'ID.2' in df.columns:
                clientes_arquivo = analisar_clientes_arquivo(df, arquivo.name)
                
                # Consolidar com dados globais
                for cliente_id, dados in clientes_arquivo.items():
                    if cliente_id not in clientes_consolidados:
                        clientes_consolidados[cliente_id] = {
                            'nome_cliente': dados['nome_cliente'],
                            'cpf_cnpj': dados['cpf_cnpj'],
                            'arquivos_origem': [],
                            'total_transacoes': 0,
                            'valor_total': 0.0,
                            'primeira_transacao': None,
                            'ultima_transacao': None
                        }
                    
                    # Atualizar dados consolidados
                    clientes_consolidados[cliente_id]['arquivos_origem'].append(arquivo.name)
                    clientes_consolidados[cliente_id]['total_transacoes'] += dados['total_transacoes']
                    clientes_consolidados[cliente_id]['valor_total'] += dados['valor_total']
                    
                    # Atualizar datas
                    if dados['primeira_transacao']:
                        if not clientes_consolidados[cliente_id]['primeira_transacao'] or \
                           dados['primeira_transacao'] < clientes_consolidados[cliente_id]['primeira_transacao']:
                            clientes_consolidados[cliente_id]['primeira_transacao'] = dados['primeira_transacao']
                    
                    if dados['ultima_transacao']:
                        if not clientes_consolidados[cliente_id]['ultima_transacao'] or \
                           dados['ultima_transacao'] > clientes_consolidados[cliente_id]['ultima_transacao']:
                            clientes_consolidados[cliente_id]['ultima_transacao'] = dados['ultima_transacao']
            
            total_registros += len(df)
            print(f"      ✅ {len(df):,} registros processados")
            
        except Exception as e:
            print(f"      ❌ Erro: {e}")
    
    print(f"\n📊 RESUMO CLIENTES TRANS FINANC:")
    print(f"   👥 Clientes únicos (ID.2): {len(clientes_consolidados)}")
    print(f"   📄 Total de registros: {total_registros:,}")
    
    # Top 10 clientes por valor
    top_clientes = sorted(clientes_consolidados.items(), 
                         key=lambda x: x[1]['valor_total'], reverse=True)[:10]
    
    print(f"\n🏆 TOP 10 CLIENTES POR VALOR:")
    for i, (cliente_id, dados) in enumerate(top_clientes, 1):
        nome = dados['nome_cliente'] or 'SEM NOME'
        valor = dados['valor_total']
        transacoes = dados['total_transacoes']
        print(f"   {i:2d}. ID {cliente_id}: {nome[:30]} - R$ {valor:,.2f} ({transacoes} transações)")
    
    return clientes_consolidados

def analisar_clientes_arquivo(df, nome_arquivo):
    """Analisa clientes de um arquivo específico"""
    
    clientes_arquivo = {}
    
    # Agrupar por ID.2
    if 'ID.2' in df.columns:
        for cliente_id in df['ID.2'].dropna().unique():
            if cliente_id == 0:  # Ignorar ID 0 (geralmente sistema)
                continue
                
            # Filtrar transações deste cliente
            df_cliente = df[df['ID.2'] == cliente_id]
            
            # Extrair informações do cliente
            nome_cliente = None
            cpf_cnpj = None
            
            if 'Cliente.1' in df.columns:
                nomes = df_cliente['Cliente.1'].dropna().unique()
                if len(nomes) > 0:
                    nome_cliente = nomes[0]
            
            if 'CPF/CNPJ' in df.columns:
                cpfs = df_cliente['CPF/CNPJ'].dropna().unique()
                if len(cpfs) > 0:
                    cpf_cnpj = cpfs[0]
            
            # Calcular estatísticas
            valor_total = 0.0
            if 'Vl.líquido' in df_cliente.columns:
                valor_total = df_cliente['Vl.líquido'].sum()
            
            # Datas
            primeira_transacao = None
            ultima_transacao = None
            
            if 'Dh.emissão' in df_cliente.columns:
                datas = pd.to_datetime(df_cliente['Dh.emissão'], errors='coerce').dropna()
                if len(datas) > 0:
                    primeira_transacao = datas.min()
                    ultima_transacao = datas.max()
            
            clientes_arquivo[cliente_id] = {
                'nome_cliente': nome_cliente,
                'cpf_cnpj': cpf_cnpj,
                'total_transacoes': len(df_cliente),
                'valor_total': valor_total,
                'primeira_transacao': primeira_transacao,
                'ultima_transacao': ultima_transacao
            }
    
    return clientes_arquivo

def carregar_uuids_vixen(pasta_vixen):
    """Carrega UUIDs de clientes e lojas do VIXEN"""
    
    print("🔍 Procurando dados VIXEN com UUIDs...")
    
    # Procurar arquivos VIXEN com UUIDs
    arquivos_vixen_possiveis = [
        "vixen_clientes_com_uuid.csv",
        "vixen_clientes_uuid.csv", 
        "clientes_vixen_uuid.csv",
        "base_clientes_vixen_uuid.csv"
    ]
    
    uuids_encontrados = {
        'clientes': {},
        'lojas': {},
        'arquivos_processados': []
    }
    
    # Buscar recursivamente
    for arquivo_nome in arquivos_vixen_possiveis:
        arquivos_encontrados = list(pasta_vixen.rglob(arquivo_nome))
        
        for arquivo in arquivos_encontrados:
            print(f"   📄 Carregando: {arquivo}")
            
            try:
                df_vixen = pd.read_csv(arquivo, encoding='utf-8')
                
                # Processar clientes com UUID
                if 'uuid' in df_vixen.columns and 'id_cliente' in df_vixen.columns:
                    for _, row in df_vixen.iterrows():
                        if pd.notna(row['uuid']) and pd.notna(row['id_cliente']):
                            uuids_encontrados['clientes'][int(row['id_cliente'])] = {
                                'uuid': row['uuid'],
                                'nome': row.get('nome_cliente', ''),
                                'arquivo_origem': arquivo.name
                            }
                
                uuids_encontrados['arquivos_processados'].append(arquivo.name)
                print(f"      ✅ {len(df_vixen)} registros carregados")
                
            except Exception as e:
                print(f"      ❌ Erro ao carregar {arquivo}: {e}")
    
    # Buscar dados de lojas
    arquivos_lojas = list(pasta_vixen.rglob("*loja*uuid*.csv"))
    
    for arquivo in arquivos_lojas:
        print(f"   🏪 Carregando lojas: {arquivo}")
        
        try:
            df_lojas = pd.read_csv(arquivo, encoding='utf-8')
            
            if 'uuid' in df_lojas.columns and 'id_loja' in df_lojas.columns:
                for _, row in df_lojas.iterrows():
                    if pd.notna(row['uuid']) and pd.notna(row['id_loja']):
                        uuids_encontrados['lojas'][int(row['id_loja'])] = {
                            'uuid': row['uuid'],
                            'nome_loja': row.get('nome_loja', ''),
                            'arquivo_origem': arquivo.name
                        }
            
            uuids_encontrados['arquivos_processados'].append(arquivo.name)
            print(f"      ✅ {len(df_lojas)} lojas carregadas")
            
        except Exception as e:
            print(f"      ❌ Erro ao carregar lojas {arquivo}: {e}")
    
    print(f"\n📊 RESUMO UUIDs VIXEN:")
    print(f"   👥 Clientes com UUID: {len(uuids_encontrados['clientes'])}")
    print(f"   🏪 Lojas com UUID: {len(uuids_encontrados['lojas'])}")
    print(f"   📄 Arquivos processados: {len(uuids_encontrados['arquivos_processados'])}")
    
    return uuids_encontrados

def fazer_cruzamento_uuids(clientes_trans, uuids_vixen):
    """Faz cruzamento entre clientes Trans Financ e UUIDs VIXEN"""
    
    cruzamento = {
        'matches_encontrados': {},
        'clientes_sem_uuid': {},
        'estatisticas': {
            'total_clientes_trans': len(clientes_trans),
            'total_uuids_vixen': len(uuids_vixen['clientes']),
            'matches_diretos': 0,
            'clientes_orphaos': 0
        }
    }
    
    print(f"🔗 Fazendo cruzamento de {len(clientes_trans)} clientes Trans Financ")
    print(f"   com {len(uuids_vixen['clientes'])} UUIDs VIXEN")
    
    # Fazer match direto por ID
    for cliente_id, dados_trans in clientes_trans.items():
        if cliente_id in uuids_vixen['clientes']:
            # Match encontrado!
            uuid_info = uuids_vixen['clientes'][cliente_id]
            
            cruzamento['matches_encontrados'][cliente_id] = {
                'trans_financ': dados_trans,
                'vixen_uuid': uuid_info,
                'tipo_match': 'ID_DIRETO'
            }
            
            cruzamento['estatisticas']['matches_diretos'] += 1
        else:
            # Cliente sem UUID
            cruzamento['clientes_sem_uuid'][cliente_id] = dados_trans
            cruzamento['estatisticas']['clientes_orphaos'] += 1
    
    # Calcular estatísticas
    match_rate = (cruzamento['estatisticas']['matches_diretos'] / 
                 cruzamento['estatisticas']['total_clientes_trans']) * 100
    
    print(f"\n📊 RESULTADO DO CRUZAMENTO:")
    print(f"   ✅ Matches encontrados: {cruzamento['estatisticas']['matches_diretos']}")
    print(f"   ❌ Clientes sem UUID: {cruzamento['estatisticas']['clientes_orphaos']}")
    print(f"   📈 Taxa de match: {match_rate:.1f}%")
    
    return cruzamento

def salvar_integracao_uuids(resultado, pasta_destino):
    """Salva resultados da integração"""
    
    # 1. Salvar matches encontrados
    if resultado['matches_encontrados']:
        matches_data = []
        
        for cliente_id, match_info in resultado['matches_encontrados'].items():
            matches_data.append({
                'id_cliente': cliente_id,
                'uuid_cliente': match_info['vixen_uuid']['uuid'],
                'nome_trans_financ': match_info['trans_financ']['nome_cliente'],
                'nome_vixen': match_info['vixen_uuid']['nome'],
                'cpf_cnpj': match_info['trans_financ']['cpf_cnpj'],
                'total_transacoes': match_info['trans_financ']['total_transacoes'],
                'valor_total': match_info['trans_financ']['valor_total'],
                'primeira_transacao': match_info['trans_financ']['primeira_transacao'],
                'ultima_transacao': match_info['trans_financ']['ultima_transacao'],
                'arquivo_uuid_origem': match_info['vixen_uuid']['arquivo_origem']
            })
        
        df_matches = pd.DataFrame(matches_data)
        arquivo_matches = pasta_destino / "trans_financ_clientes_com_uuid.csv"
        df_matches.to_csv(arquivo_matches, index=False, encoding='utf-8')
        
        print(f"✅ Matches salvos: {arquivo_matches}")
        print(f"   📊 {len(matches_data)} clientes com UUID")
    
    # 2. Salvar clientes sem UUID
    if resultado['clientes_sem_uuid']:
        orphaos_data = []
        
        for cliente_id, dados in resultado['clientes_sem_uuid'].items():
            orphaos_data.append({
                'id_cliente': cliente_id,
                'nome_cliente': dados['nome_cliente'],
                'cpf_cnpj': dados['cpf_cnpj'],
                'total_transacoes': dados['total_transacoes'],
                'valor_total': dados['valor_total'],
                'primeira_transacao': dados['primeira_transacao'],
                'ultima_transacao': dados['ultima_transacao']
            })
        
        df_orphaos = pd.DataFrame(orphaos_data)
        arquivo_orphaos = pasta_destino / "trans_financ_clientes_sem_uuid.csv"
        df_orphaos.to_csv(arquivo_orphaos, index=False, encoding='utf-8')
        
        print(f"⚠️ Órfãos salvos: {arquivo_orphaos}")
        print(f"   📊 {len(orphaos_data)} clientes sem UUID")
    
    # 3. Salvar relatório completo
    relatorio = {
        'data_integracao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'estatisticas': resultado['estatisticas'],
        'resumo': {
            'matches_salvos': len(resultado['matches_encontrados']),
            'orphaos_salvos': len(resultado['clientes_sem_uuid']),
            'taxa_sucesso': (resultado['estatisticas']['matches_diretos'] / 
                           resultado['estatisticas']['total_clientes_trans']) * 100
        }
    }
    
    arquivo_relatorio = pasta_destino / "relatorio_integracao_uuids.json"
    
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"📊 Relatório salvo: {arquivo_relatorio}")

if __name__ == "__main__":
    resultado = integrar_trans_financ_vixen_uuids()
    
    print(f"\n🎉 INTEGRAÇÃO CONCLUÍDA!")
    print("=" * 30)
    print("✅ Cruzamento de UUIDs realizado")
    print("✅ Arquivos de integração criados")
    print("✅ Relatórios de análise salvos")
    print("🔗 Ligações iniciais estabelecidas!")