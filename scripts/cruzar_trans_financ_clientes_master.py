#!/usr/bin/env python3
"""
Cruzamento Trans Financ com Clientes Master
Faz ligação entre clientes Trans Financ (ID.2) e clientes master VIXEN/OSS
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

def cruzar_trans_financ_clientes_master():
    """Cruza clientes Trans Financ com clientes master"""
    
    print("🔗 CRUZAMENTO TRANS FINANC ↔ CLIENTES MASTER")
    print("=" * 60)
    
    # Carregar dados Trans Financ
    pasta_trans = Path("data/originais/controles_gerais/trans_financ_final")
    
    # Carregar clientes master
    pasta_master = Path("data/originais/cruzamento_vixen_oss")
    
    print("📊 1. CARREGANDO CLIENTES TRANS FINANC")
    print("-" * 40)
    
    clientes_trans = carregar_clientes_trans_financ(pasta_trans)
    
    print("📊 2. CARREGANDO CLIENTES MASTER")
    print("-" * 35)
    
    clientes_master = carregar_clientes_master(pasta_master)
    
    print("🔗 3. FAZENDO CRUZAMENTO")
    print("-" * 25)
    
    resultado_cruzamento = fazer_cruzamento_master(clientes_trans, clientes_master)
    
    print("💾 4. SALVANDO RESULTADOS")
    print("-" * 25)
    
    salvar_cruzamento_master(resultado_cruzamento, pasta_trans)
    
    return resultado_cruzamento

def carregar_clientes_trans_financ(pasta_trans):
    """Carrega e analisa clientes do Trans Financ"""
    
    print("🔍 Analisando clientes Trans Financ...")
    
    clientes_consolidados = {}
    total_registros_analisados = 0
    
    # Processar todos os arquivos Trans Financ
    arquivos_trans = list(pasta_trans.glob("trans_financ_*.csv"))
    
    for arquivo in arquivos_trans:
        print(f"   📄 Processando: {arquivo.name}")
        
        try:
            df = pd.read_csv(arquivo, encoding='utf-8', low_memory=False)
            
            # Analisar clientes por ID.2
            if 'ID.2' in df.columns:
                for _, row in df.iterrows():
                    cliente_id = row.get('ID.2')
                    
                    if pd.notna(cliente_id) and cliente_id != 0:
                        cliente_id = int(cliente_id)
                        
                        if cliente_id not in clientes_consolidados:
                            clientes_consolidados[cliente_id] = {
                                'nome_trans': row.get('Cliente.1', ''),
                                'cpf_cnpj': row.get('CPF/CNPJ', ''),
                                'transacoes': [],
                                'total_transacoes': 0,
                                'valor_total': 0.0,
                                'arquivo_origem': []
                            }
                        
                        # Adicionar informações da transação
                        transacao = {
                            'origem': row.get('Origem', ''),
                            'valor': float(row.get('Vl.líquido', 0) or 0),
                            'data_emissao': row.get('Dh.emissão', ''),
                            'pagamento': row.get('Pagamento', ''),
                            'arquivo': arquivo.name
                        }
                        
                        clientes_consolidados[cliente_id]['transacoes'].append(transacao)
                        clientes_consolidados[cliente_id]['total_transacoes'] += 1
                        clientes_consolidados[cliente_id]['valor_total'] += transacao['valor']
                        
                        if arquivo.name not in clientes_consolidados[cliente_id]['arquivo_origem']:
                            clientes_consolidados[cliente_id]['arquivo_origem'].append(arquivo.name)
            
            total_registros_analisados += len(df)
            print(f"      ✅ {len(df):,} registros analisados")
            
        except Exception as e:
            print(f"      ❌ Erro: {e}")
    
    print(f"\n📊 RESUMO TRANS FINANC:")
    print(f"   👥 Clientes únicos: {len(clientes_consolidados)}")
    print(f"   📄 Total registros: {total_registros_analisados:,}")
    
    # Top 5 clientes por valor
    top_clientes = sorted(clientes_consolidados.items(), 
                         key=lambda x: x[1]['valor_total'], reverse=True)[:5]
    
    print(f"\n🏆 TOP 5 CLIENTES POR VALOR:")
    for i, (cliente_id, dados) in enumerate(top_clientes, 1):
        nome = str(dados['nome_trans'] or 'SEM NOME')
        valor = dados['valor_total']
        transacoes = dados['total_transacoes']
        print(f"   {i}. ID {cliente_id}: {nome[:25]} - R$ {valor:,.2f} ({transacoes} trans.)")
    
    return clientes_consolidados

def carregar_clientes_master(pasta_master):
    """Carrega clientes master do VIXEN/OSS"""
    
    print("🔍 Carregando clientes master...")
    
    clientes_master = {}
    
    # Arquivos clientes master
    arquivos_master = [
        "clientes_master_suzano.csv",
        "clientes_master_maua.csv"
    ]
    
    for arquivo_nome in arquivos_master:
        arquivo_path = pasta_master / arquivo_nome
        
        if arquivo_path.exists():
            print(f"   📄 Carregando: {arquivo_nome}")
            
            try:
                df = pd.read_csv(arquivo_path, encoding='utf-8')
                
                for _, row in df.iterrows():
                    cliente_id = row.get('ID')
                    
                    if pd.notna(cliente_id):
                        cliente_id = int(cliente_id)
                        
                        clientes_master[cliente_id] = {
                            'id': cliente_id,
                            'cliente_abrev': row.get('Cliente', ''),
                            'nome_completo': row.get('Nome Completo', ''),
                            'endereco': row.get('Endereço', ''),
                            'bairro': row.get('Bairro', ''),
                            'cidade': row.get('Cidade', ''),
                            'uf': row.get('UF', ''),
                            'cep': row.get('CEP', ''),
                            'fone': row.get('Fone', ''),
                            'email': row.get('E-mail', ''),
                            'vendedor': row.get('Vendedor', ''),
                            'como_conheceu': row.get('Como nos conheceu', ''),
                            'sexo': row.get('Sexo', ''),
                            'loja_id': row.get('loja_id', ''),
                            'loja_nome': row.get('loja_nome', ''),
                            'loja_uuid': row.get('loja_uuid', ''),
                            'canal_uuid': row.get('canal_uuid', ''),
                            'vendedor_uuid': row.get('vendedor_uuid', ''),
                            'tem_compra': row.get('tem_compra', False),
                            'total_compras': row.get('total_compras', 0),
                            'total_os': row.get('total_os', 0),
                            'data_compra': row.get('data_compra', ''),
                            'match_method': row.get('match_method', ''),
                            'confidence': row.get('confidence', ''),
                            'fonte_enriquecimento': row.get('fonte_enriquecimento', ''),
                            'arquivo_origem': arquivo_nome
                        }
                
                print(f"      ✅ {len(df)} clientes carregados")
                
            except Exception as e:
                print(f"      ❌ Erro ao carregar {arquivo_nome}: {e}")
        else:
            print(f"      ⚠️ Arquivo não encontrado: {arquivo_nome}")
    
    print(f"\n📊 RESUMO CLIENTES MASTER:")
    print(f"   👥 Total clientes: {len(clientes_master)}")
    
    # Análise por loja
    lojas_stats = {}
    for cliente in clientes_master.values():
        loja = cliente['loja_nome']
        if loja not in lojas_stats:
            lojas_stats[loja] = 0
        lojas_stats[loja] += 1
    
    print(f"   🏪 Distribuição por loja:")
    for loja, count in lojas_stats.items():
        print(f"      • {loja}: {count} clientes")
    
    return clientes_master

def fazer_cruzamento_master(clientes_trans, clientes_master):
    """Faz cruzamento entre Trans Financ e clientes master"""
    
    print(f"🔗 Cruzando {len(clientes_trans)} clientes Trans Financ")
    print(f"   com {len(clientes_master)} clientes master")
    
    resultado = {
        'matches_encontrados': {},
        'clientes_trans_orphaos': {},
        'clientes_master_sem_transacao': {},
        'estatisticas': {
            'total_trans_financ': len(clientes_trans),
            'total_master': len(clientes_master),
            'matches_diretos': 0,
            'trans_orphaos': 0,
            'master_sem_trans': 0
        }
    }
    
    # 1. Buscar matches diretos (mesmo ID)
    for trans_id, dados_trans in clientes_trans.items():
        if trans_id in clientes_master:
            # Match encontrado!
            dados_master = clientes_master[trans_id]
            
            resultado['matches_encontrados'][trans_id] = {
                'trans_financ': dados_trans,
                'cliente_master': dados_master,
                'tipo_match': 'ID_DIRETO'
            }
            
            resultado['estatisticas']['matches_diretos'] += 1
        else:
            # Cliente Trans Financ sem correspondente no master
            resultado['clientes_trans_orphaos'][trans_id] = dados_trans
            resultado['estatisticas']['trans_orphaos'] += 1
    
    # 2. Identificar clientes master sem transações financeiras
    for master_id, dados_master in clientes_master.items():
        if master_id not in clientes_trans:
            resultado['clientes_master_sem_transacao'][master_id] = dados_master
            resultado['estatisticas']['master_sem_trans'] += 1
    
    # Calcular estatísticas
    match_rate = (resultado['estatisticas']['matches_diretos'] / 
                 resultado['estatisticas']['total_trans_financ']) * 100
    
    cobertura_master = (resultado['estatisticas']['matches_diretos'] / 
                       resultado['estatisticas']['total_master']) * 100
    
    print(f"\n📊 RESULTADO DO CRUZAMENTO:")
    print(f"   ✅ Matches encontrados: {resultado['estatisticas']['matches_diretos']}")
    print(f"   ❌ Trans Financ órfãos: {resultado['estatisticas']['trans_orphaos']}")
    print(f"   📋 Master sem transação: {resultado['estatisticas']['master_sem_trans']}")
    print(f"   📈 Taxa de match Trans Financ: {match_rate:.1f}%")
    print(f"   📊 Cobertura do Master: {cobertura_master:.1f}%")
    
    return resultado

def salvar_cruzamento_master(resultado, pasta_destino):
    """Salva resultados do cruzamento"""
    
    # 1. Matches encontrados - dados integrados
    if resultado['matches_encontrados']:
        matches_data = []
        
        for cliente_id, match_info in resultado['matches_encontrados'].items():
            trans_data = match_info['trans_financ']
            master_data = match_info['cliente_master']
            
            # Preparar linha integrada
            linha_integrada = {
                # Identificação
                'id_cliente': cliente_id,
                'tipo_match': match_info['tipo_match'],
                
                # Dados Master (mais completos)
                'nome_completo': master_data['nome_completo'],
                'nome_abrev': master_data['cliente_abrev'],
                'endereco': master_data['endereco'],
                'bairro': master_data['bairro'],
                'cidade': master_data['cidade'],
                'uf': master_data['uf'],
                'cep': master_data['cep'],
                'fone': master_data['fone'],
                'email': master_data['email'],
                'sexo': master_data['sexo'],
                
                # Dados de Loja/UUIDs
                'loja_id': master_data['loja_id'],
                'loja_nome': master_data['loja_nome'],
                'loja_uuid': master_data['loja_uuid'],
                'vendedor': master_data['vendedor'],
                'vendedor_uuid': master_data['vendedor_uuid'],
                'canal_uuid': master_data['canal_uuid'],
                'como_conheceu': master_data['como_conheceu'],
                
                # Dados Financeiros (Trans Financ)
                'total_transacoes_financ': trans_data['total_transacoes'],
                'valor_total_financ': trans_data['valor_total'],
                'cpf_cnpj_financ': trans_data['cpf_cnpj'],
                'arquivos_financ': ';'.join(trans_data['arquivo_origem']),
                
                # Dados OSS (Master)
                'tem_compra_oss': master_data['tem_compra'],
                'total_compras_oss': master_data['total_compras'],
                'total_os': master_data['total_os'],
                'data_compra_oss': master_data['data_compra'],
                
                # Metadados
                'match_method_oss': master_data['match_method'],
                'confidence_oss': master_data['confidence'],
                'fonte_enriquecimento': master_data['fonte_enriquecimento'],
                'arquivo_master_origem': master_data['arquivo_origem']
            }
            
            matches_data.append(linha_integrada)
        
        # Salvar matches integrados
        df_matches = pd.DataFrame(matches_data)
        arquivo_matches = pasta_destino / "clientes_integrados_trans_financ_master.csv"
        df_matches.to_csv(arquivo_matches, index=False, encoding='utf-8')
        
        print(f"✅ Clientes integrados: {arquivo_matches}")
        print(f"   📊 {len(matches_data)} clientes com dados completos")
    
    # 2. Clientes Trans Financ órfãos
    if resultado['clientes_trans_orphaos']:
        orphaos_trans_data = []
        
        for cliente_id, dados in resultado['clientes_trans_orphaos'].items():
            orphaos_trans_data.append({
                'id_cliente': cliente_id,
                'nome_trans_financ': dados['nome_trans'],
                'cpf_cnpj': dados['cpf_cnpj'],
                'total_transacoes': dados['total_transacoes'],
                'valor_total': dados['valor_total'],
                'arquivos_origem': ';'.join(dados['arquivo_origem']),
                'observacao': 'Não encontrado no cadastro master VIXEN/OSS'
            })
        
        df_orphaos_trans = pd.DataFrame(orphaos_trans_data)
        arquivo_orphaos_trans = pasta_destino / "clientes_trans_financ_orphaos.csv"
        df_orphaos_trans.to_csv(arquivo_orphaos_trans, index=False, encoding='utf-8')
        
        print(f"⚠️ Trans Financ órfãos: {arquivo_orphaos_trans}")
        print(f"   📊 {len(orphaos_trans_data)} clientes sem cadastro master")
    
    # 3. Clientes master sem transações financeiras
    if resultado['clientes_master_sem_transacao']:
        master_sem_trans_data = []
        
        for cliente_id, dados in resultado['clientes_master_sem_transacao'].items():
            master_sem_trans_data.append({
                'id_cliente': cliente_id,
                'nome_completo': dados['nome_completo'],
                'loja_nome': dados['loja_nome'],
                'tem_compra_oss': dados['tem_compra'],
                'total_os': dados['total_os'],
                'data_compra': dados['data_compra'],
                'observacao': 'Cadastrado no master mas sem transações financeiras'
            })
        
        df_master_sem_trans = pd.DataFrame(master_sem_trans_data)
        arquivo_master_sem_trans = pasta_destino / "clientes_master_sem_transacoes_financ.csv"
        df_master_sem_trans.to_csv(arquivo_master_sem_trans, index=False, encoding='utf-8')
        
        print(f"📋 Master sem transações: {arquivo_master_sem_trans}")
        print(f"   📊 {len(master_sem_trans_data)} clientes master sem atividade financeira")
    
    # 4. Relatório completo
    relatorio = {
        'data_cruzamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'estatisticas_detalhadas': resultado['estatisticas'],
        'resumo_arquivos': {
            'clientes_integrados': len(resultado['matches_encontrados']),
            'trans_financ_orphaos': len(resultado['clientes_trans_orphaos']),
            'master_sem_transacoes': len(resultado['clientes_master_sem_transacao'])
        },
        'taxas_cobertura': {
            'match_rate_trans_financ': (resultado['estatisticas']['matches_diretos'] / 
                                       resultado['estatisticas']['total_trans_financ']) * 100,
            'cobertura_master': (resultado['estatisticas']['matches_diretos'] / 
                               resultado['estatisticas']['total_master']) * 100
        }
    }
    
    arquivo_relatorio = pasta_destino / "relatorio_cruzamento_trans_financ_master.json"
    
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"📊 Relatório detalhado: {arquivo_relatorio}")

if __name__ == "__main__":
    resultado = cruzar_trans_financ_clientes_master()
    
    print(f"\n🎉 CRUZAMENTO CONCLUÍDO!")
    print("=" * 30)
    print("✅ Ligação Trans Financ ↔ Clientes Master realizada")
    print("✅ Dados integrados com UUIDs de loja/vendedor/canal")
    print("✅ Análise de cobertura completada")
    print("🔗 Base unificada para controle no banco criada!")