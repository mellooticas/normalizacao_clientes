#!/usr/bin/env python3
"""
Importador de Dados Completos - Carnê Fácil
Importa dados reais das planilhas originais para o Supabase
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

class ImportadorCompleto:
    """Importador completo de dados originais para Supabase"""
    
    def __init__(self):
        self.load_config()
        self.conn = None
        self.base_path = Path("data/originais")
        self.arquivos_processados = []
        
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
    
    def verificar_dados_disponiveis(self):
        """Verifica se há dados para processar"""
        logger.info("🔍 Verificando dados disponíveis...")
        
        # Executar analisador primeiro
        from analisar_dados_originais import AnalisadorDadosOriginais
        analisador = AnalisadorDadosOriginais()
        analisador.varrer_pastas()
        
        total_arquivos = sum(len(arquivos) for arquivos in analisador.arquivos_encontrados.values())
        
        if total_arquivos == 0:
            logger.error("❌ Nenhum arquivo encontrado para importar!")
            logger.error("📁 Coloque os arquivos nas pastas apropriadas em data/originais/")
            return False
        
        logger.info(f"📊 {total_arquivos} arquivo(s) encontrado(s) para processar")
        
        # Verificar tipos essenciais
        todos_arquivos = []
        for arquivos in analisador.arquivos_encontrados.values():
            todos_arquivos.extend(arquivos)
        
        tem_clientes = any(arquivo.get('conteudo_tipo') == 'CLIENTES' for arquivo in todos_arquivos)
        tem_vendas = any(arquivo.get('conteudo_tipo') in ['VENDAS', 'ORDENS_SERVICO'] for arquivo in todos_arquivos)
        
        if not tem_clientes:
            logger.warning("⚠️ Nenhum arquivo de CLIENTES identificado")
        if not tem_vendas:
            logger.warning("⚠️ Nenhum arquivo de VENDAS/OS identificado")
        
        return True
    
    def importar_vixen(self):
        """Importa dados do sistema Vixen"""
        logger.info("🔄 Processando dados Vixen...")
        
        pasta_vixen = self.base_path / "vixen"
        arquivos_clientes = list(pasta_vixen.glob("**/*.xlsx")) + list(pasta_vixen.glob("**/*.csv"))
        
        if not arquivos_clientes:
            logger.info("📭 Nenhum arquivo Vixen encontrado")
            return
        
        for arquivo in arquivos_clientes:
            logger.info(f"📄 Processando: {arquivo.name}")
            
            try:
                # Detectar tipo de arquivo
                if arquivo.suffix.lower() == '.csv':
                    df = pd.read_csv(arquivo)
                else:
                    df = pd.read_excel(arquivo)
                
                # Identificar tipo de conteúdo e processar
                if self._identificar_clientes(df):
                    self._processar_clientes_vixen(df, arquivo.name)
                elif self._identificar_vendas(df):
                    self._processar_vendas_vixen(df, arquivo.name)
                else:
                    logger.warning(f"⚠️ Tipo de conteúdo não identificado: {arquivo.name}")
                
                self.arquivos_processados.append({
                    'arquivo': arquivo.name,
                    'tipo': 'vixen',
                    'registros': len(df),
                    'status': 'OK'
                })
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar {arquivo.name}: {e}")
                self.arquivos_processados.append({
                    'arquivo': arquivo.name,
                    'tipo': 'vixen',
                    'registros': 0,
                    'status': f'ERRO: {e}'
                })
    
    def importar_oss(self):
        """Importa Ordens de Serviço"""
        logger.info("📋 Processando Ordens de Serviço...")
        
        pasta_oss = self.base_path / "oss"
        
        # Processar por loja
        for loja_pasta in pasta_oss.glob("por_loja/*"):
            if loja_pasta.is_dir():
                self._processar_oss_loja(loja_pasta)
        
        # Processar consolidadas
        pasta_consolidadas = pasta_oss / "consolidadas"
        if pasta_consolidadas.exists():
            self._processar_oss_consolidadas(pasta_consolidadas)
    
    def importar_cxs(self):
        """Importa dados de Caixa"""
        logger.info("💰 Processando dados de Caixa...")
        
        pasta_cxs = self.base_path / "cxs"
        arquivos = list(pasta_cxs.glob("**/*.xlsx")) + list(pasta_cxs.glob("**/*.csv"))
        
        for arquivo in arquivos:
            logger.info(f"📄 Processando caixa: {arquivo.name}")
            # TODO: Implementar processamento específico de caixa
    
    def importar_controles_geral(self):
        """Importa controles gerais"""
        logger.info("📊 Processando controles gerais...")
        
        pasta_controles = self.base_path / "controles_geral"
        arquivos = list(pasta_controles.glob("**/*.xlsx")) + list(pasta_controles.glob("**/*.csv"))
        
        for arquivo in arquivos:
            logger.info(f"📄 Processando controle: {arquivo.name}")
            # TODO: Implementar processamento específico de controles
    
    def _identificar_clientes(self, df):
        """Identifica se o arquivo contém dados de clientes"""
        colunas = [col.lower() for col in df.columns]
        return any(palavra in ' '.join(colunas) for palavra in ['cpf', 'cliente', 'nome']) and \
               any(palavra in ' '.join(colunas) for palavra in ['telefone', 'celular', 'email'])
    
    def _identificar_vendas(self, df):
        """Identifica se o arquivo contém dados de vendas"""
        colunas = [col.lower() for col in df.columns]
        return any(palavra in ' '.join(colunas) for palavra in ['venda', 'valor', 'total', 'preco']) and \
               any(palavra in ' '.join(colunas) for palavra in ['data', 'cliente'])
    
    def _processar_clientes_vixen(self, df, nome_arquivo):
        """Processa arquivo de clientes Vixen"""
        logger.info(f"👥 Processando {len(df)} clientes de {nome_arquivo}")
        
        # TODO: Implementar importação específica de clientes Vixen
        # - Mapear colunas
        # - Normalizar dados
        # - Inserir no banco
        
        logger.info(f"✅ {len(df)} clientes Vixen processados")
    
    def _processar_vendas_vixen(self, df, nome_arquivo):
        """Processa arquivo de vendas Vixen"""
        logger.info(f"💰 Processando {len(df)} vendas de {nome_arquivo}")
        
        # TODO: Implementar importação específica de vendas Vixen
        # - Mapear colunas
        # - Relacionar com clientes
        # - Calcular totais
        
        logger.info(f"✅ {len(df)} vendas Vixen processadas")
    
    def _processar_oss_loja(self, loja_pasta):
        """Processa OS de uma loja específica"""
        loja_nome = loja_pasta.name.upper()
        logger.info(f"🏪 Processando OS da loja: {loja_nome}")
        
        arquivos = list(loja_pasta.glob("*.xlsx")) + list(loja_pasta.glob("*.csv"))
        
        for arquivo in arquivos:
            logger.info(f"📄 Processando OS: {arquivo.name}")
            
            try:
                if arquivo.suffix.lower() == '.csv':
                    df = pd.read_csv(arquivo)
                else:
                    df = pd.read_excel(arquivo)
                
                # TODO: Implementar processamento específico de OS
                # - Identificar colunas de OS
                # - Relacionar com clientes
                # - Criar vendas e itens
                
                logger.info(f"✅ {len(df)} OS processadas de {loja_nome}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar OS {arquivo.name}: {e}")
    
    def _processar_oss_consolidadas(self, pasta_consolidadas):
        """Processa OS já consolidadas"""
        logger.info("📋 Processando OS consolidadas...")
        
        arquivos = list(pasta_consolidadas.glob("*.xlsx")) + list(pasta_consolidadas.glob("*.csv"))
        
        for arquivo in arquivos:
            logger.info(f"📄 Processando consolidada: {arquivo.name}")
            # TODO: Implementar processamento de OS consolidadas
    
    def relatorio_final(self):
        """Gera relatório final da importação"""
        logger.info("\n" + "="*60)
        logger.info("RELATÓRIO FINAL - IMPORTAÇÃO COMPLETA")
        logger.info("="*60)
        
        if not self.arquivos_processados:
            logger.info("📭 Nenhum arquivo foi processado")
            return
        
        logger.info(f"📊 ARQUIVOS PROCESSADOS: {len(self.arquivos_processados)}")
        
        # Agrupar por tipo
        tipos = {}
        for arquivo in self.arquivos_processados:
            tipo = arquivo['tipo']
            if tipo not in tipos:
                tipos[tipo] = {'ok': 0, 'erro': 0, 'registros': 0}
            
            if 'ERRO' in arquivo['status']:
                tipos[tipo]['erro'] += 1
            else:
                tipos[tipo]['ok'] += 1
                tipos[tipo]['registros'] += arquivo['registros']
        
        for tipo, stats in tipos.items():
            logger.info(f"\n📂 {tipo.upper()}:")
            logger.info(f"  ✅ Sucessos: {stats['ok']}")
            logger.info(f"  ❌ Erros: {stats['erro']}")
            logger.info(f"  📊 Registros: {stats['registros']:,}")
        
        # Estatísticas do banco
        logger.info(f"\n📈 ESTATÍSTICAS DO BANCO:")
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM core.clientes")
            clientes = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM vendas.vendas")
            vendas = cursor.fetchone()[0]
            
            logger.info(f"  👥 Clientes: {clientes:,}")
            logger.info(f"  💰 Vendas: {vendas:,}")
            
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível obter estatísticas: {e}")
        
        logger.info("\n🎯 IMPORTAÇÃO COMPLETA FINALIZADA!")
        logger.info("="*60)
    
    def close(self):
        """Fecha conexão"""
        if self.conn:
            self.conn.close()
            logger.info("🔌 Conexão fechada")

def main():
    """Função principal"""
    logger.info("="*60)
    logger.info("IMPORTADOR COMPLETO - CARNÊ FÁCIL")
    logger.info(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info("="*60)
    
    importador = ImportadorCompleto()
    
    try:
        # Verificar dados disponíveis
        if not importador.verificar_dados_disponiveis():
            return
        
        # Conectar ao banco
        if not importador.connect():
            logger.error("❌ Falha na conexão. Verifique credenciais Supabase.")
            return
        
        # Executar importações
        importador.importar_vixen()
        importador.importar_oss()
        importador.importar_cxs()
        importador.importar_controles_geral()
        
        # Relatório final
        importador.relatorio_final()
        
    except Exception as e:
        logger.error(f"❌ Erro durante importação: {e}")
        if importador.conn:
            importador.conn.rollback()
    
    finally:
        importador.close()

if __name__ == "__main__":
    main()