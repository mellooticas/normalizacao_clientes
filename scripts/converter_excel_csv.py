#!/usr/bin/env python3
"""
Conversor de Excel para CSV - Carnê Fácil
Converte arquivos "OS NOVA*" de todas as lojas do OneDrive para CSV
"""

import os
import pandas as pd
from pathlib import Path
import shutil
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConversorExcelCSV:
    """Conversor de arquivos Excel das lojas para CSV"""
    
    def __init__(self):
        # Caminho base do OneDrive
        self.onedrive_base = Path(r"D:\OneDrive - Óticas Taty Mello\LOJAS")
        
        # Caminho destino no projeto
        self.destino_base = Path("data/originais/oss/por_loja")
        
        # Mapeamento de lojas OneDrive -> Projeto
        self.mapeamento_lojas = {
            'MAUA': 'maua',
            'SUZANO': 'suzano', 
            'SUZANO2': 'suzano2',
            'PERUS': 'perus',
            'RIO_PEQUENO': 'rio_pequeno',
            'SAO_MATEUS': 'sao_mateus'
        }
        
        self.arquivos_convertidos = []
        self.arquivos_erro = []
    
    def verificar_onedrive(self):
        """Verifica se o caminho do OneDrive existe"""
        if not self.onedrive_base.exists():
            logger.error(f"❌ Caminho OneDrive não encontrado: {self.onedrive_base}")
            logger.error("💡 Verifique se o OneDrive está sincronizado")
            return False
        
        logger.info(f"✅ OneDrive encontrado: {self.onedrive_base}")
        return True
    
    def listar_lojas_disponiveis(self):
        """Lista lojas disponíveis no OneDrive com busca recursiva"""
        logger.info("🔍 Verificando lojas disponíveis no OneDrive...")
        
        lojas_encontradas = []
        
        for loja_onedrive, loja_projeto in self.mapeamento_lojas.items():
            pasta_loja = self.onedrive_base / loja_onedrive
            
            if pasta_loja.exists():
                # Buscar recursivamente por arquivos "OS NOVA"
                arquivos_os_nova = []
                
                try:
                    # Busca recursiva em todas as subpastas
                    for arquivo in pasta_loja.rglob("*"):
                        if (arquivo.is_file() and 
                            'OS NOVA' in arquivo.name.upper() and 
                            arquivo.suffix.lower() in ['.xlsx', '.xls', '.xlsm']):
                            arquivos_os_nova.append(arquivo)
                except Exception as e:
                    logger.error(f"❌ Erro ao buscar arquivos em {loja_onedrive}: {e}")
                    
                lojas_encontradas.append({
                    'loja': loja_onedrive,
                    'pasta': pasta_loja,
                    'arquivos_os_nova': arquivos_os_nova
                })
                
                logger.info(f"  ✅ {loja_onedrive}: {len(arquivos_os_nova)} arquivo(s) 'OS NOVA'")
            else:
                logger.warning(f"  ❌ {loja_onedrive}: Loja não encontrada")
        
        return lojas_encontradas
    
    def converter_loja(self, info_loja):
        """Converte arquivos de uma loja específica"""
        loja_nome = info_loja['loja']
        arquivos_os_nova = info_loja['arquivos_os_nova']
        
        logger.info(f"🔄 Convertendo loja: {loja_nome}")
        
        # Pasta destino
        loja_projeto = self.mapeamento_lojas[loja_nome]
        pasta_destino = self.destino_base / loja_projeto
        pasta_destino.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📄 Encontrados {len(arquivos_os_nova)} arquivos para converter")
        
        arquivos_processados = []
        
        for arquivo_excel in arquivos_os_nova:
            resultado = self._converter_arquivo(arquivo_excel, pasta_destino, loja_nome)
            if resultado:
                arquivos_processados.append(resultado)
                
        return arquivos_processados
    
    def _converter_arquivo(self, arquivo_excel, pasta_destino, loja_nome):
        """Converte um arquivo Excel específico para CSV"""
        nome_original = arquivo_excel.name
        nome_csv = arquivo_excel.stem + ".csv"
        arquivo_destino = pasta_destino / nome_csv
        
        logger.info(f"  📝 Convertendo: {nome_original}")
        
        try:
            # Ler Excel com diferentes engines
            df = None
            
            try:
                # Primeiro tentar com openpyxl (para .xlsx/.xlsm)
                if arquivo_excel.suffix.lower() in ['.xlsx', '.xlsm']:
                    df = pd.read_excel(arquivo_excel, engine='openpyxl')
                else:
                    # Para .xls, usar xlrd
                    df = pd.read_excel(arquivo_excel, engine='xlrd')
                    
            except Exception as e:
                logger.warning(f"    ⚠️ Erro com engine padrão: {e}")
                return None
            
            # Verificar se tem dados
            if df is None or df.empty:
                logger.warning(f"    ⚠️ Arquivo vazio: {nome_original}")
                return None
            
            # Limpar dados básicos
            df = df.dropna(how='all')  # Remove linhas completamente vazias
            df = df.dropna(axis=1, how='all')  # Remove colunas completamente vazias
            
            # Salvar como CSV
            df.to_csv(arquivo_destino, index=False, encoding='utf-8-sig')
            
            # Informações do arquivo
            info_arquivo = {
                'loja': loja_nome,
                'arquivo_original': nome_original,
                'arquivo_csv': nome_csv,
                'caminho_destino': str(arquivo_destino),
                'linhas': len(df),
                'colunas': len(df.columns),
                'tamanho_mb': round(arquivo_destino.stat().st_size / 1024 / 1024, 2),
                'status': 'SUCESSO'
            }
            
            self.arquivos_convertidos.append(info_arquivo)
            
            logger.info(f"    ✅ Convertido: {len(df)} linhas, {len(df.columns)} colunas")
            return info_arquivo
            
        except Exception as e:
            erro_info = {
                'loja': loja_nome,
                'arquivo_original': nome_original,
                'erro': str(e),
                'status': 'ERRO'
            }
            
            self.arquivos_erro.append(erro_info)
            logger.error(f"    ❌ Erro ao converter {nome_original}: {e}")
            return None
            logger.error(f"    ❌ Erro: {str(e)[:60]}...")
    
    def gerar_relatorio(self):
        """Gera relatório da conversão"""
        logger.info("\n" + "="*70)
        logger.info("RELATÓRIO DE CONVERSÃO EXCEL → CSV")
        logger.info("="*70)
        
        total_sucessos = len(self.arquivos_convertidos)
        total_erros = len(self.arquivos_erro)
        total_arquivos = total_sucessos + total_erros
        
        logger.info(f"📊 RESUMO GERAL:")
        logger.info(f"  • Total de arquivos: {total_arquivos}")
        logger.info(f"  • Convertidos com sucesso: {total_sucessos}")
        logger.info(f"  • Erros: {total_erros}")
        
        if total_sucessos > 0:
            logger.info(f"\n✅ ARQUIVOS CONVERTIDOS ({total_sucessos}):")
            logger.info("-" * 50)
            
            # Agrupar por loja
            por_loja = {}
            total_linhas = 0
            total_tamanho = 0
            
            for arquivo in self.arquivos_convertidos:
                loja = arquivo['loja']
                if loja not in por_loja:
                    por_loja[loja] = []
                por_loja[loja].append(arquivo)
                total_linhas += arquivo['linhas']
                total_tamanho += arquivo['tamanho_mb']
            
            for loja, arquivos in por_loja.items():
                logger.info(f"\n📂 {loja} ({len(arquivos)} arquivo(s)):")
                
                for arquivo in arquivos:
                    logger.info(f"  • {arquivo['arquivo_csv']}")
                    logger.info(f"    📍 {arquivo['caminho_destino']}")
                    logger.info(f"    📊 {arquivo['linhas']:,} linhas, {arquivo['colunas']} colunas")
                    logger.info(f"    💾 {arquivo['tamanho_mb']} MB")
            
            logger.info(f"\n📈 TOTAIS:")
            logger.info(f"  • Registros: {total_linhas:,} linhas")
            logger.info(f"  • Tamanho: {total_tamanho:.1f} MB")
        
        if total_erros > 0:
            logger.info(f"\n❌ ERROS ({total_erros}):")
            logger.info("-" * 30)
            
            for erro in self.arquivos_erro:
                logger.info(f"  • {erro['loja']}: {erro['arquivo_original']}")
                logger.info(f"    ❌ {erro['erro']}")
        
        logger.info(f"\n🚀 PRÓXIMOS PASSOS:")
        logger.info("-" * 30)
        
        if total_sucessos > 0:
            logger.info("  1. Execute: python analisar_dados_originais.py")
            logger.info("  2. Verifique os dados convertidos")
            logger.info("  3. Execute: python import_dados_completos.py")
            logger.info("  4. ✅ Dados importados para Supabase!")
        else:
            logger.info("  1. Verifique os erros acima")
            logger.info("  2. Confirme localização dos arquivos")
            logger.info("  3. Execute novamente o conversor")
        
        logger.info("\n" + "="*70)
    
    def executar_conversao_completa(self):
        """Executa conversão completa de todas as lojas"""
        logger.info("🚀 INICIANDO CONVERSÃO COMPLETA")
        logger.info(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        logger.info("="*70)
        
        # Verificar OneDrive
        if not self.verificar_onedrive():
            return False
        
        # Listar lojas
        lojas_disponiveis = self.listar_lojas_disponiveis()
        
        if not lojas_disponiveis:
            logger.error("❌ Nenhuma loja com arquivos 'OS NOVA' encontrada")
            return False
        
        logger.info(f"\n🎯 Processando {len(lojas_disponiveis)} loja(s)...")
        
        # Converter cada loja
        for info_loja in lojas_disponiveis:
            self.converter_loja(info_loja)
        
        # Gerar relatório
        self.gerar_relatorio()
        
        return len(self.arquivos_convertidos) > 0

def main():
    """Função principal"""
    conversor = ConversorExcelCSV()
    
    try:
        sucesso = conversor.executar_conversao_completa()
        
        if sucesso:
            logger.info("🎉 Conversão concluída com sucesso!")
        else:
            logger.error("❌ Conversão falhou ou nenhum arquivo processado")
    
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()