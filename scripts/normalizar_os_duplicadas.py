#!/usr/bin/env python3
"""
Normalizador de OS Duplicadas
=============================

Consolida registros duplicados por OS N°, unindo todos os dados disponíveis
para criar registros únicos com máximo de informações possível.

Estratégia:
- Agrupa por OS N°
- Para cada campo, escolhe o valor mais completo/recente
- Prioriza dados não vazios
- Combina informações fragmentadas
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime
import re

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class NormalizadorOS:
    def __init__(self):
        self.input_dir = Path("data/originais/oss/consolidadas")
        self.output_dir = Path("data/originais/oss/normalizadas")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.resultados = []
        self.estatisticas = {}
    
    def normalizar_arquivo(self, arquivo_consolidado):
        """Normaliza um arquivo consolidado, removendo duplicatas de OS"""
        loja_nome = arquivo_consolidado.stem.replace('_consolidado', '')
        logger.info(f"🔄 Normalizando loja: {loja_nome}")
        
        try:
            # Carregar dados
            df = pd.read_csv(arquivo_consolidado, encoding='utf-8-sig')
            
            registros_iniciais = len(df)
            logger.info(f"   📊 Registros iniciais: {registros_iniciais}")
            
            # Verificar se tem coluna OS N°
            if 'OS N°' not in df.columns:
                logger.error(f"   ❌ Coluna 'OS N°' não encontrada em {loja_nome}")
                return None
            
            # Remover registros sem OS N°
            df_limpo = df.dropna(subset=['OS N°'])
            df_limpo = df_limpo[df_limpo['OS N°'] != '']
            
            logger.info(f"   📊 Registros com OS válida: {len(df_limpo)}")
            
            # Agrupar por OS N° e consolidar
            logger.info(f"   🔄 Consolidando registros duplicados...")
            
            df_normalizado = self.consolidar_duplicatas(df_limpo, loja_nome)
            
            registros_finais = len(df_normalizado)
            duplicatas_removidas = registros_iniciais - registros_finais
            
            # Estatísticas
            stats = {
                'loja': loja_nome,
                'registros_iniciais': registros_iniciais,
                'registros_finais': registros_finais,
                'duplicatas_removidas': duplicatas_removidas,
                'taxa_consolidacao': round((duplicatas_removidas / registros_iniciais) * 100, 2) if registros_iniciais > 0 else 0,
                'os_unicas': len(df_normalizado['OS N°'].unique()),
                'arquivo_saida': f"{loja_nome}_normalizado.csv"
            }
            
            self.estatisticas[loja_nome] = stats
            
            # Salvar arquivo normalizado
            arquivo_saida = self.output_dir / stats['arquivo_saida']
            df_normalizado.to_csv(arquivo_saida, index=False, encoding='utf-8-sig')
            
            logger.info(f"   ✅ Normalizado: {registros_finais} registros únicos")
            logger.info(f"   📉 Duplicatas removidas: {duplicatas_removidas} ({stats['taxa_consolidacao']}%)")
            logger.info(f"   💾 Salvo em: {stats['arquivo_saida']}")
            
            return stats
            
        except Exception as e:
            logger.error(f"   ❌ Erro ao normalizar {loja_nome}: {e}")
            return None
    
    def consolidar_duplicatas(self, df, loja_nome):
        """Consolida registros duplicados por OS N°"""
        
        def consolidar_grupo(grupo):
            """Consolida um grupo de registros da mesma OS"""
            if len(grupo) == 1:
                return grupo.iloc[0]
            
            # Criar registro consolidado
            registro_consolidado = {}
            
            for coluna in grupo.columns:
                valores = grupo[coluna].dropna()
                valores = valores[valores != '']
                valores = valores[valores != 0]
                
                if len(valores) == 0:
                    registro_consolidado[coluna] = None
                elif len(valores) == 1:
                    registro_consolidado[coluna] = valores.iloc[0]
                else:
                    # Múltiplos valores - escolher o melhor
                    registro_consolidado[coluna] = self.escolher_melhor_valor(valores, coluna)
            
            return pd.Series(registro_consolidado)
        
        # Agrupar por OS N° e consolidar
        df_normalizado = df.groupby('OS N°').apply(consolidar_grupo).reset_index(drop=True)
        
        return df_normalizado
    
    def escolher_melhor_valor(self, valores, coluna):
        """Escolhe o melhor valor entre múltiplos valores para uma coluna"""
        
        # Remover valores que são claramente inválidos
        valores_limpos = []
        for val in valores:
            val_str = str(val).strip()
            if val_str and val_str.lower() not in ['nan', 'none', 'null', '0', '0.0']:
                valores_limpos.append(val)
        
        if not valores_limpos:
            return None
        
        if len(valores_limpos) == 1:
            return valores_limpos[0]
        
        # Estratégias específicas por tipo de coluna
        coluna_lower = coluna.lower()
        
        # Para campos de texto (nome, endereço, etc)
        if any(campo in coluna_lower for campo in ['nome', 'end', 'bairro', 'email']):
            # Escolher o mais longo (mais completo)
            return max(valores_limpos, key=lambda x: len(str(x)))
        
        # Para campos numéricos (CPF, RG, CEP, telefone)
        elif any(campo in coluna_lower for campo in ['cpf', 'rg', 'cep', 'telefone', 'celular']):
            # Escolher o mais completo (mais dígitos)
            valores_numericos = []
            for val in valores_limpos:
                digits = re.sub(r'\D', '', str(val))
                if digits:
                    valores_numericos.append((val, len(digits)))
            
            if valores_numericos:
                return max(valores_numericos, key=lambda x: x[1])[0]
        
        # Para datas
        elif any(campo in coluna_lower for campo in ['data', 'nasc', 'entr']):
            # Escolher a data mais recente válida
            datas_validas = []
            for val in valores_limpos:
                try:
                    if isinstance(val, (int, float)) and val > 40000:  # Excel date
                        datas_validas.append((val, val))
                    elif pd.to_datetime(val, errors='coerce') is not pd.NaT:
                        datas_validas.append((val, pd.to_datetime(val)))
                except:
                    continue
            
            if datas_validas:
                return max(datas_validas, key=lambda x: x[1])[0]
        
        # Para valores monetários
        elif any(campo in coluna_lower for campo in ['valor', 'total', 'sinal', 'resta']):
            # Escolher o maior valor válido
            valores_numericos = []
            for val in valores_limpos:
                try:
                    num_val = float(str(val).replace(',', '.'))
                    if num_val > 0:
                        valores_numericos.append((val, num_val))
                except:
                    continue
            
            if valores_numericos:
                return max(valores_numericos, key=lambda x: x[1])[0]
        
        # Default: escolher o primeiro valor não vazio
        return valores_limpos[0]
    
    def processar_todas_lojas(self):
        """Processa todas as lojas consolidadas"""
        logger.info("🚀 INICIANDO NORMALIZAÇÃO DE OS DUPLICADAS")
        logger.info(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        logger.info("=" * 70)
        
        if not self.input_dir.exists():
            logger.error(f"❌ Diretório não encontrado: {self.input_dir}")
            return
        
        # Buscar arquivos consolidados
        arquivos_consolidados = list(self.input_dir.glob("*_consolidado.csv"))
        
        if not arquivos_consolidados:
            logger.error("❌ Nenhum arquivo consolidado encontrado")
            return
        
        logger.info(f"📂 Encontrados {len(arquivos_consolidados)} arquivo(s) consolidado(s)")
        logger.info("")
        
        # Processar cada arquivo
        for arquivo in sorted(arquivos_consolidados):
            resultado = self.normalizar_arquivo(arquivo)
            if resultado:
                self.resultados.append(resultado)
            logger.info("")
        
        self.gerar_relatorio()
    
    def gerar_relatorio(self):
        """Gera relatório da normalização"""
        logger.info("=" * 70)
        logger.info("📊 RELATÓRIO DE NORMALIZAÇÃO DE OS")
        logger.info("=" * 70)
        
        if not self.resultados:
            logger.error("❌ Nenhuma loja foi normalizada com sucesso")
            return
        
        logger.info(f"🏪 Lojas normalizadas: {len(self.resultados)}")
        
        total_iniciais = sum(r['registros_iniciais'] for r in self.resultados)
        total_finais = sum(r['registros_finais'] for r in self.resultados)
        total_duplicatas = sum(r['duplicatas_removidas'] for r in self.resultados)
        taxa_geral = round((total_duplicatas / total_iniciais) * 100, 2) if total_iniciais > 0 else 0
        
        logger.info(f"📊 Registros iniciais: {total_iniciais:,}")
        logger.info(f"📊 Registros finais: {total_finais:,}")
        logger.info(f"📉 Duplicatas consolidadas: {total_duplicatas:,} ({taxa_geral}%)")
        
        logger.info(f"\n✅ RESULTADOS POR LOJA:")
        logger.info("-" * 50)
        
        for resultado in sorted(self.resultados, key=lambda x: x['duplicatas_removidas'], reverse=True):
            logger.info(f"\n🏪 {resultado['loja']}:")
            logger.info(f"   📊 Inicial: {resultado['registros_iniciais']:,} → Final: {resultado['registros_finais']:,}")
            logger.info(f"   📉 Duplicatas: {resultado['duplicatas_removidas']:,} ({resultado['taxa_consolidacao']}%)")
            logger.info(f"   🎯 OS únicas: {resultado['os_unicas']:,}")
            logger.info(f"   📍 Arquivo: {resultado['arquivo_saida']}")
        
        logger.info(f"\n📁 ARQUIVOS NORMALIZADOS SALVOS EM:")
        logger.info(f"   📍 {self.output_dir}")
        
        logger.info(f"\n🎯 MELHORES CONSOLIDAÇÕES:")
        top_consolidacoes = sorted(self.resultados, key=lambda x: x['taxa_consolidacao'], reverse=True)[:3]
        for i, resultado in enumerate(top_consolidacoes, 1):
            logger.info(f"   {i}. {resultado['loja']}: {resultado['taxa_consolidacao']}% consolidação")
        
        logger.info(f"\n🚀 PRÓXIMOS PASSOS:")
        logger.info("-" * 30)
        logger.info("   1. Revisar dados normalizados")
        logger.info("   2. Validar qualidade da consolidação")
        logger.info("   3. Importar para Supabase")
        logger.info("   4. Criar dashboard com dados limpos")
        
        logger.info("\n" + "=" * 70)
        logger.info("🎉 Normalização concluída! OS duplicadas consolidadas com sucesso!")

def main():
    normalizador = NormalizadorOS()
    normalizador.processar_todas_lojas()

if __name__ == "__main__":
    main()