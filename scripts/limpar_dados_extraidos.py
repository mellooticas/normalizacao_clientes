#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpeza dos dados extraídos - Remove headers incorretos e valores inválidos
"""

import pandas as pd
import os
import json
from datetime import datetime
import shutil

def limpar_dados_extraidos():
    """Limpa todos os dados extraídos removendo headers e valores inválidos"""
    
    print("🧹 LIMPEZA DOS DADOS EXTRAÍDOS")
    print("=" * 50)
    
    # Pastas
    pasta_base = r"d:\projetos\carne_facil\carne_facil\data\originais\cxs\extraidos_por_tipo"
    pasta_backup = os.path.join(pasta_base, "_backup_antes_limpeza")
    pasta_analises = r"d:\projetos\carne_facil\carne_facil\_analises"
    
    os.makedirs(pasta_backup, exist_ok=True)
    os.makedirs(pasta_analises, exist_ok=True)
    
    # Definir padrões de limpeza por tipo de tabela
    padroes_limpeza = {
        'vendas': {
            'headers_invalidos': [
                'Cliente', 'Forma de Pgto', 'Valor Venda', 'Entrada', 'Valor Parcela',
                'Nº Venda', 'OS', 'Nº Parcela',
                "['Nº Venda', 'Cliente', 'Forma de Pgto', 'Valor Venda', 'Entrada']",
                "['OS', 'Cliente', 'Forma de Pgto', 'Valor Parcela', 'Nº Parcela']"
            ],
            'colunas_importantes': ['nn_venda', 'cliente', 'forma_de_pgto', 'valor_venda', 'entrada'],
            'validacoes': {
                'nn_venda': {'tipo': 'numerico', 'min': 1},
                'valor_venda': {'tipo': 'numerico', 'min': 0}
            }
        },
        'restante_entrada': {
            'headers_invalidos': [
                'Cliente', 'Forma de Pgto', 'Valor Parcela', 'OS', 'Nº Parcela',
                "['OS', 'Cliente', 'Forma de Pgto', 'Valor Parcela', 'Nº Parcela']",
                "['Coluna1', 'Coluna2', 'Coluna3', 'Coluna4', 'Coluna5']"
            ],
            'colunas_importantes': ['os', 'cliente', 'forma_de_pgto', 'valor_parcela'],
            'validacoes': {
                'valor_parcela': {'tipo': 'numerico', 'min': 0}
            }
        },
        'recebimento_carne': {
            'headers_invalidos': [
                'Cliente', 'Forma de Pgto', 'Valor Parcela', 'OS', 'Nº Parcela',
                "['OS', 'Cliente', 'Forma de Pgto', 'Valor Parcela', 'Nº Parcela']",
                "['Coluna1', 'Coluna2', 'Coluna3', 'Coluna4', 'Coluna5']"
            ],
            'colunas_importantes': ['os', 'cliente', 'forma_de_pgto', 'valor_parcela'],
            'validacoes': {
                'valor_parcela': {'tipo': 'numerico', 'min': 0}
            }
        },
        'os_entregues_dia': {
            'headers_invalidos': [
                'OS', 'Parcelas', 'Valor Total',
                "['OS', 'Parcelas', 'Valor Total']"
            ],
            'colunas_importantes': ['os', 'parcelas', 'valor_total'],
            'validacoes': {
                'valor_total': {'tipo': 'numerico', 'min': 0}
            }
        },
        'entrega_carne': {
            'headers_invalidos': [],
            'colunas_importantes': ['os'],
            'validacoes': {}
        }
    }
    
    relatorio_limpeza = {
        'timestamp': datetime.now().isoformat(),
        'tipos_processados': {},
        'estatisticas_gerais': {},
        'problemas_corrigidos': []
    }
    
    # Processar cada tipo de tabela
    tipos_tabela = [d for d in os.listdir(pasta_base) 
                   if os.path.isdir(os.path.join(pasta_base, d)) and not d.startswith('_')]
    
    for tipo in sorted(tipos_tabela):
        print(f"\n🧹 LIMPANDO: {tipo.upper()}")
        print("-" * 40)
        
        pasta_tipo = os.path.join(pasta_base, tipo)
        pasta_backup_tipo = os.path.join(pasta_backup, tipo)
        os.makedirs(pasta_backup_tipo, exist_ok=True)
        
        arquivos_csv = [f for f in os.listdir(pasta_tipo) if f.endswith('.csv')]
        
        if len(arquivos_csv) == 0:
            print("⚠️  Nenhum arquivo CSV encontrado")
            continue
        
        config_limpeza = padroes_limpeza.get(tipo, padroes_limpeza['entrega_carne'])
        
        tipo_info = {
            'arquivos_processados': 0,
            'registros_originais': 0,
            'registros_limpos': 0,
            'headers_removidos': 0,
            'problemas_corrigidos': []
        }
        
        for arquivo in sorted(arquivos_csv):
            caminho_arquivo = os.path.join(pasta_tipo, arquivo)
            caminho_backup = os.path.join(pasta_backup_tipo, arquivo)
            
            try:
                print(f"  📄 {arquivo}")
                
                # Fazer backup
                if not os.path.exists(caminho_backup):
                    shutil.copy2(caminho_arquivo, caminho_backup)
                
                # Ler dados
                df_original = pd.read_csv(caminho_arquivo)
                registros_originais = len(df_original)
                tipo_info['registros_originais'] += registros_originais
                
                # LIMPEZA 1: Remover headers como dados
                df_limpo = df_original.copy()
                headers_removidos = 0
                
                for coluna in df_limpo.columns:
                    if df_limpo[coluna].dtype == 'object':
                        # Remover valores que são headers
                        for header_invalido in config_limpeza['headers_invalidos']:
                            mask = df_limpo[coluna].astype(str).str.contains(header_invalido, regex=False, na=False)
                            if mask.any():
                                removidos = mask.sum()
                                headers_removidos += removidos
                                df_limpo = df_limpo[~mask]
                                print(f"    ✂️  Removidos {removidos} '{header_invalido}' de {coluna}")
                
                # LIMPEZA 2: Valores inválidos específicos
                valores_invalidos = ['*', 'Coluna3', '', ' ']
                for coluna in df_limpo.columns:
                    if df_limpo[coluna].dtype == 'object':
                        mask_invalidos = df_limpo[coluna].isin(valores_invalidos)
                        if mask_invalidos.any():
                            df_limpo.loc[mask_invalidos, coluna] = None
                
                # LIMPEZA 3: Validações específicas por tipo
                for coluna, regras in config_limpeza['validacoes'].items():
                    if coluna in df_limpo.columns:
                        if regras['tipo'] == 'numerico':
                            # Converter para numérico, colocando NaN em valores inválidos
                            df_limpo[coluna] = pd.to_numeric(df_limpo[coluna], errors='coerce')
                            
                            # Remover valores negativos se necessário
                            if 'min' in regras:
                                mask_negativo = df_limpo[coluna] < regras['min']
                                if mask_negativo.any():
                                    df_limpo.loc[mask_negativo, coluna] = None
                
                # LIMPEZA 4: Remover linhas completamente vazias
                df_limpo = df_limpo.dropna(how='all')
                
                # LIMPEZA 5: Remover duplicatas exatas
                duplicatas_antes = len(df_limpo)
                df_limpo = df_limpo.drop_duplicates()
                duplicatas_removidas = duplicatas_antes - len(df_limpo)
                
                registros_limpos = len(df_limpo)
                
                # Salvar arquivo limpo
                df_limpo.to_csv(caminho_arquivo, index=False)
                
                # Estatísticas
                tipo_info['arquivos_processados'] += 1
                tipo_info['registros_limpos'] += registros_limpos
                tipo_info['headers_removidos'] += headers_removidos
                
                redução = registros_originais - registros_limpos
                percentual_reducao = (redução / registros_originais * 100) if registros_originais > 0 else 0
                
                print(f"    📊 {registros_originais:,} → {registros_limpos:,} registros (-{redução:,}, -{percentual_reducao:.1f}%)")
                if headers_removidos > 0:
                    print(f"    🧹 {headers_removidos} headers removidos")
                if duplicatas_removidas > 0:
                    print(f"    🔄 {duplicatas_removidas} duplicatas removidas")
                
            except Exception as e:
                erro = f"Erro ao processar {arquivo}: {str(e)}"
                print(f"    ❌ {erro}")
                tipo_info['problemas_corrigidos'].append(erro)
        
        relatorio_limpeza['tipos_processados'][tipo] = tipo_info
        
        print(f"\n✅ {tipo.upper()} concluído:")
        print(f"   📄 {tipo_info['arquivos_processados']} arquivos processados")
        print(f"   📊 {tipo_info['registros_originais']:,} → {tipo_info['registros_limpos']:,} registros")
        print(f"   🧹 {tipo_info['headers_removidos']} headers inválidos removidos")
    
    # Estatísticas gerais
    total_arquivos = sum(info['arquivos_processados'] for info in relatorio_limpeza['tipos_processados'].values())
    total_originais = sum(info['registros_originais'] for info in relatorio_limpeza['tipos_processados'].values())
    total_limpos = sum(info['registros_limpos'] for info in relatorio_limpeza['tipos_processados'].values())
    total_headers_removidos = sum(info['headers_removidos'] for info in relatorio_limpeza['tipos_processados'].values())
    
    relatorio_limpeza['estatisticas_gerais'] = {
        'total_arquivos_processados': total_arquivos,
        'registros_antes_limpeza': total_originais,
        'registros_apos_limpeza': total_limpos,
        'registros_removidos': total_originais - total_limpos,
        'percentual_reducao': round((total_originais - total_limpos) / total_originais * 100, 2) if total_originais > 0 else 0,
        'headers_invalidos_removidos': total_headers_removidos
    }
    
    # Salvar relatório
    caminho_relatorio = os.path.join(pasta_analises, "relatorio_limpeza_dados.json")
    with open(caminho_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio_limpeza, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 LIMPEZA CONCLUÍDA!")
    print("=" * 50)
    print(f"📄 Arquivos processados: {total_arquivos}")
    print(f"📊 Registros: {total_originais:,} → {total_limpos:,} (-{total_originais - total_limpos:,})")
    print(f"🧹 Headers inválidos removidos: {total_headers_removidos:,}")
    print(f"💾 Backups salvos em: {pasta_backup}")
    print(f"📋 Relatório: {caminho_relatorio}")

if __name__ == "__main__":
    limpar_dados_extraidos()