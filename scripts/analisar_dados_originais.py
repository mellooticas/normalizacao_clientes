#!/usr/bin/env python3
"""
Analisador de Dados Originais - Carnê Fácil
Varre as pastas de dados originais e analisa o conteúdo encontrado
"""

import os
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnalisadorDadosOriginais:
    """Analisa dados originais nas pastas organizadas"""
    
    def __init__(self, base_path="data/originais"):
        self.base_path = Path(base_path)
        self.arquivos_encontrados = {
            'vixen': [],
            'oss': [],
            'cxs': [],
            'controles_geral': []
        }
        self.estatisticas = {}
        
    def varrer_pastas(self):
        """Varre todas as pastas procurando arquivos"""
        logger.info("🔍 Iniciando varredura das pastas de dados originais...")
        
        for tipo in ['vixen', 'oss', 'cxs', 'controles_geral']:
            pasta = self.base_path / tipo
            if pasta.exists():
                self._varrer_pasta_tipo(pasta, tipo)
            else:
                logger.warning(f"📁 Pasta {tipo} não encontrada")
        
        self._gerar_relatorio()
    
    def _varrer_pasta_tipo(self, pasta, tipo):
        """Varre uma pasta específica"""
        logger.info(f"📂 Analisando pasta: {tipo}")
        
        arquivos = []
        
        # Buscar arquivos recursivamente
        for arquivo in pasta.rglob("*"):
            if arquivo.is_file() and arquivo.suffix.lower() in ['.xlsx', '.xls', '.csv', '.xlsm']:
                info_arquivo = self._analisar_arquivo(arquivo, tipo)
                if info_arquivo:
                    arquivos.append(info_arquivo)
        
        self.arquivos_encontrados[tipo] = arquivos
        logger.info(f"  ✅ Encontrados {len(arquivos)} arquivos em {tipo}")
    
    def _analisar_arquivo(self, arquivo, tipo):
        """Analisa um arquivo específico"""
        try:
            # Informações básicas
            stat = arquivo.stat()
            info = {
                'nome': arquivo.name,
                'caminho': str(arquivo.relative_to(self.base_path)),
                'tamanho': self._formatar_tamanho(stat.st_size),
                'modificado': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M'),
                'tipo': tipo,
                'extensao': arquivo.suffix.lower()
            }
            
            # Tentar analisar conteúdo
            try:
                if arquivo.suffix.lower() == '.csv':
                    df = pd.read_csv(arquivo, nrows=5)  # Apenas primeiras linhas
                else:
                    df = pd.read_excel(arquivo, nrows=5)  # Apenas primeiras linhas
                
                info.update({
                    'linhas_estimadas': self._estimar_linhas(arquivo),
                    'colunas': len(df.columns),
                    'colunas_nomes': list(df.columns)[:10],  # Primeiras 10 colunas
                    'status': 'OK'
                })
                
                # Identificar tipo de conteúdo
                info['conteudo_tipo'] = self._identificar_conteudo(df, arquivo.name)
                
            except Exception as e:
                info.update({
                    'status': f'ERRO: {str(e)[:50]}...',
                    'conteudo_tipo': 'DESCONHECIDO'
                })
            
            return info
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar {arquivo}: {e}")
            return None
    
    def _estimar_linhas(self, arquivo):
        """Estima número de linhas do arquivo"""
        try:
            if arquivo.suffix.lower() == '.csv':
                with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                    return sum(1 for _ in f) - 1  # -1 para header
            else:
                # Para Excel, usamos pandas para contar
                df = pd.read_excel(arquivo)
                return len(df)
        except:
            return "N/A"
    
    def _identificar_conteudo(self, df, nome_arquivo):
        """Identifica o tipo de conteúdo baseado nas colunas"""
        colunas = [col.lower() for col in df.columns]
        nome = nome_arquivo.lower()
        
        # Padrões de identificação
        if any(palavra in ' '.join(colunas) for palavra in ['cpf', 'cliente', 'nome']):
            if any(palavra in ' '.join(colunas) for palavra in ['telefone', 'celular', 'email']):
                return 'CLIENTES'
        
        if any(palavra in ' '.join(colunas) for palavra in ['os', 'ordem', 'servico', 'atendimento']):
            return 'ORDENS_SERVICO'
        
        if any(palavra in ' '.join(colunas) for palavra in ['venda', 'valor', 'total', 'preco']):
            if any(palavra in ' '.join(colunas) for palavra in ['data', 'produto']):
                return 'VENDAS'
        
        if any(palavra in ' '.join(colunas) for palavra in ['caixa', 'pagamento', 'dinheiro']):
            return 'FINANCEIRO'
        
        if any(palavra in ' '.join(colunas) for palavra in ['estoque', 'produto', 'quantidade']):
            return 'INVENTARIO'
        
        if 'vixen' in nome:
            return 'VIXEN_EXPORT'
        
        return 'OUTROS'
    
    def _formatar_tamanho(self, bytes):
        """Formata tamanho do arquivo"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} TB"
    
    def _gerar_relatorio(self):
        """Gera relatório completo da análise"""
        logger.info("\n" + "="*80)
        logger.info("RELATÓRIO DE ANÁLISE DOS DADOS ORIGINAIS")
        logger.info("="*80)
        
        total_arquivos = sum(len(arquivos) for arquivos in self.arquivos_encontrados.values())
        
        if total_arquivos == 0:
            logger.info("📭 NENHUM ARQUIVO ENCONTRADO")
            logger.info("\n🔧 INSTRUÇÕES:")
            logger.info("1. Coloque os arquivos Excel/CSV nas pastas apropriadas:")
            logger.info("   • data/originais/vixen/ - Dados do sistema Vixen")
            logger.info("   • data/originais/oss/ - Ordens de Serviço")
            logger.info("   • data/originais/cxs/ - Dados de Caixa")
            logger.info("   • data/originais/controles_geral/ - Controles gerais")
            logger.info("2. Execute novamente: python analisar_dados_originais.py")
            return
        
        logger.info(f"📊 TOTAL DE ARQUIVOS ENCONTRADOS: {total_arquivos}")
        
        # Relatório por tipo
        for tipo, arquivos in self.arquivos_encontrados.items():
            if arquivos:
                logger.info(f"\n📂 {tipo.upper()} ({len(arquivos)} arquivos):")
                logger.info("-" * 50)
                
                # Agrupar por tipo de conteúdo
                tipos_conteudo = {}
                for arquivo in arquivos:
                    conteudo = arquivo.get('conteudo_tipo', 'OUTROS')
                    if conteudo not in tipos_conteudo:
                        tipos_conteudo[conteudo] = []
                    tipos_conteudo[conteudo].append(arquivo)
                
                for conteudo, lista_arquivos in tipos_conteudo.items():
                    logger.info(f"\n  📋 {conteudo} ({len(lista_arquivos)} arquivos):")
                    
                    for arquivo in lista_arquivos:
                        linhas = arquivo.get('linhas_estimadas', 'N/A')
                        colunas = arquivo.get('colunas', 'N/A')
                        status = arquivo.get('status', 'N/A')
                        
                        logger.info(f"    • {arquivo['nome']}")
                        logger.info(f"      📍 {arquivo['caminho']}")
                        logger.info(f"      📊 {linhas} linhas, {colunas} colunas")
                        logger.info(f"      💾 {arquivo['tamanho']} - {status}")
                        
                        if arquivo.get('colunas_nomes'):
                            colunas_str = ', '.join(arquivo['colunas_nomes'][:5])
                            if len(arquivo['colunas_nomes']) > 5:
                                colunas_str += "..."
                            logger.info(f"      🏷️  Colunas: {colunas_str}")
        
        # Resumo de tipos de conteúdo
        logger.info(f"\n📈 RESUMO POR TIPO DE CONTEÚDO:")
        logger.info("-" * 40)
        
        todos_arquivos = []
        for arquivos in self.arquivos_encontrados.values():
            todos_arquivos.extend(arquivos)
        
        tipos_resumo = {}
        for arquivo in todos_arquivos:
            conteudo = arquivo.get('conteudo_tipo', 'OUTROS')
            if conteudo not in tipos_resumo:
                tipos_resumo[conteudo] = 0
            tipos_resumo[conteudo] += 1
        
        for conteudo, quantidade in sorted(tipos_resumo.items()):
            logger.info(f"  📋 {conteudo}: {quantidade} arquivo(s)")
        
        # Próximos passos
        logger.info(f"\n🚀 PRÓXIMOS PASSOS:")
        logger.info("-" * 30)
        
        if any(arquivo.get('conteudo_tipo') == 'CLIENTES' for arquivos in self.arquivos_encontrados.values() for arquivo in arquivos):
            logger.info("  ✅ Dados de clientes encontrados")
        else:
            logger.info("  ⚠️  Dados de clientes NÃO encontrados")
        
        if any(arquivo.get('conteudo_tipo') in ['VENDAS', 'ORDENS_SERVICO'] for arquivos in self.arquivos_encontrados.values() for arquivo in arquivos):
            logger.info("  ✅ Dados de vendas/OS encontrados")
        else:
            logger.info("  ⚠️  Dados de vendas/OS NÃO encontrados")
        
        logger.info("\n🔄 Para prosseguir com a importação:")
        logger.info("  1. Valide se todos os arquivos necessários estão presentes")
        logger.info("  2. Execute: python import_dados_completos.py")
        
        logger.info("\n" + "="*80)

def main():
    """Função principal"""
    analisador = AnalisadorDadosOriginais()
    analisador.varrer_pastas()

if __name__ == "__main__":
    main()