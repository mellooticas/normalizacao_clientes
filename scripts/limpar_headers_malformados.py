#!/usr/bin/env python3
"""
LIMPEZA ESPECÍFICA - HEADERS MALFORMADOS
================================================================
Corrige os headers malformados encontrados no ENTREGA_CARNE SUZANO
================================================================
"""

import os

def limpar_headers_malformados():
    """Limpa headers malformados específicos encontrados"""
    
    print("🧹 LIMPANDO HEADERS MALFORMADOS")
    print("=" * 50)
    
    arquivo = "data/originais/cxs/extraidos_corrigidos/entrega_carne/entrega_carne_suzano_com_uuids_enriquecido_completo.csv"
    
    if os.path.exists(arquivo):
        print(f"📁 Processando: {arquivo}")
        
        # Ler arquivo
        with open(arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        print(f"📊 Linhas originais: {len(linhas)}")
        
        # Identificar header original
        header_original = linhas[0].strip()
        print(f"📋 Header: {header_original[:50]}...")
        
        linhas_limpas = [linhas[0]]  # Manter header original
        problemas_removidos = 0
        
        for i, linha in enumerate(linhas[1:], 1):
            linha_limpa = linha.strip()
            
            # Verificar se é header malformado
            if 'OS,Parcelas,Valor Total' in linha_limpa:
                print(f"❌ Removendo linha {i + 1}: {linha_limpa[:80]}...")
                problemas_removidos += 1
            else:
                linhas_limpas.append(linha)
        
        # Salvar arquivo limpo
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.writelines(linhas_limpas)
        
        print(f"✅ Arquivo limpo!")
        print(f"📊 Linhas finais: {len(linhas_limpas)}")
        print(f"🗑️ Problemas removidos: {problemas_removidos}")
        
        return problemas_removidos
    else:
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return 0

def verificar_outros_arquivos():
    """Verifica se há problemas similares em outros arquivos"""
    
    print(f"\n🔍 VERIFICANDO OUTROS ARQUIVOS")
    print("-" * 50)
    
    base_dir = "data/originais/cxs/extraidos_corrigidos"
    tabelas = ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano', 'suzano2']
    
    total_problemas = 0
    
    for tabela in tabelas:
        for loja in lojas:
            arquivo = f"{base_dir}/{tabela}/{tabela}_{loja}_com_uuids_enriquecido_completo.csv"
            
            if os.path.exists(arquivo) and not (tabela == 'entrega_carne' and loja == 'suzano'):
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    
                    # Verificar padrões de headers malformados
                    padroes_suspeitos = [
                        'OS,Parcelas,Valor Total',
                        'nn_venda,cliente,forma_de_pgto',
                        'os,vendedor,carne'
                    ]
                    
                    for padrao in padroes_suspeitos:
                        if padrao in conteudo:
                            print(f"⚠️ {tabela}_{loja}: Contém '{padrao}'")
                            total_problemas += 1
                            
                except Exception as e:
                    print(f"❌ Erro ao verificar {tabela}_{loja}: {e}")
    
    if total_problemas == 0:
        print("✅ Nenhum outro problema encontrado!")
    
    return total_problemas

if __name__ == "__main__":
    removidos = limpar_headers_malformados()
    outros_problemas = verificar_outros_arquivos()
    
    print(f"\n📋 RESUMO DA LIMPEZA")
    print("=" * 50)
    print(f"🗑️ Headers malformados removidos: {removidos}")
    print(f"⚠️ Outros problemas encontrados: {outros_problemas}")
    
    if removidos > 0:
        print(f"\n✅ LIMPEZA CONCLUÍDA!")
        print(f"🎯 Arquivo ENTREGA_CARNE SUZANO agora está limpo")
        print(f"🚀 Pronto para gerar arquivos finais novamente")
    else:
        print(f"\n⚠️ Nenhuma limpeza foi necessária")