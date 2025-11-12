"""
Validação COMPLETA do arquivo CLIENTES_OUTRAS_LOJAS.csv
contra as constraints da tabela core.clientes

Verifica TODAS as regras do banco ANTES de importar para evitar erros.
"""

import pandas as pd
from pathlib import Path
import re
from datetime import datetime

# Caminhos
BASE_DIR = Path(__file__).parent.parent
FILE_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_OUTRAS_LOJAS.csv'

print("=" * 80)
print("VALIDAÇÃO COMPLETA CONTRA CONSTRAINTS DO BANCO")
print("Tabela: core.clientes")
print("=" * 80)

# 1. Ler arquivo
print(f"\n1. Lendo arquivo: {FILE_PATH.name}")
df = pd.read_csv(FILE_PATH, sep=';', dtype=str, encoding='utf-8')
print(f"   ✓ {len(df):,} registros")

# ============================================================================
# FUNÇÕES DE VALIDAÇÃO
# ============================================================================

def validar_cpf(cpf_str):
    """
    Valida CPF segundo regras PostgreSQL
    - Pode ser NULL
    - Se preenchido, deve ter 11 dígitos numéricos
    - Não pode ter todos dígitos iguais
    - Não pode começar com 00000 ou similar
    """
    if pd.isna(cpf_str) or str(cpf_str).strip() == '':
        return True, None  # NULL é válido
    
    # Remove formatação
    cpf = re.sub(r'\D', '', str(cpf_str))
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False, f"CPF deve ter 11 dígitos (tem {len(cpf)})"
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False, "CPF com todos dígitos iguais"
    
    # Primeiros 2 dígitos devem ser >= 10 (região fiscal válida)
    # CPFs que começam com 00-09 são inválidos
    if int(cpf[:2]) < 10:
        return False, f"CPF começa com 0{cpf[1]} (região fiscal inválida)"
    
    # Lista de CPFs conhecidos como inválidos
    cpfs_invalidos = [
        '00000000000', '11111111111', '22222222222', '33333333333',
        '44444444444', '55555555555', '66666666666', '77777777777',
        '88888888888', '99999999999', '12345678901', '12345678900'
    ]
    
    if cpf in cpfs_invalidos:
        return False, "CPF conhecido como inválido"
    
    # Validação dos dígitos verificadores
    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[9]) != digito1:
        return False, f"Dígito verificador 1 inválido (esperado {digito1}, encontrado {cpf[9]})"
    
    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[10]) != digito2:
        return False, f"Dígito verificador 2 inválido (esperado {digito2}, encontrado {cpf[10]})"
    
    return True, None

def validar_email(email_str):
    """
    Valida email segundo regras PostgreSQL
    - Pode ser NULL
    - Se preenchido, deve ter formato válido com @
    """
    if pd.isna(email_str) or str(email_str).strip() == '':
        return True, None  # NULL é válido
    
    email = str(email_str).strip()
    
    # Verifica se tem @
    if '@' not in email:
        return False, "Email sem @"
    
    # Regex para email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email, re.IGNORECASE):
        return False, "Formato de email inválido"
    
    return True, None

def validar_data(data_str):
    """
    Valida data segundo regras PostgreSQL
    - Pode ser NULL
    - Se preenchida, deve ser formato YYYY-MM-DD válido
    - Dia não pode ser 00
    - Mês não pode ser 00
    """
    if pd.isna(data_str) or str(data_str).strip() == '':
        return True, None  # NULL é válido
    
    try:
        # Verifica formato básico
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(data_str)):
            return False, "Formato deve ser YYYY-MM-DD"
        
        # Verifica se dia ou mês são 00
        if str(data_str).endswith('-00'):
            return False, "Dia não pode ser 00"
        
        if '-00-' in str(data_str):
            return False, "Mês não pode ser 00"
        
        # Tenta parsear a data
        data = datetime.strptime(str(data_str), '%Y-%m-%d')
        
        # Verifica se a data é razoável
        if data.year < 1900 or data.year > 2025:
            return False, f"Ano {data.year} fora do range válido"
        
        return True, None
    except Exception as e:
        return False, f"Data inválida: {str(e)}"

def validar_sexo(sexo_str):
    """
    Valida sexo segundo regras PostgreSQL
    - Pode ser NULL
    - Se preenchido, deve ser 'M', 'F' ou 'O'
    """
    if pd.isna(sexo_str) or str(sexo_str).strip() == '':
        return True, None  # NULL é válido
    
    sexo = str(sexo_str).strip().upper()
    
    if sexo not in ['M', 'F', 'O']:
        return False, f"Sexo deve ser M, F ou O (encontrado: '{sexo}')"
    
    return True, None

