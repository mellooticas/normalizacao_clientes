#!/usr/bin/env python3
"""
Importador Limpo - Carnê Fácil
Importa dados consolidados direto para Supabase
"""

import os
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from datetime import datetime
import uuid
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImportadorLimpo:
    """Importador limpo de dados para Supabase"""
    
    def __init__(self):
        self.load_config()
        self.conn = None
        
    def load_config(self):
        """Carrega configurações do .env"""
        from dotenv import load_dotenv
        load_dotenv()
        
        self.database_url = os.getenv('SUPABASE_DATABASE_URL') or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL não encontrada no .env")
    
    def connect(self):
        """Conecta ao Supabase"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.conn.autocommit = False
            logger.info("✅ Conectado ao Supabase")
            return True
        except Exception as e:
            logger.error(f"❌ Erro de conexão: {e}")
            return False
    
    def criar_lojas(self):
        """Cria as lojas padrão"""
        logger.info("🏢 Criando lojas...")
        
        lojas = [
            ('MAUA', 'Ótica Mauá', 'Mauá', 'SP', True),
            ('SUZANO', 'Ótica Suzano', 'Suzano', 'SP', True),
            ('SUZANO2', 'Ótica Suzano 2', 'Suzano', 'SP', True),
            ('RIO_PEQUENO', 'Ótica Rio Pequeno', 'São Paulo', 'SP', True),
            ('PERUS', 'Ótica Perus', 'São Paulo', 'SP', True),
            ('SAO_MATEUS', 'Ótica São Mateus', 'São Paulo', 'SP', False),  # Fechada
        ]
        
        cursor = self.conn.cursor()
        
        for codigo, nome, cidade, estado, ativa in lojas:
            loja_id = str(uuid.uuid4())
            try:
                cursor.execute("""
                    INSERT INTO core.lojas (id, codigo, nome, cidade, estado, ativa, criado_em)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (codigo) DO UPDATE SET
                        nome = EXCLUDED.nome,
                        cidade = EXCLUDED.cidade,
                        estado = EXCLUDED.estado,
                        ativa = EXCLUDED.ativa
                """, (loja_id, codigo, nome, cidade, estado, ativa))
                
            except Exception as e:
                logger.warning(f"Loja {codigo} já existe ou erro: {e}")
        
        self.conn.commit()
        logger.info("✅ Lojas criadas/atualizadas")
    
    def importar_clientes_os(self):
        """Importa clientes do arquivo os_clientes.parquet"""
        logger.info("👥 Importando clientes OS...")
        
        # Carregar dados
        df = pd.read_parquet('data_backup/input/os_clientes.parquet')
        logger.info(f"📄 Arquivo carregado: {len(df)} registros")
        
        # Preparar dados
        clientes_data = []
        telefones_data = []
        
        # Mapear lojas
        loja_map = self.get_loja_map()
        
        for _, row in df.iterrows():
            # Extrair loja do arquivo_origem
            arquivo = str(row.get('arquivo_origem', ''))
            loja_codigo = self.extrair_loja_do_arquivo(arquivo)
            loja_id = loja_map.get(loja_codigo)
            
            if not loja_id:
                logger.warning(f"Loja não encontrada para: {arquivo}")
                continue
            
            # Preparar cliente
            cliente_id = str(uuid.uuid4())
            cliente = (
                cliente_id,
                str(row.get('nome', '')).strip(),
                str(row.get('cpf', '')).replace('.', '').replace('-', '').strip(),
                None,  # rg
                None,  # data_nascimento
                str(row.get('email', '')).strip() if pd.notna(row.get('email')) else None,
                None,  # telefone_principal (será definido abaixo)
                None,  # endereco
                None,  # bairro
                None,  # cidade
                None,  # cep
                loja_id,
                f"Origem: {arquivo}",  # observacoes
                True,  # ativo
            )
            
            # Telefones
            telefone = str(row.get('telefone', '')).strip() if pd.notna(row.get('telefone')) else None
            celular = str(row.get('celular', '')).strip() if pd.notna(row.get('celular')) else None
            
            telefone_principal = celular or telefone
            
            # Atualizar cliente com telefone principal
            cliente = cliente[:5] + (telefone_principal,) + cliente[6:]
            clientes_data.append(cliente)
            
            # Adicionar telefones
            if telefone and telefone != telefone_principal:
                telefones_data.append((cliente_id, telefone, 'FIXO', True))
            if celular and celular != telefone_principal:
                telefones_data.append((cliente_id, celular, 'CELULAR', True))
            elif celular:
                telefones_data.append((cliente_id, celular, 'CELULAR', True))
        
        # Inserir clientes
        cursor = self.conn.cursor()
        
        logger.info(f"💾 Inserindo {len(clientes_data)} clientes...")
        execute_values(
            cursor,
            """
            INSERT INTO core.clientes 
            (id, nome, cpf, rg, data_nascimento, email, telefone_principal, 
             endereco, bairro, cidade, cep, loja_id, observacoes, ativo)
            VALUES %s
            ON CONFLICT (cpf, loja_id) DO UPDATE SET
                nome = EXCLUDED.nome,
                email = EXCLUDED.email,
                telefone_principal = EXCLUDED.telefone_principal
            """,
            clientes_data
        )
        
        # Inserir telefones
        if telefones_data:
            logger.info(f"📞 Inserindo {len(telefones_data)} telefones...")
            execute_values(
                cursor,
                """
                INSERT INTO core.telefones (cliente_id, numero, tipo, ativo)
                VALUES %s
                ON CONFLICT DO NOTHING
                """,
                telefones_data
            )
        
        self.conn.commit()
        logger.info("✅ Clientes OS importados")
    
    def importar_clientes_vixen(self):
        """Importa clientes do arquivo vixen_clientes.parquet"""
        logger.info("👥 Importando clientes Vixen...")
        
        # Carregar dados
        df = pd.read_parquet('data_backup/input/vixen_clientes.parquet')
        logger.info(f"📄 Arquivo carregado: {len(df)} registros")
        
        # Preparar dados (assumindo que são de SUZANO baseado no email)
        loja_map = self.get_loja_map()
        suzano_id = loja_map.get('SUZANO')
        
        clientes_data = []
        
        for _, row in df.iterrows():
            cliente_id = str(uuid.uuid4())
            
            # Extrair telefone do campo Fone
            fone_raw = str(row.get('Fone', ''))
            telefone = self.limpar_telefone(fone_raw)
            
            cliente = (
                cliente_id,
                str(row.get('Cliente', '')).strip(),
                None,  # cpf (não disponível)
                None,  # rg
                None,  # data_nascimento
                str(row.get('E-mail', '')).strip() if pd.notna(row.get('E-mail')) else None,
                telefone,
                None,  # endereco
                None,  # bairro
                None,  # cidade
                None,  # cep
                suzano_id,
                f"Origem: Vixen ID {row.get('ID', '')}",
                True,  # ativo
            )
            
            clientes_data.append(cliente)
        
        # Inserir clientes
        cursor = self.conn.cursor()
        
        logger.info(f"💾 Inserindo {len(clientes_data)} clientes Vixen...")
        execute_values(
            cursor,
            """
            INSERT INTO core.clientes 
            (id, nome, cpf, rg, data_nascimento, email, telefone_principal, 
             endereco, bairro, cidade, cep, loja_id, observacoes, ativo)
            VALUES %s
            ON CONFLICT (nome, loja_id) DO UPDATE SET
                email = EXCLUDED.email,
                telefone_principal = EXCLUDED.telefone_principal
            """,
            clientes_data
        )
        
        self.conn.commit()
        logger.info("✅ Clientes Vixen importados")
    
    def importar_vendas(self):
        """Importa vendas do arquivo vendas_os_completo.csv"""
        logger.info("💰 Importando vendas...")
        
        # Carregar dados
        df = pd.read_csv('data_backup/vendas_os_completo.csv')
        logger.info(f"📄 Arquivo carregado: {len(df)} registros")
        
        # Mapear lojas
        loja_map = self.get_loja_map()
        
        vendas_data = []
        
        for _, row in df.iterrows():
            loja_codigo = str(row.get('loja', '')).strip()
            loja_id = loja_map.get(loja_codigo)
            
            if not loja_id:
                continue
            
            # Buscar cliente por CPF e loja
            cliente_id = self.buscar_cliente_por_cpf(str(row.get('cpf', '')), loja_id)
            
            venda_id = str(uuid.uuid4())
            
            # Converter data
            data_venda = pd.to_datetime(row.get('data_de_compra'), errors='coerce')
            if pd.isna(data_venda):
                continue
            
            # Valor total
            valor_total = float(row.get('total', 0)) if pd.notna(row.get('total')) else 0
            
            venda = (
                venda_id,
                str(row.get('os_n', '')).strip(),
                cliente_id,
                loja_id,
                data_venda.date(),
                valor_total,
                0,  # desconto
                str(row.get('pagto_1', '')).strip() if pd.notna(row.get('pagto_1')) else None,
                'FINALIZADA',
                f"Consultor: {row.get('consultor', '')}, Como conheceu: {row.get('como_conheceu', '')}",
            )
            
            vendas_data.append(venda)
        
        # Inserir vendas
        cursor = self.conn.cursor()
        
        logger.info(f"💾 Inserindo {len(vendas_data)} vendas...")
        execute_values(
            cursor,
            """
            INSERT INTO vendas.vendas 
            (id, os_numero, cliente_id, loja_id, data_venda, valor_total, 
             desconto, forma_pagamento, status, observacoes)
            VALUES %s
            ON CONFLICT (os_numero, loja_id) DO UPDATE SET
                valor_total = EXCLUDED.valor_total,
                forma_pagamento = EXCLUDED.forma_pagamento
            """,
            vendas_data
        )
        
        self.conn.commit()
        logger.info("✅ Vendas importadas")
    
    def get_loja_map(self):
        """Retorna mapeamento código -> id das lojas"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT codigo, id FROM core.lojas")
        return {row[0]: row[1] for row in cursor.fetchall()}
    
    def buscar_cliente_por_cpf(self, cpf, loja_id):
        """Busca cliente por CPF e loja"""
        if not cpf or cpf == 'nan':
            return None
            
        cpf_limpo = str(cpf).replace('.', '').replace('-', '').strip()
        
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM core.clientes WHERE cpf = %s AND loja_id = %s LIMIT 1",
            (cpf_limpo, loja_id)
        )
        
        result = cursor.fetchone()
        return result[0] if result else None
    
    def extrair_loja_do_arquivo(self, arquivo):
        """Extrai código da loja do nome do arquivo"""
        arquivo_upper = arquivo.upper()
        
        if 'MAUA' in arquivo_upper:
            return 'MAUA'
        elif 'SUZANO2' in arquivo_upper:
            return 'SUZANO2' 
        elif 'SUZANO' in arquivo_upper:
            return 'SUZANO'
        elif 'PERUS' in arquivo_upper:
            return 'PERUS'
        elif 'RIO_PEQUENO' in arquivo_upper or 'RIO PEQUENO' in arquivo_upper:
            return 'RIO_PEQUENO'
        elif 'SAO_MATEUS' in arquivo_upper or 'SÃO MATEUS' in arquivo_upper:
            return 'SAO_MATEUS'
        
        return 'SUZANO'  # Padrão
    
    def limpar_telefone(self, fone_raw):
        """Limpa e extrai telefone"""
        import re
        
        if not fone_raw or fone_raw == 'nan':
            return None
        
        # Extrair números
        numeros = re.findall(r'\d+', str(fone_raw))
        if numeros:
            telefone = ''.join(numeros)
            # Remover código do país se presente
            if telefone.startswith('55') and len(telefone) > 11:
                telefone = telefone[2:]
            return telefone if len(telefone) >= 10 else None
        
        return None
    
    def relatorio_final(self):
        """Gera relatório final da importação"""
        logger.info("📊 Gerando relatório final...")
        
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        
        # Contar registros
        tabelas = [
            ('core.lojas', 'Lojas'),
            ('core.clientes', 'Clientes'),
            ('core.telefones', 'Telefones'),
            ('vendas.vendas', 'Vendas'),
        ]
        
        logger.info("\n" + "="*50)
        logger.info("RELATÓRIO FINAL DA IMPORTAÇÃO")
        logger.info("="*50)
        
        for tabela, nome in tabelas:
            cursor.execute(f"SELECT COUNT(*) as total FROM {tabela}")
            count = cursor.fetchone()['total']
            logger.info(f"  ✅ {nome}: {count:,} registros")
        
        # Clientes por loja
        cursor.execute("""
            SELECT l.codigo, l.nome, COUNT(c.id) as clientes
            FROM core.lojas l
            LEFT JOIN core.clientes c ON c.loja_id = l.id  
            GROUP BY l.codigo, l.nome
            ORDER BY clientes DESC
        """)
        
        logger.info("\n📍 CLIENTES POR LOJA:")
        for row in cursor.fetchall():
            logger.info(f"  • {row['codigo']}: {row['clientes']:,} clientes")
        
        logger.info("\n🎯 IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info("="*50)
    
    def close(self):
        """Fecha conexão"""
        if self.conn:
            self.conn.close()
            logger.info("🔌 Conexão fechada")

def main():
    """Função principal"""
    logger.info("="*60)
    logger.info("IMPORTADOR LIMPO - CARNÊ FÁCIL")
    logger.info(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info("="*60)
    
    importador = ImportadorLimpo()
    
    try:
        if not importador.connect():
            logger.error("❌ Falha na conexão. Verifique credenciais Supabase.")
            return
        
        # Executar importação
        importador.criar_lojas()
        importador.importar_clientes_os()
        importador.importar_clientes_vixen()
        importador.importar_vendas()
        importador.relatorio_final()
        
    except Exception as e:
        logger.error(f"❌ Erro durante importação: {e}")
        if importador.conn:
            importador.conn.rollback()
    
    finally:
        importador.close()

if __name__ == "__main__":
    main()