# 📁 ESTRUTURA REORGANIZADA - CRM CARNÊ FÁCIL

## 🎯 **REORGANIZAÇÃO COMPLETA**

✅ **Frontend (app/) separado do ETL (etl/)**  
✅ **Scripts organizados por função**  
✅ **Zero conflitos entre módulos**  

---

## 📂 **NOVA ESTRUTURA**

```
📦 carne_facil/
├── 🎨 app/                      # FRONTEND/API LIMPO
│   ├── main.py                  # Servidor principal
│   ├── controllers/             # Controladores web
│   ├── services/               # Lógica de negócio  
│   ├── templates/              # Interface HTML
│   └── models/                 # Estruturas de dados
│
├── 🔧 etl/                      # ETL SEPARADO
│   ├── sql/                    # Todos os .sql
│   ├── scripts/                # Scripts Python
│   ├── normalizacao/           # Mapeamentos
│   └── outputs/                # Resultados
│
└── 📊 data/                     # DADOS ORGANIZADOS
    ├── raw/                    # Originais
    └── processed/              # Processados
```

---

## 🚀 **EXECUÇÃO**

### **Frontend**
```bash
python app/main.py
# http://localhost:8000
```

### **ETL** 
```bash
cd etl/scripts/
python movimento_caixa/11_migrar_apenas_carnes.py
```

---

## ✅ **STATUS**

- **Frontend:** ✅ Funcional e limpo
- **ETL:** ✅ Organizado e separado  
- **Dados:** ✅ 5.126 registros prontos
- **Config:** 🔧 Supabase pendente

**Próximo:** Configurar Supabase e testar end-to-end! 🚀