def validar_status(status_str):
    """
    Valida status segundo regras PostgreSQL
    - Obrigatório (NOT NULL)
    - Deve ser um dos valores: 'ATIVO', 'INATIVO', 'BLOQUEADO', 'PENDENTE'
    """
    if pd.isna(status_str) or str(status_str).strip() == '':
        return False, "Status é obrigatório (NOT NULL)"
    
    status = str(status_str).strip().upper()
    
    valores_validos = ['ATIVO', 'INATIVO', 'BLOQUEADO', 'PENDENTE']
    
    if status not in valores_validos:
        return False, f"Status deve ser um de {valores_validos} (encontrado: '{status}')"
    
    return True, None

def validar_nome(nome_str):
    """
    Valida nome segundo regras PostgreSQL
    - Obrigatório (NOT NULL)
    - Não pode ser vazio
    """
    if pd.isna(nome_str) or str(nome_str).strip() == '':
        return False, "Nome é obrigatório (NOT NULL)"
    
    return True, None

# ============================================================================
# EXECUTAR VALIDAÇÕES
# ============================================================================

print(f"\n2. Executando validações...")

erros = []
correcoes_necessarias = 0

# Mapeamento de colunas para validadores
validacoes = {
    'cpf': validar_cpf,
    'email': validar_email,
    'data_nascimento': validar_data,
    'cliente_desde': validar_data,
    'sexo': validar_sexo,
    'status': validar_status,
    'nome': validar_nome
}

# Executar validações
for coluna, validador in validacoes.items():
    if coluna not in df.columns:
        print(f"   ⚠️ Coluna '{coluna}' não encontrada no arquivo!")
        continue
    
    print(f"\n   Validando: {coluna}...")
    erros_coluna = 0
    
    for idx, valor in df[coluna].items():
        valido, mensagem_erro = validador(valor)
        
        if not valido:
            erros_coluna += 1
            correcoes_necessarias += 1
            
            # Guardar erro
            nome_cliente = df.at[idx, 'nome'] if 'nome' in df.columns else f"Linha {idx + 2}"
            erros.append({
                'linha': idx + 2,  # +2 porque: +1 para linha real, +1 para header
                'nome': nome_cliente,
                'coluna': coluna,
                'valor': valor,
                'erro': mensagem_erro
            })
            
            # Mostrar só os primeiros 5 erros de cada coluna
            if erros_coluna <= 5:
                print(f"     ❌ Linha {idx + 2} ({nome_cliente}): {mensagem_erro}")
                print(f"        Valor: '{valor}'")
    
    if erros_coluna == 0:
        print(f"     ✅ Todos os {len(df)} valores válidos")
    else:
        print(f"     ⚠️ {erros_coluna} erros encontrados")
        if erros_coluna > 5:
            print(f"        (mostrando apenas os primeiros 5)")

# ============================================================================
# RELATÓRIO FINAL
# ============================================================================

print("\n" + "=" * 80)
print("RELATÓRIO DE VALIDAÇÃO")
print("=" * 80)

if correcoes_necessarias == 0:
    print("\n✅ ARQUIVO VÁLIDO! Pronto para importação.")
    print(f"\n   Total de registros: {len(df):,}")
    print(f"   Todas as constraints validadas com sucesso!")
else:
    print(f"\n⚠️ ARQUIVO COM ERROS! {correcoes_necessarias} correções necessárias.")
    print(f"\n   Total de registros: {len(df):,}")
    print(f"   Registros com erro: {len(set([e['linha'] for e in erros]))}")
    
    print(f"\n   Erros por coluna:")
    erros_por_coluna = {}
    for erro in erros:
        col = erro['coluna']
        if col not in erros_por_coluna:
            erros_por_coluna[col] = 0
        erros_por_coluna[col] += 1
    
    for col, count in sorted(erros_por_coluna.items(), key=lambda x: x[1], reverse=True):
        print(f"     - {col}: {count} erros")
    
    print(f"\n   Salvando relatório detalhado de erros...")
    
    # Salvar relatório de erros em CSV
    df_erros = pd.DataFrame(erros)
    erro_path = FILE_PATH.parent / 'ERROS_VALIDACAO.csv'
    df_erros.to_csv(erro_path, sep=';', index=False, encoding='utf-8')
    print(f"     ✓ Arquivo salvo: {erro_path.name}")
    print(f"     ✓ {len(erros)} erros listados")

print("\n" + "=" * 80)
