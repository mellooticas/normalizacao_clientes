#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import re
from difflib import SequenceMatcher

def analise_final_cruzamento():
    """Análise final completa para estratégia de cruzamento VIXEN x OSS"""
    
    print('🎯 ANÁLISE FINAL - ESTRATÉGIA DE CRUZAMENTO VIXEN x OSS')
    print('=' * 70)
    
    # Carregar dados
    vixen_maua = pd.read_csv('data/originais/cruzamento_vixen_oss/clientes_vixen_maua_original.csv')
    oss_maua = pd.read_csv('data/originais/cruzamento_vixen_oss/oss_maua_original.csv')
    vixen_suzano = pd.read_csv('data/originais/cruzamento_vixen_oss/clientes_vixen_suzano_original.csv')
    oss_suzano = pd.read_csv('data/originais/cruzamento_vixen_oss/oss_suzano_original.csv')
    
    print('📊 RESUMO DOS DADOS:')
    print('-' * 40)
    print(f'VIXEN MAUA: {len(vixen_maua)} clientes')
    print(f'OSS MAUA: {len(oss_maua)} OS')
    print(f'VIXEN SUZANO: {len(vixen_suzano)} clientes')
    print(f'OSS SUZANO: {len(oss_suzano)} OS')
    
    def analisar_qualidade_campos(df_vixen, df_oss, loja):
        print(f'\n🏪 QUALIDADE DOS CAMPOS - {loja}:')
        print('-' * 30)
        
        # VIXEN
        nome_vixen = df_vixen['Nome Completo'].notna().sum()
        email_vixen = df_vixen['E-mail'].notna().sum()
        fone_vixen = df_vixen['Fone'].notna().sum()
        endereco_vixen = df_vixen['Endereço'].notna().sum()
        
        # OSS
        nome_oss = df_oss['NOME:'].notna().sum()
        email_oss = df_oss['EMAIL:'].notna().sum()
        celular_oss = df_oss['CELULAR:'].notna().sum()
        cpf_oss = df_oss['CPF'].notna().sum()
        endereco_oss = df_oss['END:'].notna().sum()
        
        print(f'📋 VIXEN ({len(df_vixen)} registros):')
        print(f'   👤 Nome: {nome_vixen} ({(nome_vixen/len(df_vixen))*100:.1f}%)')
        print(f'   📧 Email: {email_vixen} ({(email_vixen/len(df_vixen))*100:.1f}%)')
        print(f'   📞 Telefone: {fone_vixen} ({(fone_vixen/len(df_vixen))*100:.1f}%)')
        print(f'   🏠 Endereço: {endereco_vixen} ({(endereco_vixen/len(df_vixen))*100:.1f}%)')
        
        print(f'📋 OSS ({len(df_oss)} registros):')
        print(f'   👤 Nome: {nome_oss} ({(nome_oss/len(df_oss))*100:.1f}%)')
        print(f'   📧 Email: {email_oss} ({(email_oss/len(df_oss))*100:.1f}%)')
        print(f'   📞 Celular: {celular_oss} ({(celular_oss/len(df_oss))*100:.1f}%)')
        print(f'   🆔 CPF: {cpf_oss} ({(cpf_oss/len(df_oss))*100:.1f}%)')
        print(f'   🏠 Endereço: {endereco_oss} ({(endereco_oss/len(df_oss))*100:.1f}%)')
        
        return {
            'vixen_nome': nome_vixen,
            'vixen_email': email_vixen,
            'vixen_fone': fone_vixen,
            'oss_nome': nome_oss,
            'oss_email': email_oss,
            'oss_celular': celular_oss,
            'oss_cpf': cpf_oss
        }
    
    # Analisar qualidade por loja
    maua_stats = analisar_qualidade_campos(vixen_maua, oss_maua, 'MAUA')
    suzano_stats = analisar_qualidade_campos(vixen_suzano, oss_suzano, 'SUZANO')
    
    print(f'\n🎯 ESTRATÉGIAS DE CRUZAMENTO RECOMENDADAS:')
    print('=' * 50)
    
    def normalizar_email(email):
        if pd.isna(email) or email == '':
            return None
        return str(email).lower().strip()
    
    def normalizar_telefone(fone):
        if pd.isna(fone) or fone == '':
            return None
        # Extrair apenas números
        numeros = re.sub(r'[^0-9]', '', str(fone))
        # Pegar últimos 8-9 dígitos
        if len(numeros) >= 8:
            return numeros[-9:] if len(numeros) >= 11 else numeros[-8:]
        return None
    
    def normalizar_nome(nome):
        if pd.isna(nome) or nome == '':
            return None
        # Remover acentos, espaços extras, maiúscula
        nome_limpo = str(nome).upper().strip()
        nome_limpo = re.sub(r'[^A-Z\s]', '', nome_limpo)
        nome_limpo = re.sub(r'\s+', ' ', nome_limpo)
        return nome_limpo
    
    # Testar cruzamentos
    def testar_cruzamentos(df_vixen, df_oss, loja):
        print(f'\n🔍 TESTE DE CRUZAMENTOS - {loja}:')
        
        # 1. Por Email
        emails_vixen = set(filter(None, df_vixen['E-mail'].apply(normalizar_email)))
        emails_oss = set(filter(None, df_oss['EMAIL:'].apply(normalizar_email)))
        match_email = emails_vixen.intersection(emails_oss)
        
        # 2. Por Telefone
        fones_vixen = set(filter(None, df_vixen['Fone'].apply(normalizar_telefone)))
        fones_oss = set(filter(None, df_oss['CELULAR:'].apply(normalizar_telefone)))
        match_fone = fones_vixen.intersection(fones_oss)
        
        # 3. Por Nome
        nomes_vixen = set(filter(None, df_vixen['Nome Completo'].apply(normalizar_nome)))
        nomes_oss = set(filter(None, df_oss['NOME:'].apply(normalizar_nome)))
        match_nome = nomes_vixen.intersection(nomes_oss)
        
        print(f'   📧 Email: {len(match_email)} matches')
        print(f'   📞 Telefone: {len(match_fone)} matches')
        print(f'   👤 Nome: {len(match_nome)} matches')
        
        # Mostrar exemplos
        if match_email:
            print(f'      📧 Exemplo email: {list(match_email)[0]}')
        if match_fone:
            print(f'      📞 Exemplo telefone: {list(match_fone)[0]}')
        if match_nome:
            print(f'      👤 Exemplo nome: {list(match_nome)[0][:40]}...')
        
        return len(match_email), len(match_fone), len(match_nome)
    
    # Testar para ambas as lojas
    maua_email, maua_fone, maua_nome = testar_cruzamentos(vixen_maua, oss_maua, 'MAUA')
    suzano_email, suzano_fone, suzano_nome = testar_cruzamentos(vixen_suzano, oss_suzano, 'SUZANO')
    
    print(f'\n📊 RESUMO DOS MATCHES:')
    print('=' * 40)
    print(f'🏪 MAUA:')
    print(f'   📧 Email: {maua_email} matches')
    print(f'   📞 Telefone: {maua_fone} matches')
    print(f'   👤 Nome: {maua_nome} matches')
    
    print(f'🏪 SUZANO:')
    print(f'   📧 Email: {suzano_email} matches')
    print(f'   📞 Telefone: {suzano_fone} matches')
    print(f'   👤 Nome: {suzano_nome} matches')
    
    total_matches = maua_email + maua_fone + maua_nome + suzano_email + suzano_fone + suzano_nome
    
    print(f'\n🎯 CONCLUSÕES E PRÓXIMOS PASSOS:')
    print('=' * 50)
    print(f'✅ Total de matches identificados: {total_matches}')
    
    if total_matches > 0:
        print(f'🚀 ESTRATÉGIA RECOMENDADA:')
        print(f'   1️⃣ Implementar cruzamento em cascata')
        print(f'   2️⃣ Prioridade: Email → Telefone → Nome')
        print(f'   3️⃣ Criar tabela de relacionamentos')
        print(f'   4️⃣ Implementar fuzzy matching para nomes')
        print(f'   5️⃣ Gerar relatório consolidado')
    else:
        print(f'⚠️ BAIXO NÚMERO DE MATCHES DIRETOS')
        print(f'💡 ALTERNATIVAS:')
        print(f'   1️⃣ Implementar fuzzy matching avançado')
        print(f'   2️⃣ Cruzamento por período temporal')
        print(f'   3️⃣ Análise por vendedor/consultor')
        print(f'   4️⃣ Relatórios separados por fonte')
        print(f'   5️⃣ Dashboard consolidado sem cruzamento direto')
    
    print(f'\n📝 ARQUIVOS GERADOS PARA PRÓXIMA ETAPA:')
    print(f'   📊 Dados prontos em: data/originais/cruzamento_vixen_oss/')
    print(f'   🎯 Próximo: Implementar algoritmo de cruzamento')

if __name__ == "__main__":
    analise_final_cruzamento()