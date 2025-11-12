#!/usr/bin/env python3
"""
Análise completa dos canais de aquisição baseada na lista fornecida
"""

import json
import uuid
from collections import defaultdict

def analisar_canais_completos():
    """Analisa e categoriza todos os 100 canais de aquisição"""
    
    print("📋 ANÁLISE COMPLETA DOS CANAIS DE AQUISIÇÃO")
    print("=" * 60)
    
    # Lista completa dos canais conforme fornecida
    canais_lista = [
        (1, "REDE SOCIAL"),
        (2, "SITE"),
        (3, "QUEM INDICA AMIGO É"),
        (4, "JÁ É CLIENTE"),
        (5, "PANFLETOS"),
        (6, "EMPRESA ATENTO"),
        (7, "DR ÁLVARO"),
        (8, "TERMINAL SANTANA"),
        (9, "CLINICA MED"),
        (10, "MAGAZINE LUIZA"),
        (100, "TESTE"),
        (101, "DV JACIANE DINIZ"),
        (102, "DV ANDERSON KENION"),
        (103, "DV WESLLEY ABREU"),
        (104, "DV EMERSON DE JESUS"),
        (105, "SUPERMERCADO SÃO JOSE"),
        (106, "FEIRA VILA AMORIM"),
        (107, "LUIS FIO FOLHETOS"),
        (108, "DV BRYAN NASCIMENTO"),
        (109, "PREVINA JORDANESIA"),
        (11, "PASSAGEM"),
        (110, "PREFEITO NO SEU BAIRRO"),
        (111, "BOLIVIANOS"),
        (112, "ELIS"),
        (113, "MARTINS LOCOCO"),
        (114, "HOSPITAL STELLA MARIS"),
        (115, "FLORIPARK"),
        (116, "RD ESP"),
        (117, "MINDBE"),
        (118, "GUIMA"),
        (119, "DR GUILHERME H J"),
        (12, "CARRO DE SOM"),
        (120, "CONVENIO INTERMÉDICA"),
        (121, "DR MARIA EUGENIA BUSCA"),
        (122, "DR MARCELO KENDI FUJII"),
        (123, "DR KIU SUB SHIN"),
        (124, "DR MARCUS TAKATSU"),
        (125, "DV THALITA ASSIS"),
        (126, "DV DENILSON"),
        (127, "DV ANDERSON"),
        (128, "DV ROBSON OLIVEIRA"),
        (129, "DV RAFAELA GOMES"),
        (13, "VITRINE"),
        (130, "DV JEAN LEANDRO"),
        (131, "DV NIKE"),
        (132, "DV NATALIA"),
        (133, "DV LETICIA"),
        (134, "INTERGALAXY SA"),
        (135, "DR BEATRIZ NAKAGOME"),
        (136, "DR GILVAN VILARINHO"),
        (137, "DR MARCOS VINICIUS PRADO"),
        (138, "SAÚDE DOS OLHOS"),
        (139, "DR JOÃO VICTOR RAMOS DE TOLEDO"),
        (14, "PLACA DE LOJA"),
        (140, "DR ALEXANDRE TOMIO UMINO"),
        (141, "DR ALLAN GOMES DA SILVA"),
        (142, "DR AMANDA A VV DE CASTRO"),
        (143, "DR GABRIEL CASTILHO SANDOVAL"),
        (144, "DR MAURICIO FLANK"),
        (145, "INTS"),
        (146, "DR MARCIA FERRARI PEREZ"),
        (147, "INSTITUTO SUEL ABUJAMRA"),
        (149, "RADIO ÔMEGA"),
        (15, "ORÇAMENTO"),
        (150, "DR CRISTINA FREIRE"),
        (151, "ARKIMEDES CENTRO MÉDICO"),
        (152, "GOOGLE/FACE/INSTA - PATROCÍNIO"),
        (153, "DR CAROLINA REZENDE"),
        (154, "DR GUILHERME  M.KAPPEL"),
        (155, "DR WALTHER CAMPOS NETO"),
        (156, "DR ANESIO RUIZ"),
        (157, "DR LIVIA FERRAZ"),
        (158, "TRANSPPASS"),
        (159, "CLINICA DIMEG"),
        (16, "INDICAÇÃO"),
        (160, "CONVENIO PARTMED"),
        (161, "OUTRA LOJA"),
        (162, "DR GUILHERME S. MOTTA"),
        (163, "IGREJA PLENITUDE"),
        (164, "CAMPANHA COMPRE 1 LEVE 3"),
        (165, "CAMPANHA NINJAS"),
        (166, "DV BRUNA RAFAELLA DA SILVA"),
        (167, "DV GRAZIELA SANTOS FERREIRA"),
        (168, "DV TAIS CARDOSO"),
        (169, "DV DOUGLAS JESUS DA SILVA"),
        (17, "ABORDAGEM"),
        (170, "PENITENCIARIA FEM SÃO PAULO"),
        (171, "KOMBOS"),
        (172, "CAMPANHA LYOR"),
        (18, "RADIO TROPICAL"),
        (19, "CARRETA"),
        (20, "RADIO ESPERANCA"),
        (21, "TELEMARKETING"),
        (22, "OUTDOOR"),
        (23, "CAMPANHA VADO"),
        (24, "CLINICA"),
        (25, "DR EDSON"),
        (26, "DROGARIA SÃO PAULO"),
        (27, "DROGARIA SUPERMED"),
        (28, "DROGARIA DROGALIS"),
        (29, "SIND SINETROSV"),
        (30, "MEDILINE ASSISTENCIA"),
        (31, "SIND CORREIOS"),
        (32, "IAMSPE"),
        (33, "OPEN LINE"),
        (34, "ABMED"),
        (35, "CLUB GOLD STAR"),
        (36, "VALE SAUDE JEQUITI"),
        (37, "SIND SINDSERVITA"),
        (38, "DIVULGADOR"),
        (39, "DV BARBARA MATOS"),
        (40, "SIND SINTRAMMSP"),
        (41, "SEGUROS UNIMED"),
        (42, "AMEPLAN"),
        (43, "CRUZ AZUL"),
        (44, "CONVENIO FL"),
        (45, "RADIO ADORE FM"),
        (46, "CONVENIO JASON"),
        (47, "DV NAYARA COSTA"),
        (48, "RX DE FORA"),
        (49, "ALEFARMA"),
        (50, "PROGRAMA SHOW"),
        (51, "NOVA X"),
        (52, "DROGARIA CAMPEA"),
        (53, "SANTA TEREZINHA ASSOCIAÇÃO"),
        (54, "PREFEITURA"),
        (55, "CARTAO DE TODOS"),
        (56, "PLENA SAÚDE"),
        (57, "SUBPREFEITURA"),
        (58, "CARTÃO INDICAÇÃO"),
        (59, "SITAP - LINEX"),
        (60, "ASSEMBLEIA DE DEUS"),
        (61, "INDICAÇÃO CONVÊNIO PREFEITURA"),
        (62, "CONVENIO MWI"),
        (63, "1ª COMPRA"),
        (64, "CONVENIO FAN"),
        (65, "VISIOTESTE"),
        (66, "CLINICA ALPHA VISION"),
        (67, "DV JOÃO PAULO"),
        (68, "RADIO NOVA X 103.1"),
        (69, "RADIO REDE UNÇÃO 96.5"),
        (70, "DV SUELEN RODRIGUES"),
        (71, "DV GABRIELA SILVA"),
        (72, "ULTRASOM"),
        (73, "RADIO ATALAIA"),
        (74, "DV MIKELY FORTALEZA"),
        (75, "DR RAFAEL BORGES"),
        (76, "DR RENATO MACCIONE"),
        (77, "AMIGOS"),
        (78, "DR RAFAEL PIVATTO"),
        (79, "SUS"),
        (80, "CESTA BÁSICA"),
        (81, "ADEASP"),
        (82, "RADIO IMPRENSA FM"),
        (83, "RADIO TERRA"),
        (84, "PROJETO CUIDAR"),
        (85, "CONVENIO INTERMÉDICA"),
        (86, "BIO SAÚDE"),
        (87, "CARTÃO COMPLETO"),
        (88, "DV VICTOR HUGO"),
        (89, "RADIO FÉ 101.5"),
        (90, "DV LARISSA SILVA"),
        (91, "DV LARISSA COSTA"),
        (92, "DV MARIANA COSTA"),
        (93, "DV MAICON OLIVEIRA"),
        (94, "DV ERICK ANJOS"),
        (95, "DV ALINE CRUZ"),
        (96, "DROGARIA DROGASIL"),
        (97, "LOJA FECHADA"),
        (98, "WHATSAPP"),
        (99, "OUTROS")
    ]
    
    # Categorização automática baseada em palavras-chave
    def categorizar_canal(nome):
        nome_upper = nome.upper()
        
        # Médicos e Profissionais de Saúde
        if any(x in nome_upper for x in ['DR ', 'DRA ', 'MÉDICO', 'CLINICA', 'HOSPITAL', 'SAÚDE', 'CENTRO MÉDICO']):
            return 'MEDICO'
        
        # Divulgadores
        if any(x in nome_upper for x in ['DV ', 'DIVULGADOR']):
            return 'DIVULGADOR'
        
        # Digital/Online
        if any(x in nome_upper for x in ['REDE SOCIAL', 'SITE', 'GOOGLE', 'FACE', 'INSTA', 'WHATSAPP', 'DIGITAL']):
            return 'DIGITAL'
        
        # Rádio
        if any(x in nome_upper for x in ['RADIO', 'FM']):
            return 'RADIO'
        
        # Convênios
        if any(x in nome_upper for x in ['CONVENIO', 'UNIMED', 'PLANO', 'SEGUROS']):
            return 'CONVENIO'
        
        # Farmácias/Drogarias
        if any(x in nome_upper for x in ['DROGARIA', 'FARMACIA', 'ALEFARMA']):
            return 'FARMACIA'
        
        # Indicação/Referência
        if any(x in nome_upper for x in ['INDICAÇÃO', 'AMIGO', 'CLIENTE', 'OUTRA LOJA']):
            return 'INDICACAO'
        
        # Marketing/Campanhas
        if any(x in nome_upper for x in ['CAMPANHA', 'OUTDOOR', 'PANFLETO', 'CARTÃO', 'CARRO DE SOM', 'PLACA']):
            return 'MARKETING'
        
        # Governo/Institucional
        if any(x in nome_upper for x in ['PREFEITURA', 'SUBPREFEITURA', 'SUS', 'SIND ', 'SINDICATO']):
            return 'INSTITUCIONAL'
        
        # Parcerias/Empresas
        if any(x in nome_upper for x in ['EMPRESA', 'MAGAZINE', 'SUPERMERCADO', 'FEIRA']):
            return 'PARCERIA'
        
        # Abordagem Direta
        if any(x in nome_upper for x in ['ABORDAGEM', 'TELEMARKETING', 'PASSAGEM']):
            return 'ABORDAGEM'
        
        # Religioso
        if any(x in nome_upper for x in ['IGREJA', 'ASSEMBLEIA']):
            return 'RELIGIOSO'
        
        return 'OUTROS'
    
    # Processar todos os canais
    canais_processados = []
    categorias = defaultdict(list)
    
    for codigo, nome in canais_lista:
        categoria = categorizar_canal(nome)
        canal_uuid = str(uuid.uuid4())
        
        canal_data = {
            'codigo': codigo,
            'nome': nome,
            'categoria': categoria,
            'uuid': canal_uuid
        }
        
        canais_processados.append(canal_data)
        categorias[categoria].append(canal_data)
    
    print(f"📊 ESTATÍSTICAS GERAIS:")
    print(f"   • Total de canais: {len(canais_processados)}")
    print(f"   • Categorias identificadas: {len(categorias)}")
    
    print(f"\n📋 DISTRIBUIÇÃO POR CATEGORIA:")
    for categoria, canais in sorted(categorias.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"   • {categoria}: {len(canais)} canais")
        
        # Mostrar alguns exemplos
        exemplos = [c['nome'] for c in canais[:3]]
        if len(canais) > 3:
            exemplos.append(f"... +{len(canais)-3}")
        print(f"     {', '.join(exemplos)}")
    
    # Salvar mapeamento completo
    mapeamento_completo = {
        'data_geracao': '2025-10-29',
        'total_canais': len(canais_processados),
        'canais': canais_processados,
        'categorias': {cat: len(canais) for cat, canais in categorias.items()}
    }
    
    with open('mapeamento_canais_aquisicao_completo.json', 'w', encoding='utf-8') as f:
        json.dump(mapeamento_completo, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 MAPEAMENTO SALVO:")
    print(f"   • Arquivo: mapeamento_canais_aquisicao_completo.json")
    print(f"   • {len(canais_processados)} canais com UUIDs gerados")
    
    # Análise das categorias
    print(f"\n📈 ANÁLISE DETALHADA POR CATEGORIA:")
    
    for categoria, canais in sorted(categorias.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n🏷️  {categoria} ({len(canais)} canais):")
        for canal in sorted(canais, key=lambda x: x['codigo']):
            print(f"   {canal['codigo']:3d}. {canal['nome']}")
    
    print(f"\n✅ ANÁLISE COMPLETA FINALIZADA!")
    return mapeamento_completo

if __name__ == "__main__":
    analisar_canais_completos()