#!/usr/bin/env python3
"""
ANALISADOR DE PROBLEMAS DE HEADER E LIMPEZA
================================================================
Analisa problemas de headers duplicados, dados malformados e
outras questões de limpeza nos arquivos processados.
================================================================
"""

import pandas as pd
import os

def analisar_problemas_limpeza():
    """Analisa problemas de limpeza em todas as tabelas"""
    
    print("🔍 ANÁLISE COMPLETA DE PROBLEMAS DE LIMPEZA")
    print("=" * 60)
    
    base_dir = "data/originais/cxs/extraidos_corrigidos"
    tabelas = ['vendas', 'restante_entrada', 'recebimento_carne', 'os_entregues_dia', 'entrega_carne']
    lojas = ['maua', 'perus', 'rio_pequeno', 'sao_mateus', 'suzano', 'suzano2']
    
    problemas_encontrados = {}
    
    for tabela in tabelas:
        print(f"\n📋 ANALISANDO TABELA: {tabela.upper()}")
        print("-" * 50)
        
        problemas_tabela = {}
        
        for loja in lojas:
            arquivo = f"{base_dir}/{tabela}/{tabela}_{loja}_com_uuids_enriquecido_completo.csv"
            
            if os.path.exists(arquivo):
                try:
                    # Ler arquivo como texto primeiro
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        linhas = f.readlines()
                    
                    print(f"\n🏪 {loja.upper()}: {len(linhas)} linhas totais")
                    
                    problemas_loja = {
                        'headers_duplicados': [],
                        'linhas_vazias': 0,
                        'dados_malformados': [],
                        'valores_suspeitos': []
                    }
                    
                    # Verificar header duplicado
                    header_original = linhas[0].strip() if linhas else ""
                    
                    for i, linha in enumerate(linhas[1:], 1):
                        linha_limpa = linha.strip()
                        
                        # Verificar se é header duplicado
                        if linha_limpa == header_original:
                            problemas_loja['headers_duplicados'].append(i + 1)
                            print(f"   ❌ Header duplicado na linha {i + 1}")
                        
                        # Verificar linhas vazias
                        if not linha_limpa:
                            problemas_loja['linhas_vazias'] += 1
                        
                        # Verificar dados malformados (como o exemplo que você mostrou)
                        if linha_limpa and ('OS,Parcelas,Valor Total' in linha_limpa or 
                                          'nn_venda,cliente,forma_de_pgto' in linha_limpa or
                                          'os,vendedor,carne' in linha_limpa):
                            problemas_loja['dados_malformados'].append(i + 1)
                            print(f"   ❌ Dados malformados na linha {i + 1}: {linha_limpa[:100]}...")
                    
                    # Ler como DataFrame para análise estrutural
                    df = pd.read_csv(arquivo)
                    
                    # Verificar valores suspeitos
                    if tabela == 'entrega_carne':
                        # Procurar por valores que são na verdade headers
                        if 'os' in df.columns:
                            valores_os = df['os'].astype(str)
                            headers_como_dados = valores_os[valores_os.str.contains('OS,Parcelas', na=False)]
                            if not headers_como_dados.empty:
                                problemas_loja['valores_suspeitos'].extend(headers_como_dados.index.tolist())
                                print(f"   ⚠️ {len(headers_como_dados)} registros com headers como dados")
                    
                    # Verificar inconsistências de colunas
                    colunas_esperadas = {
                        'vendas': ['nn_venda', 'cliente', 'forma_de_pgto'],
                        'restante_entrada': ['nn_venda', 'cliente', 'forma_de_pgto'],
                        'recebimento_carne': ['os', 'cliente', 'forma_de_pgto'],
                        'os_entregues_dia': ['os', 'vendedor', 'carne'],
                        'entrega_carne': ['os', 'parcelas', 'valor_total']
                    }
                    
                    if tabela in colunas_esperadas:
                        esperadas = colunas_esperadas[tabela]
                        faltando = [col for col in esperadas if col not in df.columns]
                        if faltando:
                            print(f"   ⚠️ Colunas faltando: {faltando}")
                    
                    # Estatísticas
                    total_problemas = (len(problemas_loja['headers_duplicados']) + 
                                     problemas_loja['linhas_vazias'] + 
                                     len(problemas_loja['dados_malformados']) +
                                     len(problemas_loja['valores_suspeitos']))
                    
                    print(f"   📊 Registros válidos: {len(df)}")
                    print(f"   ❌ Total de problemas: {total_problemas}")
                    
                    if total_problemas > 0:
                        problemas_tabela[loja] = problemas_loja
                    else:
                        print(f"   ✅ Arquivo limpo!")
                        
                except Exception as e:
                    print(f"   ❌ Erro ao analisar: {e}")
            else:
                print(f"   ⚠️ Arquivo não encontrado")
        
        if problemas_tabela:
            problemas_encontrados[tabela] = problemas_tabela
    
    # Relatório consolidado
    print(f"\n📋 RELATÓRIO CONSOLIDADO DE PROBLEMAS")
    print("=" * 60)
    
    if problemas_encontrados:
        for tabela, lojas_prob in problemas_encontrados.items():
            print(f"\n📋 {tabela.upper()}:")
            for loja, problemas in lojas_prob.items():
                print(f"   🏪 {loja}:")
                if problemas['headers_duplicados']:
                    print(f"      ❌ Headers duplicados: {len(problemas['headers_duplicados'])} linhas")
                if problemas['linhas_vazias'] > 0:
                    print(f"      ⚠️ Linhas vazias: {problemas['linhas_vazias']}")
                if problemas['dados_malformados']:
                    print(f"      ❌ Dados malformados: {len(problemas['dados_malformados'])} linhas")
                if problemas['valores_suspeitos']:
                    print(f"      ⚠️ Valores suspeitos: {len(problemas['valores_suspeitos'])} registros")
    else:
        print("✅ Nenhum problema de limpeza encontrado!")
    
    return problemas_encontrados

