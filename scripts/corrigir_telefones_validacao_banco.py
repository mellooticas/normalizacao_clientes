import pandas as pd
import re

# Carregar arquivo de telefones
df = pd.read_csv('data/telefones_para_importar/telefones_core_final.csv', dtype=str)

def validar_telefone_brasileiro(numero):
    """Simula a validação que o banco faz"""
    # Remove tudo que não for número
    apenas_numeros = re.sub(r'\D', '', str(numero))
    
    # Telefone brasileiro deve ter 10 ou 11 dígitos
    if len(apenas_numeros) not in [10, 11]:
        return False
        
    # Se tiver 11 dígitos, o terceiro deve ser 9 (celular)
    if len(apenas_numeros) == 11 and apenas_numeros[2] != '9':
        return False
        
    return True

def normalizar_telefone_brasileiro(numero):
    """Normaliza telefone para formato brasileiro válido"""
    # Remove tudo que não for número
    apenas_numeros = re.sub(r'\D', '', str(numero))
    
    # Se tem 11 dígitos e é válido, formata
    if len(apenas_numeros) == 11 and apenas_numeros[2] == '9':
        return f'({apenas_numeros[:2]}) {apenas_numeros[2:]}'
    
    # Se tem 10 dígitos, adiciona 9 e formata
    if len(apenas_numeros) == 10:
        return f'({apenas_numeros[:2]}) 9{apenas_numeros[2:]}'
    
    # Se não conseguir normalizar, retorna vazio
    return ''

# Identificar telefones inválidos
df['valido'] = df['numero'].apply(validar_telefone_brasileiro)
invalidos = df[~df['valido']]

print(f'Total de telefones: {len(df)}')
print(f'Telefones inválidos: {len(invalidos)}')

if len(invalidos) > 0:
    print('\nExemplos de telefones inválidos:')
    print(invalidos['numero'].head(10).tolist())
    
    # Salvar relatório de inválidos
    invalidos[['cliente_id', 'numero']].to_csv('data/telefones_para_importar/telefones_invalidos.csv', index=False)

# Normalizar todos os telefones
df['numero_corrigido'] = df['numero'].apply(normalizar_telefone_brasileiro)

# Remover telefones que não puderam ser corrigidos
df_final = df[df['numero_corrigido'] != ''].copy()
df_final['numero'] = df_final['numero_corrigido']
df_final = df_final[['cliente_id', 'tipo', 'numero', 'whatsapp', 'principal', 'observacao']]

# Salvar arquivo corrigido
df_final.to_csv('data/telefones_para_importar/telefones_core_final_corrigido.csv', index=False, encoding='utf-8')

print(f'Telefones corrigidos: {len(df_final)}')
print(f'Telefones removidos (não corrigíveis): {len(df) - len(df_final)}')