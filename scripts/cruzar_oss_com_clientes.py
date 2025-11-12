"""
Cruza OSS.csv com CLIENTES_FINAL_CONSOLIDADO para adicionar IDs únicos aos pedidos/vendas
"""
import pandas as pd
from pathlib import Path
from datetime import datetime

# Configuração
DIR_BASE = Path(__file__).parent.parent
ARQUIVO_OSS = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'OSS.csv'
ARQUIVO_CLIENTES = DIR_BASE / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_FINAL_CONSOLIDADO_20251109_205218.csv'
DIR_SAIDA = DIR_BASE / 'dados_processados' / 'originais' / 'vendas'

def limpar_cpf(cpf_str):
    """Remove formatação do CPF"""
    if pd.isna(cpf_str) or cpf_str == 'nan' or str(cpf_str).strip() == '':
        return None
    return str(cpf_str).replace('.', '').replace('-', '').replace(' ', '').strip()

def limpar_telefone(tel_str):
    """Remove formatação de telefone"""
    if pd.isna(tel_str) or str(tel_str).strip() == '':
        return None
    return str(tel_str).replace('(', '').replace(')', '').replace('-', '').replace(' ', '').strip()

def main():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print("="*70)
    print("=== CRUZAMENTO OSS.CSV COM CLIENTES CONSOLIDADOS ===")
    print("="*70)
    
    # Lê arquivo de clientes consolidado
    print("\n1. Lendo arquivo de clientes consolidado...")
    df_clientes = pd.read_csv(ARQUIVO_CLIENTES, sep=';', dtype=str)
    df_clientes['cpf_limpo'] = df_clientes['cpf'].apply(limpar_cpf)
    
    print(f"   ✓ {len(df_clientes)} clientes carregados")
    print(f"   ✓ {df_clientes['cpf_limpo'].notna().sum()} com CPF")
    
    # Cria dicionários de lookup
    print("\n2. Criando índices de busca...")
    
    # Por CPF
    clientes_por_cpf = {}
    for _, row in df_clientes[df_clientes['cpf_limpo'].notna()].iterrows():
        cpf = row['cpf_limpo']
        if cpf not in clientes_por_cpf:
            clientes_por_cpf[cpf] = row.to_dict()
    
    print(f"   ✓ {len(clientes_por_cpf)} CPFs indexados")
    
    # Por nome (para fallback quando não tem CPF)
    clientes_por_nome = {}
    for _, row in df_clientes.iterrows():
        nome = str(row['nome']).strip().upper()
        if nome and nome != 'NAN':
            if nome not in clientes_por_nome:
                clientes_por_nome[nome] = []
            clientes_por_nome[nome].append(row.to_dict())
    
    print(f"   ✓ {len(clientes_por_nome)} nomes indexados")
    
    # Lê arquivo OSS
    print("\n3. Lendo arquivo OSS.csv...")
    df_oss = pd.read_csv(ARQUIVO_OSS, sep=';', dtype=str, encoding='utf-8-sig')
    
    print(f"   ✓ {len(df_oss)} OS (Ordens de Serviço) carregadas")
    print(f"\n   Colunas do OSS:")
    print(f"     - OS N°: {df_oss['OS N°'].notna().sum()} preenchidas")
    print(f"     - NOME: {df_oss['NOME:'].notna().sum()} preenchidos")
    print(f"     - CPF: {df_oss['CPF'].notna().sum()} preenchidos")
    print(f"     - ID_CLIENTE (antigo): {df_oss['ID_CLIENTE'].notna().sum()} preenchidos")
    
    # Limpa CPFs no OSS
    df_oss['cpf_limpo'] = df_oss['CPF'].apply(limpar_cpf)
    
    # Faz o cruzamento
    print("\n4. Cruzando dados...")
    
    matches_cpf = 0
    matches_nome = 0
    sem_match = 0
    
    # Adiciona colunas para o ID novo
    df_oss['id_cliente_novo'] = None
    df_oss['match_tipo'] = None
    df_oss['cliente_nome_consolidado'] = None
    df_oss['cliente_cpf_consolidado'] = None
    df_oss['cliente_email_consolidado'] = None
    df_oss['cliente_origem'] = None
    
    for idx, row in df_oss.iterrows():
        cpf = row['cpf_limpo']
        nome = str(row['NOME:']).strip().upper() if pd.notna(row['NOME:']) else None
        
        match_encontrado = False
        
        # Tenta match por CPF primeiro
        if cpf and cpf in clientes_por_cpf:
            cliente = clientes_por_cpf[cpf]
            df_oss.at[idx, 'id_cliente_novo'] = cliente['id_legado']
            df_oss.at[idx, 'match_tipo'] = 'CPF'
            df_oss.at[idx, 'cliente_nome_consolidado'] = cliente['nome']
            df_oss.at[idx, 'cliente_cpf_consolidado'] = cliente['cpf']
            df_oss.at[idx, 'cliente_email_consolidado'] = cliente.get('email')
            df_oss.at[idx, 'cliente_origem'] = cliente['origem']
            matches_cpf += 1
            match_encontrado = True
        
        # Se não achou por CPF, tenta por nome
        elif nome and nome in clientes_por_nome:
            # Pega o primeiro cliente com esse nome
            cliente = clientes_por_nome[nome][0]
            df_oss.at[idx, 'id_cliente_novo'] = cliente['id_legado']
            df_oss.at[idx, 'match_tipo'] = 'NOME'
            df_oss.at[idx, 'cliente_nome_consolidado'] = cliente['nome']
            df_oss.at[idx, 'cliente_cpf_consolidado'] = cliente.get('cpf')
            df_oss.at[idx, 'cliente_email_consolidado'] = cliente.get('email')
            df_oss.at[idx, 'cliente_origem'] = cliente['origem']
            matches_nome += 1
            match_encontrado = True
        
        if not match_encontrado:
            sem_match += 1
    
    print(f"\n   Resultados do cruzamento:")
    print(f"     ✓ Matches por CPF: {matches_cpf}")
    print(f"     ✓ Matches por NOME: {matches_nome}")
    print(f"     ⚠️  Sem match: {sem_match}")
    print(f"     📊 Taxa de sucesso: {((matches_cpf + matches_nome) / len(df_oss) * 100):.1f}%")
    
    # Salva arquivo cruzado
    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    arquivo_saida = DIR_SAIDA / f'OSS_COM_IDS_CLIENTES_{timestamp}.csv'
    
    df_oss.to_csv(arquivo_saida, sep=';', index=False, encoding='utf-8-sig')
    
    print("\n" + "="*70)
    print("=== ARQUIVO CRUZADO CRIADO ===")
    print(f"\n📁 {arquivo_saida.name}")
    print(f"📍 {arquivo_saida.parent}")
    print(f"\n✅ {len(df_oss)} OS com IDs cruzados")
    
    # Estatísticas detalhadas
    print("\n" + "="*70)
    print("=== ESTATÍSTICAS ===")
    
    print(f"\nOS com ID novo encontrado: {df_oss['id_cliente_novo'].notna().sum()}")
    print(f"OS sem ID novo: {df_oss['id_cliente_novo'].isna().sum()}")
    
    print(f"\nDistribuição por tipo de match:")
    if df_oss['match_tipo'].notna().sum() > 0:
        for tipo, count in df_oss['match_tipo'].value_counts().items():
            print(f"   {tipo}: {count}")
    
    print(f"\nDistribuição por origem do cliente:")
    if df_oss['cliente_origem'].notna().sum() > 0:
        for origem, count in df_oss['cliente_origem'].value_counts().items():
            print(f"   {origem}: {count}")
    
    # Exemplos de OS sem match
    os_sem_match = df_oss[df_oss['id_cliente_novo'].isna()]
    if len(os_sem_match) > 0:
        print(f"\n" + "="*70)
        print("=== EXEMPLOS DE OS SEM MATCH (primeiras 5) ===")
        for idx, row in os_sem_match.head(5).iterrows():
            print(f"\nOS {row['OS N°']}:")
            print(f"   Nome: {row['NOME:']}")
            print(f"   CPF: {row['CPF']}")
            print(f"   ID antigo: {row['ID_CLIENTE']}")
    
    print("\n" + "="*70)
    print("\n🎯 CRUZAMENTO CONCLUÍDO!")
    print("\nNovas colunas adicionadas ao OSS.csv:")
    print("   - id_cliente_novo: ID único do cliente consolidado")
    print("   - match_tipo: Como o match foi feito (CPF ou NOME)")
    print("   - cliente_nome_consolidado: Nome do cliente no arquivo consolidado")
    print("   - cliente_cpf_consolidado: CPF do cliente no arquivo consolidado")
    print("   - cliente_email_consolidado: Email do cliente no arquivo consolidado")
    print("   - cliente_origem: Origem do cliente (OSS_SUZANO_MAUA, VIXEN, etc)")
    print("\n" + "="*70)

if __name__ == '__main__':
    main()
