#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalização correta dos dados de carnê - Valor das parcelas
Lógica correta: valor_total / numero_parcelas = valor_unitario_parcela
"""

import pandas as pd
import os
import json
from datetime import datetime

def normalizar_dados_carne_final():
    """Normaliza os dados de carnê com cálculo correto das parcelas"""
    
    print("🏧 NORMALIZAÇÃO CORRETA DOS DADOS DE CARNÊ")
    print("=" * 50)
    
    # Pastas
    pasta_base = r"d:\projetos\carne_facil\carne_facil\data\originais\cxs\extraidos_corrigidos"
    pasta_analises = r"d:\projetos\carne_facil\carne_facil\_analises"
    os.makedirs(pasta_analises, exist_ok=True)
    
    # Tipos de carnê para processar
    tipos_carne = {
        'entrega_carne': {
            'descricao': 'Carnês entregues',
            'colunas_necessarias': ['os', 'parcelas', 'valor_total']
        },
        'recebimento_carne': {
            'descricao': 'Recebimentos de carnê',
            'colunas_necessarias': ['os', 'valor_parcela', 'n_parcela']
        }
    }
    
    relatorio_normalizacao = {
        'timestamp': datetime.now().isoformat(),
        'tipos_processados': {},
        'logica_calculo': 'valor_total / numero_parcelas = valor_unitario_parcela',
        'validacoes_realizadas': []
    }
    
    for tipo_carne, config in tipos_carne.items():
        print(f"\n🔄 PROCESSANDO: {tipo_carne.upper()}")
        print(f"📋 {config['descricao']}")
        print("-" * 40)
        
        pasta_tipo = os.path.join(pasta_base, tipo_carne)
        
        if not os.path.exists(pasta_tipo):
            print(f"❌ Pasta não encontrada: {pasta_tipo}")
            continue
        
        arquivos_csv = [f for f in os.listdir(pasta_tipo) if f.endswith('.csv')]
        
        tipo_info = {
            'arquivos_processados': 0,
            'registros_processados': 0,
            'calculos_realizados': 0,
            'inconsistencias_encontradas': 0,
            'estatisticas_valor': {},
            'problemas_identificados': []
        }
        
        # Processar cada arquivo
        for arquivo in sorted(arquivos_csv):
            caminho_arquivo = os.path.join(pasta_tipo, arquivo)
            
            try:
                print(f"  📄 {arquivo}")
                
                df = pd.read_csv(caminho_arquivo)
                registros_originais = len(df)
                
                if tipo_carne == 'entrega_carne':
                    # ENTREGA_CARNE: Calcular valor unitário da parcela
                    if all(col in df.columns for col in ['parcelas', 'valor_total']):
                        # Garantir que os valores são numéricos
                        df['parcelas'] = pd.to_numeric(df['parcelas'], errors='coerce')
                        df['valor_total'] = pd.to_numeric(df['valor_total'], errors='coerce')
                        
                        # Calcular valor unitário da parcela (LÓGICA CORRETA)
                        # valor_total / numero_parcelas = valor_unitario_parcela
                        mask_valido = (df['parcelas'] > 0) & (df['valor_total'] > 0)
                        
                        df.loc[mask_valido, 'valor_unitario_parcela'] = (
                            df.loc[mask_valido, 'valor_total'] / df.loc[mask_valido, 'parcelas']
                        ).round(2)
                        
                        # Adicionar informações complementares
                        df['tipo_calculo'] = 'valor_total_dividido_por_parcelas'
                        df['formula_aplicada'] = 'valor_total / parcelas = valor_unitario_parcela'
                        
                        # Verificar inconsistências
                        inconsistencias = 0
                        for idx, row in df.iterrows():
                            if pd.notna(row['parcelas']) and pd.notna(row['valor_total']):
                                if row['parcelas'] <= 0:
                                    inconsistencias += 1
                                    tipo_info['problemas_identificados'].append(
                                        f"{arquivo}: OS {row.get('os', 'N/A')} - Parcelas <= 0: {row['parcelas']}"
                                    )
                                elif row['valor_total'] <= 0:
                                    inconsistencias += 1
                                    tipo_info['problemas_identificados'].append(
                                        f"{arquivo}: OS {row.get('os', 'N/A')} - Valor total <= 0: {row['valor_total']}"
                                    )
                        
                        tipo_info['inconsistencias_encontradas'] += inconsistencias
                        tipo_info['calculos_realizados'] += mask_valido.sum()
                        
                        print(f"    ✅ {mask_valido.sum()} cálculos realizados")
                        if inconsistencias > 0:
                            print(f"    ⚠️  {inconsistencias} inconsistências encontradas")
                
                elif tipo_carne == 'recebimento_carne':
                    # RECEBIMENTO_CARNE: Validar se valor_parcela está correto
                    if all(col in df.columns for col in ['valor_parcela', 'n_parcela']):
                        df['valor_parcela'] = pd.to_numeric(df['valor_parcela'], errors='coerce')
                        df['n_parcela'] = pd.to_numeric(df['n_parcela'], errors='coerce')
                        
                        # Aqui o valor_parcela já deve estar correto (é o que foi recebido)
                        # Apenas validamos e adicionamos informações
                        mask_valido = (df['valor_parcela'] > 0) & (df['n_parcela'] > 0)
                        
                        df['tipo_registro'] = 'recebimento_parcela_individual'
                        df['validacao'] = 'valor_parcela_recebido'
                        
                        tipo_info['calculos_realizados'] += mask_valido.sum()
                        
                        print(f"    ✅ {mask_valido.sum()} registros validados")
                
                # Salvar arquivo atualizado
                df.to_csv(caminho_arquivo, index=False)
                
                tipo_info['arquivos_processados'] += 1
                tipo_info['registros_processados'] += registros_originais
                
                # Estatísticas de valor
                if tipo_carne == 'entrega_carne' and 'valor_unitario_parcela' in df.columns:
                    valores_validos = df['valor_unitario_parcela'].dropna()
                    if len(valores_validos) > 0:
                        tipo_info['estatisticas_valor'] = {
                            'valor_parcela_min': float(valores_validos.min()),
                            'valor_parcela_max': float(valores_validos.max()),
                            'valor_parcela_medio': float(valores_validos.mean()),
                            'total_parcelas_calculadas': len(valores_validos)
                        }
                
            except Exception as e:
                erro_msg = f"Erro ao processar {arquivo}: {str(e)}"
                print(f"    ❌ {erro_msg}")
                tipo_info['problemas_identificados'].append(erro_msg)
        
        relatorio_normalizacao['tipos_processados'][tipo_carne] = tipo_info
        
        print(f"\n✅ {tipo_carne.upper()} CONCLUÍDO:")
        print(f"   📄 {tipo_info['arquivos_processados']} arquivos processados")
        print(f"   📊 {tipo_info['registros_processados']:,} registros")
        print(f"   🧮 {tipo_info['calculos_realizados']:,} cálculos realizados")
        if tipo_info['inconsistencias_encontradas'] > 0:
            print(f"   ⚠️  {tipo_info['inconsistencias_encontradas']} inconsistências encontradas")
    
    # Validações cruzadas
    print(f"\n🔍 VALIDAÇÕES CRUZADAS")
    print("-" * 40)
    
    # Comparar dados entre entrega_carne e recebimento_carne
    try:
        # Carregar dados consolidados
        entrega_path = os.path.join(pasta_base, 'entrega_carne', 'entrega_carne_todas_lojas.csv')
        recebimento_path = os.path.join(pasta_base, 'recebimento_carne', 'recebimento_carne_todas_lojas.csv')
        
        if os.path.exists(entrega_path) and os.path.exists(recebimento_path):
            df_entrega = pd.read_csv(entrega_path)
            df_recebimento = pd.read_csv(recebimento_path)
            
            # OS em comum
            os_entrega = set(df_entrega['os'].dropna())
            os_recebimento = set(df_recebimento['os'].dropna())
            os_comuns = os_entrega.intersection(os_recebimento)
            
            validacao_cruzada = {
                'os_apenas_entrega': len(os_entrega - os_recebimento),
                'os_apenas_recebimento': len(os_recebimento - os_entrega),
                'os_em_ambos': len(os_comuns),
                'percentual_cobertura': round(len(os_comuns) / max(len(os_entrega), 1) * 100, 2)
            }
            
            relatorio_normalizacao['validacao_cruzada'] = validacao_cruzada
            
            print(f"📋 OS apenas em entrega: {validacao_cruzada['os_apenas_entrega']}")
            print(f"📋 OS apenas em recebimento: {validacao_cruzada['os_apenas_recebimento']}")
            print(f"📋 OS em ambos: {validacao_cruzada['os_em_ambos']}")
            print(f"📋 Cobertura: {validacao_cruzada['percentual_cobertura']}%")
        
    except Exception as e:
        print(f"⚠️  Erro na validação cruzada: {str(e)}")
    
    # Salvar relatório
    caminho_relatorio = os.path.join(pasta_analises, "normalizacao_carne_corrigida.json")
    with open(caminho_relatorio, 'w', encoding='utf-8') as f:
        json.dump(relatorio_normalizacao, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 NORMALIZAÇÃO CONCLUÍDA!")
    print(f"📊 Lógica aplicada: VALOR_TOTAL ÷ PARCELAS = VALOR_UNITÁRIO")
    print(f"💾 Relatório salvo: {caminho_relatorio}")
    
    # Exemplo prático
    print(f"\n💡 EXEMPLO PRÁTICO:")
    print(f"   OS 4098: R$ 399,00 ÷ 3 parcelas = R$ 133,00 por parcela")
    print(f"   OS 4033: R$ 1.884,00 ÷ 6 parcelas = R$ 314,00 por parcela")

if __name__ == "__main__":
    normalizar_dados_carne_final()