def gerar_script_limpeza(problemas):
    """Gera script para corrigir os problemas encontrados"""
    
    if not problemas:
        print("\n✅ Nenhuma limpeza necessária!")
        return
    
    print(f"\n🧹 GERANDO SCRIPT DE LIMPEZA")
    print("-" * 50)
    
    script_content = '''#!/usr/bin/env python3
"""
SCRIPT DE LIMPEZA AUTOMÁTICA
================================================================
Corrige problemas de headers duplicados e dados malformados
identificados na análise.
================================================================
"""

import pandas as pd
import os

def limpar_arquivos_problematicos():
    """Limpa arquivos com problemas identificados"""
    
    print("🧹 EXECUTANDO LIMPEZA AUTOMÁTICA")
    print("=" * 50)
    
    base_dir = "data/originais/cxs/extraidos_corrigidos"
'''
    
    for tabela, lojas_prob in problemas.items():
        for loja, problemas_loja in lojas_prob.items():
            script_content += f'''
    # Limpar {tabela}_{loja}
    arquivo = f"{base_dir}/{tabela}/{tabela}_{loja}_com_uuids_enriquecido_completo.csv"
    if os.path.exists(arquivo):
        print(f"🧹 Limpando {tabela}_{loja}...")
        
        # Ler arquivo linha por linha
        with open(arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        linhas_limpas = []
        header = linhas[0].strip()
        linhas_limpas.append(header + '\\n')
        
        for i, linha in enumerate(linhas[1:], 1):
            linha_limpa = linha.strip()
            
            # Pular headers duplicados e linhas vazias
            if linha_limpa and linha_limpa != header:
                # Verificar se não é dado malformado
                if not any(x in linha_limpa for x in ['OS,Parcelas,Valor Total', 'nn_venda,cliente,forma_de_pgto', 'os,vendedor,carne']):
                    linhas_limpas.append(linha)
        
        # Salvar arquivo limpo
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.writelines(linhas_limpas)
        
        print(f"   ✅ {tabela}_{loja}: {len(linhas)} → {len(linhas_limpas)} linhas")
'''
    
    script_content += '''

if __name__ == "__main__":
    limpar_arquivos_problematicos()
    print("\\n✅ LIMPEZA CONCLUÍDA!")
'''
    
    with open('limpar_problemas_automatico.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("📄 Script gerado: limpar_problemas_automatico.py")
    print("🚀 Execute: python limpar_problemas_automatico.py")

if __name__ == "__main__":
    problemas = analisar_problemas_limpeza()
    gerar_script_limpeza(problemas)