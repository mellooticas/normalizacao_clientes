# 📁 ESTRUTURA DE DADOS ORIGINAIS - Carnê Fácil

## 🎯 ORGANIZAÇÃO DOS DADOS REAIS

Esta pasta contém os dados originais das óticas organizados por tipo de sistema/fonte:

```
data/originais/
├── 📂 vixen/          # Dados do sistema Vixen
│   ├── clientes/      # Planilhas de clientes Vixen
│   ├── vendas/        # Relatórios de vendas Vixen
│   └── produtos/      # Catálogos de produtos
│
├── 📂 oss/            # Dados de Ordens de Serviço
│   ├── por_loja/      # OS separadas por loja
│   │   ├── suzano/
│   │   ├── maua/
│   │   ├── perus/
│   │   ├── rio_pequeno/
│   │   ├── sao_mateus/
│   │   └── suzano2/
│   └── consolidadas/  # OS já consolidadas
│
├── 📂 cxs/            # Dados de Caixa/Financeiro
│   ├── diario/        # Relatórios diários
│   ├── mensal/        # Fechamentos mensais
│   └── anual/         # Balanços anuais
│
└── 📂 controles_geral/ # Planilhas de controle geral
    ├── inventario/    # Controle de estoque
    ├── funcionarios/  # Dados de funcionários
    └── campanhas/     # Campanhas de marketing
```

## 📋 TIPOS DE ARQUIVO ESPERADOS

### 📊 VIXEN
- Exportações de clientes (.xlsx, .csv)
- Relatórios de vendas (.xlsx)
- Listagens de produtos

### 🧾 OSS (Ordens de Serviço)
- Planilhas por loja (.xlsx)
- Dados de atendimentos
- Histórico de consultas

### 💰 CXS (Caixa)
- Relatórios financeiros (.xlsx)
- Movimento diário
- Formas de pagamento

### 📈 CONTROLES GERAL
- Planilhas de controle (.xlsx)
- Relatórios gerenciais
- Dados administrativos

## 🚀 APÓS CARREGAR OS DADOS

1. **Coloque os arquivos** nas pastas apropriadas
2. **Execute o analisador**: `python analisar_dados_originais.py`
3. **Revise os dados** encontrados
4. **Execute importação**: `python import_dados_completos.py`

## 📝 EXEMPLO DE ORGANIZAÇÃO

```
data/originais/vixen/clientes/
├── suzano_clientes_2023.xlsx
├── suzano_clientes_2024.xlsx
└── todos_clientes_vixen.csv

data/originais/oss/por_loja/suzano/
├── os_suzano_jan_2023.xlsx
├── os_suzano_fev_2023.xlsx
└── ...

data/originais/cxs/mensal/
├── fechamento_janeiro_2023.xlsx
├── fechamento_fevereiro_2023.xlsx
└── ...
```

## ⚠️ IMPORTANTE

- **Não altere** os nomes originais dos arquivos
- **Mantenha backup** dos dados originais
- **Organize por data** quando possível
- **Documente** arquivos com nomes diferentes

---

**🎯 STATUS**: Aguardando dados originais para análise e importação completa.