#!/usr/bin/env python3
"""
Gerar Arquivos Finais para Banco - VERSÃO FINAL CORRIGIDA
=========================================================

Gera arquivos finais limpos das 5 tabelas essenciais para upload no banco:
1. vendas
2. restante_entrada  
3. recebimento_carne
4. os_entregues_dia (com vendedores)
5. entrega_carne

Remove colunas desnecessárias e mantém apenas dados essenciais para o banco.
"""

import pandas as pd
import os
from pathlib import Path
import glob

def processar_tabela_vendas(df):
    """Processa tabela VENDAS mantendo apenas colunas essenciais"""
    colunas_essenciais = [
        'nn_venda', 'cliente', 'forma_de_pgto', 'valor_venda', 'entrada', 
        'data_movimento', 'loja_id', 'loja_nome'
    ]
    
    return df[colunas_essenciais].copy()

def processar_tabela_restante_entrada(df):
    """Processa tabela RESTANTE_ENTRADA mantendo apenas colunas essenciais"""
    colunas_essenciais = [
        'nn_venda', 'cliente', 'forma_de_pgto', 'valor_venda', 'entrada',
        'data_movimento', 'loja_id', 'loja_nome'
    ]
    
    return df[colunas_essenciais].copy()

def processar_tabela_recebimento_carne(df):
    """Processa tabela RECEBIMENTO_CARNE mantendo apenas colunas essenciais"""
    colunas_essenciais = [
        'os', 'cliente', 'forma_de_pgto', 'valor_parcela', 'nn_parcela',
        'data_movimento', 'loja_id', 'loja_nome'
    ]
    
    return df[colunas_essenciais].copy()

def processar_tabela_os_entregues_dia(df):
    """Processa tabela OS_ENTREGUES_DIA mantendo colunas essenciais + vendedores"""
    colunas_essenciais = [
        'os', 'vendedor', 'carne', 'os_numero',
        'data_movimento', 'loja_id', 'loja_nome',
        'vendedor_uuid', 'vendedor_nome_normalizado',
        'canal_captacao_uuid', 'canal_captacao_nome'
    ]
    
    return df[colunas_essenciais].copy()

def processar_tabela_entrega_carne(df):
    """Processa tabela ENTREGA_CARNE mantendo apenas colunas essenciais"""
    colunas_essenciais = [
        'os', 'parcelas', 'valor_total',
        'data_movimento', 'loja_id', 'loja_nome'
    ]
    
    return df[colunas_essenciais].copy()

def main():
    # Diretórios
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    origem_dir = base_dir / "data" / "originais" / "cxs" / "extraidos_corrigidos"
    destino_dir = base_dir / "data" / "finais_banco"
    
    # Criar diretório de destino
    destino_dir.mkdir(parents=True, exist_ok=True)
    
    # Limpar arquivos antigos
    for arquivo_antigo in destino_dir.glob("*.csv"):
        arquivo_antigo.unlink()
    
    # Definir tabelas e suas funções de processamento
    processadores = {
        'vendas': processar_tabela_vendas,
        'restante_entrada': processar_tabela_restante_entrada,
        'recebimento_carne': processar_tabela_recebimento_carne,
        'os_entregues_dia': processar_tabela_os_entregues_dia,
        'entrega_carne': processar_tabela_entrega_carne
    }
    
    # Lojas
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano', 'suzano2']
    
    print("🏭 GERANDO ARQUIVOS FINAIS PARA BANCO")
    print("=" * 50)
    
    total_registros = 0
    arquivos_gerados = 0
    resumo_por_tabela = {}
    
    for tabela, processador in processadores.items():
        print(f"\n📊 Processando tabela: {tabela.upper()}")
        
        registros_tabela = 0
        lojas_processadas = []
        
        for loja in lojas:
            # Buscar arquivo da tabela para a loja
            pattern = f"{tabela}_{loja}_com_uuids_enriquecido_completo.csv"
            arquivo_origem = origem_dir / tabela / pattern
            
            if arquivo_origem.exists():
                try:
                    # Carregar dados
                    df = pd.read_csv(arquivo_origem)
                    print(f"   {loja.upper()}: {len(df):,} registros")
                    
                    # Processar dados
                    df_processado = processador(df)
                    
                    # Salvar arquivo final
                    arquivo_final = destino_dir / f"{tabela}_{loja}_final.csv"
                    df_processado.to_csv(arquivo_final, index=False)
                    
                    registros_tabela += len(df_processado)
                    arquivos_gerados += 1
                    lojas_processadas.append(loja)
                    
                except Exception as e:
                    print(f"   ❌ ERRO {loja.upper()}: {e}")
            else:
                print(f"   ⚠️  {loja.upper()}: Arquivo não encontrado")
        
        print(f"   ✅ Total {tabela.upper()}: {registros_tabela:,} registros")
        total_registros += registros_tabela
        resumo_por_tabela[tabela] = {
            'registros': registros_tabela,
            'lojas': lojas_processadas
        }
    
    print(f"\n🎯 RESUMO FINAL")
    print(f"   📁 Arquivos gerados: {arquivos_gerados}")
    print(f"   📊 Total de registros: {total_registros:,}")
    print(f"   📂 Destino: {destino_dir}")
    
    print(f"\n📋 RESUMO POR TABELA:")
    for tabela, info in resumo_por_tabela.items():
        print(f"   🔹 {tabela.upper()}: {info['registros']:,} registros em {len(info['lojas'])} lojas")
    
    # Listar arquivos gerados
    print(f"\n📄 ARQUIVOS GERADOS:")
    arquivos_finais = sorted(destino_dir.glob("*_final.csv"))
    for arquivo in arquivos_finais:
        try:
            df_check = pd.read_csv(arquivo)
            print(f"   ✅ {arquivo.name}: {len(df_check):,} registros")
        except:
            print(f"   ❌ {arquivo.name}: ERRO ao verificar")
    
    print(f"\n🚀 ARQUIVOS PRONTOS PARA UPLOAD NO BANCO!")

if __name__ == "__main__":
    main()