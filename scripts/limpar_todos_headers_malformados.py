#!/usr/bin/env python3
"""
LIMPEZA COMPLETA - TODOS OS HEADERS MALFORMADOS
================================================================
Remove todos os headers malformados encontrados em todas as tabelas
================================================================
"""

import os

def limpar_todos_headers_malformados():
    """Limpa headers malformados em todos os arquivos"""
    
    print("🧹 LIMPEZA COMPLETA DE HEADERS MALFORMADOS")
    print("=" * 60)
    
    base_dir = "data/originais/cxs/extraidos_corrigidos"
    tabelas = ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano', 'suzano2']
    
    # Padrões de headers malformados por tabela
    padroes_malformados = {
        'vendas': ['nn_venda,cliente,forma_de_pgto'],
        'restante_entrada': ['nn_venda,cliente,forma_de_pgto'],
        'recebimento_carne': ['os,cliente,forma_de_pgto'],
        'os_entregues_dia': ['os,vendedor,carne'],
        'entrega_carne': ['OS,Parcelas,Valor Total', 'os,parcelas,valor_total']
    }
    
    total_removidos_geral = 0
    resumo_por_tabela = {}
    
    for tabela in tabelas:
        print(f"\n📋 LIMPANDO TABELA: {tabela.upper()}")
        print("-" * 50)
        
        padroes_tabela = padroes_malformados.get(tabela, [])
        total_removidos_tabela = 0
        
        for loja in lojas:
            arquivo = f"{base_dir}/{tabela}/{tabela}_{loja}_com_uuids_enriquecido_completo.csv"
            
            if os.path.exists(arquivo):
                try:
                    # Ler arquivo
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        linhas = f.readlines()
                    
                    linhas_originais = len(linhas)
                    linhas_limpas = [linhas[0]]  # Manter header
                    removidos_loja = 0
                    
                    # Processar cada linha
                    for i, linha in enumerate(linhas[1:], 1):
                        linha_limpa = linha.strip()
                        
                        # Verificar se contém algum padrão malformado
                        eh_malformado = False
                        for padrao in padroes_tabela:
                            if padrao in linha_limpa:
                                eh_malformado = True
                                break
                        
                        if eh_malformado:
                            removidos_loja += 1
                        else:
                            linhas_limpas.append(linha)
                    
                    # Salvar apenas se houve mudanças
                    if removidos_loja > 0:
                        with open(arquivo, 'w', encoding='utf-8') as f:
                            f.writelines(linhas_limpas)
                        
                        print(f"🏪 {loja}: {removidos_loja} linhas removidas ({linhas_originais} → {len(linhas_limpas)})")
                        total_removidos_tabela += removidos_loja
                        total_removidos_geral += removidos_loja
                    else:
                        print(f"🏪 {loja}: ✅ Já limpo")
                        
                except Exception as e:
                    print(f"🏪 {loja}: ❌ Erro - {e}")
            else:
                print(f"🏪 {loja}: ⚠️ Arquivo não encontrado")
        
        if total_removidos_tabela > 0:
            resumo_por_tabela[tabela] = total_removidos_tabela
            print(f"📊 Total {tabela}: {total_removidos_tabela} headers malformados removidos")
        else:
            print(f"📊 Total {tabela}: ✅ Nenhuma limpeza necessária")
    
    # Relatório final
    print(f"\n📋 RELATÓRIO FINAL DE LIMPEZA")
    print("=" * 60)
    print(f"🗑️ Total geral removido: {total_removidos_geral} headers malformados")
    
    if resumo_por_tabela:
        print(f"\n📊 Detalhes por tabela:")
        for tabela, total in resumo_por_tabela.items():
            print(f"   📋 {tabela}: {total} headers")
    
    return total_removidos_geral

def verificar_limpeza():
    """Verifica se a limpeza foi bem-sucedida"""
    
    print(f"\n🔍 VERIFICANDO LIMPEZA")
    print("-" * 50)
    
    base_dir = "data/originais/cxs/extraidos_corrigidos"
    tabelas = ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano', 'suzano2']
    
    problemas_restantes = 0
    
    for tabela in tabelas:
        for loja in lojas:
            arquivo = f"{base_dir}/{tabela}/{tabela}_{loja}_com_uuids_enriquecido_completo.csv"
            
            if os.path.exists(arquivo):
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    
                    # Verificar padrões suspeitos
                    padroes_suspeitos = [
                        'nn_venda,cliente,forma_de_pgto',
                        'os,vendedor,carne',
                        'OS,Parcelas,Valor Total',
                        'os,parcelas,valor_total',
                        'os,cliente,forma_de_pgto'
                    ]
                    
                    for padrao in padroes_suspeitos:
                        if padrao in conteudo:
                            print(f"⚠️ {tabela}_{loja}: Ainda contém '{padrao}'")
                            problemas_restantes += 1
                            
                except Exception as e:
                    print(f"❌ Erro ao verificar {tabela}_{loja}: {e}")
    
    if problemas_restantes == 0:
        print("✅ TODOS OS ARQUIVOS ESTÃO LIMPOS!")
    else:
        print(f"⚠️ {problemas_restantes} problemas ainda encontrados")
    
    return problemas_restantes

if __name__ == "__main__":
    total_removidos = limpar_todos_headers_malformados()
    problemas_restantes = verificar_limpeza()
    
    print(f"\n🎯 RESUMO FINAL")
    print("=" * 60)
    
    if total_removidos > 0:
        print(f"✅ LIMPEZA CONCLUÍDA!")
        print(f"🗑️ {total_removidos} headers malformados removidos")
        
        if problemas_restantes == 0:
            print(f"🎉 TODOS OS ARQUIVOS AGORA ESTÃO LIMPOS!")
            print(f"🚀 Pronto para gerar arquivos finais corretos")
        else:
            print(f"⚠️ {problemas_restantes} problemas ainda precisam ser investigados")
    else:
        print(f"ℹ️ Nenhuma limpeza foi necessária")