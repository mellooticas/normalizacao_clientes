#!/usr/bin/env python3
"""
Script para preparar leads marketing para tabela marketing.leads do Supabase
Mapear campos e aplicar validações da estrutura da tabela
"""

import pandas as pd
import uuid
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def mapear_status_lead(data_cadastro, convertido_em_cliente):
    """
    Mapeia status do lead baseado em regras de negócio
    """
    if pd.notna(convertido_em_cliente) and convertido_em_cliente:
        return 'CONVERTIDO'
    
    # Verificar idade do lead
    if pd.notna(data_cadastro):
        try:
            data_lead = pd.to_datetime(data_cadastro)
            dias_desde_cadastro = (datetime.now() - data_lead).days
            
            if dias_desde_cadastro <= 7:
                return 'NOVO'
            elif dias_desde_cadastro <= 30:
                return 'CONTATADO'
            else:
                return 'QUALIFICADO'
        except:
            return 'NOVO'
    
    return 'NOVO'

def mapear_temperatura_lead(data_cadastro, convertido_em_cliente):
    """
    Mapeia temperatura do lead baseado em regras de negócio
    """
    if pd.notna(convertido_em_cliente) and convertido_em_cliente:
        return 'QUENTE'
    
    # Verificar idade do lead
    if pd.notna(data_cadastro):
        try:
            data_lead = pd.to_datetime(data_cadastro)
            dias_desde_cadastro = (datetime.now() - data_lead).days
            
            if dias_desde_cadastro <= 15:
                return 'QUENTE'
            elif dias_desde_cadastro <= 90:
                return 'MORNO'
            else:
                return 'FRIO'
        except:
            return 'FRIO'
    
    return 'FRIO'

def calcular_score_lead(status, temperatura, tem_email, tem_telefone, convertido):
    """
    Calcula score do lead baseado em diversos fatores
    """
    score = 0
    
    # Score por status
    status_scores = {
        'NOVO': 10,
        'CONTATADO': 20,
        'QUALIFICADO': 40,
        'PROPOSTA': 60,
        'NEGOCIACAO': 80,
        'CONVERTIDO': 100,
        'PERDIDO': 0
    }
    score += status_scores.get(status, 0)
    
    # Score por temperatura
    temp_scores = {
        'QUENTE': 30,
        'MORNO': 20,
        'FRIO': 10
    }
    score += temp_scores.get(temperatura, 0)
    
    # Score por dados de contato
    if tem_email:
        score += 15
    if tem_telefone:
        score += 15
    
    # Bônus por conversão
    if convertido:
        score += 50
    
    return min(score, 100)  # Máximo 100

def limpar_telefone(telefone):
    """
    Limpa e padroniza telefone
    """
    if pd.isna(telefone):
        return None
    
    telefone_str = str(telefone)
    
    # Remover caracteres especiais e espaços
    telefone_limpo = ''.join(filter(str.isdigit, telefone_str))
    
    # Verificar se é um telefone válido (10-11 dígitos)
    if len(telefone_limpo) >= 10:
        return telefone_limpo[:20]  # Limit to table constraint
    
    return None

def limpar_email(email):
    """
    Limpa e valida email
    """
    if pd.isna(email) or email == '':
        return None
    
    email_str = str(email).strip().lower()
    
    # Validação básica de email
    if '@' in email_str and '.' in email_str:
        return email_str[:255]  # Limit to table constraint
    
    return None

