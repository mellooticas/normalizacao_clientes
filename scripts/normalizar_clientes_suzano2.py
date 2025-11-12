import pandas as pd
import re
from datetime import datetime

arq = 'data/originais/clientes/clientes_suzano2.csv'
dest = 'data/originais/clientes/clientes_suzano2_normalizado.csv'

# Funções auxiliares
def validar_cpf(cpf):
    if pd.isna(cpf): return False
    cpf = re.sub(r'[^0-9]', '', str(cpf))
    if len(cpf) != 11 or cpf == cpf[0]*11: return False
    for i in [9, 10]:
        soma = sum(int(cpf[num]) * ((i+1) - num) for num in range(0, i))
        digito = ((soma * 10) % 11) % 10
        if digito != int(cpf[i]): return False
    return True

def validar_email(email):
    if pd.isna(email) or not isinstance(email, str) or not email.strip(): return False
    return bool(re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', email))

def validar_data(dt):
    try:
        if pd.isna(dt) or not str(dt).strip(): return False
        d = pd.to_datetime(dt, errors='coerce')
        return d is not pd.NaT and d <= pd.Timestamp.today()
    except: return False

def normalizar_sexo(sexo):
    if not isinstance(sexo, str): return ''
    s = sexo.strip().upper()
    return s if s in ['M','F','O'] else ''

# Carregar dados
df = pd.read_csv(arq, dtype=str)

# Montar DataFrame no modelo da tabela
df_out = pd.DataFrame()
df_out['id_legado'] = df[df.columns[0]]
df_out['nome'] = df['cliente_nome_normalizado'].fillna('')
df_out['cpf'] = df['CPF'].apply(lambda x: re.sub(r'[^0-9]', '', str(x)) if validar_cpf(x) else pd.NA)
df_out['rg'] = df['RG'].where(df['RG'].notna(), pd.NA)
df_out['data_nascimento'] = df['data_nascimento'].apply(lambda x: x if validar_data(x) else pd.NA)
df_out['sexo'] = df['sexo'].apply(normalizar_sexo) if 'sexo' in df.columns else ''
df_out['email'] = df['EMAIL:'].apply(lambda x: x if validar_email(x) else pd.NA)
df_out['user_id'] = pd.NA
df_out['status'] = 'ATIVO'
df_out['created_at'] = pd.NaT
df_out['updated_at'] = pd.NaT
df_out['created_by'] = pd.NA
df_out['updated_by'] = pd.NA
df_out['deleted_at'] = pd.NaT
df_out['version'] = 1

# Remover duplicidade de id_legado e cpf
if df_out['id_legado'].duplicated().any():
    df_out = df_out.drop_duplicates(subset=['id_legado'], keep='first')
if df_out['cpf'].notna().duplicated().any():
    df_out.loc[df_out['cpf'].duplicated(keep='first'), 'cpf'] = pd.NA

# Reorganizar colunas
cols = ['id_legado','user_id','nome','cpf','rg','data_nascimento','sexo','email','status','created_at','updated_at','created_by','updated_by','deleted_at','version']
df_out = df_out[cols]

df_out.to_csv(dest, index=False, encoding='utf-8')
print(f'Arquivo normalizado salvo em {dest}')