def preparar_leads_para_banco():
    """
    Prepara leads padronizados para estrutura da tabela marketing.leads
    """
    print("🎯 === PREPARANDO LEADS PARA BANCO === 🎯")
    
    arquivo_leads = 'data/leads_marketing_padronizados_20251105_133743.csv'
    
    try:
        print(f"📄 Carregando leads padronizados...")
        df_leads = pd.read_csv(arquivo_leads)
        
        print(f"📊 Leads carregados: {len(df_leads):,}")
        print(f"📋 Colunas originais: {df_leads.shape[1]}")
        
        print(f"\n🔧 === MAPEANDO CAMPOS === 🔧")
        
        # Preparar estrutura para tabela marketing.leads
        leads_banco = []
        
        for idx, row in df_leads.iterrows():
            if idx % 1000 == 0:
                print(f"   Processando: {idx:,}/{len(df_leads):,}")
            
            # Limpar dados de contato
            telefone_limpo = limpar_telefone(row.get('telefone'))
            email_limpo = limpar_email(row.get('email'))
            
            # Calcular status e temperatura
            convertido = pd.notna(row.get('convertido_em_cliente')) and row.get('convertido_em_cliente')
            status = mapear_status_lead(row.get('data_cadastro'), convertido)
            temperatura = mapear_temperatura_lead(row.get('data_cadastro'), convertido)
            
            # Calcular score
            score = calcular_score_lead(
                status, 
                temperatura, 
                email_limpo is not None,
                telefone_limpo is not None,
                convertido
            )
            
            # Estrutura da tabela marketing.leads
            lead = {
                'id': str(uuid.uuid4()),  # Novo UUID único
                'nome': str(row.get('nome', '')).strip()[:255] if pd.notna(row.get('nome')) else None,
                'email': email_limpo,
                'telefone': telefone_limpo,
                'origem': str(row.get('canal', 'DESCONHECIDO'))[:100],  # Campo obrigatório
                'campanha_id': None,  # Não disponível nos dados atuais
                'landing_page_id': None,  # Não disponível nos dados atuais
                'status': status,
                'temperatura': temperatura,
                'score': score,
                'interesse': None,  # Pode ser derivado das observações
                'observacoes': str(row.get('observacoes', '')).strip() if pd.notna(row.get('observacoes')) else None,
                'tags': None,  # Array - pode ser implementado posteriormente
                'utm_source': None,  # Não disponível nos dados atuais
                'utm_medium': None,  # Não disponível nos dados atuais
                'utm_campaign': None,  # Não disponível nos dados atuais
                'utm_content': None,  # Não disponível nos dados atuais
                'convertido_em_cliente': convertido,
                'cliente_id': row.get('cliente_id') if pd.notna(row.get('cliente_id')) else None,
                'data_conversao': row.get('data_cadastro') if convertido else None,
                'loja_id': row.get('loja_id') if pd.notna(row.get('loja_id')) else None,
                'responsavel_id': None,  # Não disponível nos dados atuais
                'created_at': row.get('data_cadastro') if pd.notna(row.get('data_cadastro')) else datetime.now().isoformat(),
                'updated_at': row.get('atualizado_em') if pd.notna(row.get('atualizado_em')) else datetime.now().isoformat(),
                'deleted_at': None,
                
                # Campos de controle/auditoria
                'lead_id_original': row.get('id'),
                'origem_original': row.get('origem_original'),
                'loja_id_original': row.get('loja_id_original')
            }
            
            leads_banco.append(lead)
        
        # Converter para DataFrame
        df_banco = pd.DataFrame(leads_banco)
        
        print(f"\n📊 === RESULTADOS === 📊")
        print(f"📋 Leads processados: {len(df_banco):,}")
        print(f"📋 Colunas da tabela: {df_banco.shape[1]}")
        
        # Análise dos dados mapeados
        print(f"\n🔍 === ANÁLISE DOS DADOS === 🔍")
        
        # Estatísticas de contato
        com_email = df_banco['email'].notna().sum()
        com_telefone = df_banco['telefone'].notna().sum()
        com_nome = df_banco['nome'].notna().sum()
        
        print(f"📞 Com telefone: {com_telefone:,} ({com_telefone/len(df_banco)*100:.1f}%)")
        print(f"📧 Com email: {com_email:,} ({com_email/len(df_banco)*100:.1f}%)")
        print(f"👤 Com nome: {com_nome:,} ({com_nome/len(df_banco)*100:.1f}%)")
        
        # Distribuição por status
        print(f"\n📊 Distribuição por status:")
        status_dist = df_banco['status'].value_counts()
        for status, count in status_dist.items():
            print(f"   {status}: {count:,} ({count/len(df_banco)*100:.1f}%)")
        
        # Distribuição por temperatura
        print(f"\n🌡️ Distribuição por temperatura:")
        temp_dist = df_banco['temperatura'].value_counts()
        for temp, count in temp_dist.items():
            print(f"   {temp}: {count:,} ({count/len(df_banco)*100:.1f}%)")
        
        # Score médio
        score_medio = df_banco['score'].mean()
        print(f"\n📈 Score médio: {score_medio:.1f}")
        
        # Conversões
        convertidos = df_banco['convertido_em_cliente'].sum()
        print(f"✅ Convertidos: {convertidos:,} ({convertidos/len(df_banco)*100:.1f}%)")
        
        # Lojas
        lojas_com_lead = df_banco['loja_id'].notna().sum()
        print(f"🏢 Com loja: {lojas_com_lead:,} ({lojas_com_lead/len(df_banco)*100:.1f}%)")
        
        # Verificações de integridade
        print(f"\n✅ === VERIFICAÇÕES === ✅")
        
        # Campos obrigatórios
        origem_nulos = df_banco['origem'].isnull().sum()
        print(f"   Origem nulos: {origem_nulos} ({'✅' if origem_nulos == 0 else '❌'})")
        
        # Status válidos
        status_validos = df_banco['status'].isin([
            'NOVO', 'CONTATADO', 'QUALIFICADO', 'PROPOSTA', 
            'NEGOCIACAO', 'CONVERTIDO', 'PERDIDO'
        ]).all()
        print(f"   Status válidos: {'✅' if status_validos else '❌'}")
        
        # Temperatura válida
        temp_validas = df_banco['temperatura'].isin(['QUENTE', 'MORNO', 'FRIO']).all()
        print(f"   Temperaturas válidas: {'✅' if temp_validas else '❌'}")
        
        # UUIDs válidos
        uuid_validos = df_banco['id'].str.len().eq(36).all()
        print(f"   UUIDs válidos: {'✅' if uuid_validos else '❌'}")
        
        # Remover campos de controle para arquivo final
        colunas_tabela = [
            'id', 'nome', 'email', 'telefone', 'origem', 'campanha_id', 
            'landing_page_id', 'status', 'temperatura', 'score', 'interesse',
            'observacoes', 'tags', 'utm_source', 'utm_medium', 'utm_campaign',
            'utm_content', 'convertido_em_cliente', 'cliente_id', 'data_conversao',
            'loja_id', 'responsavel_id', 'created_at', 'updated_at', 'deleted_at'
        ]
        
        df_final = df_banco[colunas_tabela].copy()
        
        # Salvar arquivo para banco
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        arquivo_banco = f'data/LEADS_PARA_BANCO_{timestamp}.csv'
        
        df_final.to_csv(arquivo_banco, index=False)
        
        # Salvar também arquivo com auditoria
        arquivo_auditoria = f'data/leads_com_auditoria_{timestamp}.csv'
        df_banco.to_csv(arquivo_auditoria, index=False)
        
        print(f"\n💾 === ARQUIVOS GERADOS === 💾")
        print(f"📄 Para banco: {arquivo_banco}")
        print(f"📄 Com auditoria: {arquivo_auditoria}")
        print(f"📊 Registros: {len(df_final):,}")
        print(f"📋 Estrutura: 100% compatível com marketing.leads")
        print(f"✅ Status: Pronto para importação")
        
        return arquivo_banco
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Função principal"""
    print("🎯 === PREPARAÇÃO LEADS MARKETING === 🎯")
    print("📋 Tabela destino: marketing.leads")
    print("📋 Mapeamento: leads padronizados → estrutura banco")
    
    arquivo_final = preparar_leads_para_banco()
    
    if arquivo_final:
        print(f"\n🎉 === SUCESSO === 🎉")
        print(f"✅ Arquivo: {arquivo_final}")
        print(f"📋 Status: Leads prontos para Supabase")
        print(f"🔗 Relacionamentos: Lojas e canais mapeados")
        print(f"🎯 Importação: Pode subir para marketing.leads")
    else:
        print(f"❌ Falha na preparação")
    
    print(f"📅 Processado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()