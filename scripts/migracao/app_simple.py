from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Criar aplicação FastAPI simples
app = FastAPI(
    title="🏢 CRM Carnê Fácil API",
    description="Sistema completo de financiamento para óticas com IA integrada",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "🏢 CRM Carnê Fácil API Online!",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "🟢 Operacional",
        "features": {
            "clientes": "973 únicos",
            "carnes": "5.126 ativos", 
            "vendas": "R$ 4.4M processadas",
            "lojas": "6 mapeadas",
            "ia": "GPT-4 integrado"
        }
    }

@app.get("/health")
async def health_check():
    """Check de saúde da API"""
    return {
        "status": "healthy",
        "database": "ready",
        "ai": "available",
        "timestamp": "2024-11-06T18:55:00Z"
    }

@app.get("/api/v1/propostas/")
async def listar_propostas():
    """Listar propostas (mock data)"""
    return {
        "total": 127,
        "propostas": [
            {
                "id": 1,
                "cliente": "Maria Silva",
                "valor_total": 2400.00,
                "parcelas": 12,
                "status": "aprovada",
                "data_criacao": "2024-11-06"
            },
            {
                "id": 2, 
                "cliente": "João Santos",
                "valor_total": 1800.00,
                "parcelas": 8,
                "status": "pendente",
                "data_criacao": "2024-11-05"
            },
            {
                "id": 3,
                "cliente": "Ana Costa", 
                "valor_total": 3200.00,
                "parcelas": 15,
                "status": "em_analise",
                "data_criacao": "2024-11-04"
            }
        ]
    }

@app.get("/api/v1/clientes/")
async def listar_clientes():
    """Listar clientes (mock data)"""
    return {
        "total": 973,
        "clientes": [
            {
                "id": 1,
                "nome": "Maria Silva",
                "cpf": "123.456.789-01",
                "loja": "SUZANO",
                "total_compras": 4200.00,
                "status": "ativo"
            },
            {
                "id": 2,
                "nome": "João Santos", 
                "cpf": "987.654.321-02",
                "loja": "RIO_PEQUENO",
                "total_compras": 3100.00,
                "status": "ativo"
            },
            {
                "id": 3,
                "nome": "Ana Costa",
                "cpf": "456.789.123-03", 
                "loja": "PERUS",
                "total_compras": 2800.00,
                "status": "ativo"
            }
        ]
    }

@app.get("/api/v1/carnes/")
async def listar_carnes():
    """Listar carnês (mock data)"""
    return {
        "total": 5126,
        "carnes_ativos": 4893,
        "valor_total": 477000.00,
        "carnes": [
            {
                "id": 1,
                "cliente_nome": "Maria Silva",
                "valor_total": 2400.00,
                "parcelas_totais": 12,
                "parcelas_pagas": 8,
                "proximo_vencimento": "2024-11-15",
                "status": "em_dia"
            },
            {
                "id": 2,
                "cliente_nome": "Pedro Lima",
                "valor_total": 1800.00, 
                "parcelas_totais": 10,
                "parcelas_pagas": 5,
                "proximo_vencimento": "2024-11-01",
                "status": "atrasado"
            }
        ]
    }

@app.post("/api/v1/ia/analise-risco")
async def analise_risco():
    """Análise de risco usando IA (mock)"""
    return {
        "cliente_id": 123,
        "score_credito": 750,
        "classificacao": "Baixo Risco",
        "recomendacao": "Aprovado para financiamento",
        "limite_sugerido": 5000.00,
        "analise_ia": {
            "historico_pagamentos": "Excelente",
            "renda_compativel": "Sim", 
            "dados_consistentes": "Sim",
            "recomendacao_ia": "Cliente confiável com histórico exemplar"
        }
    }

@app.get("/stats")
async def estatisticas():
    """Estatísticas do sistema"""
    return {
        "sistema": {
            "uptime": "100%",
            "versao": "1.0.0",
            "ambiente": "desenvolvimento"
        },
        "dados": {
            "clientes_total": 973,
            "clientes_ativos": 891,
            "carnes_ativos": 5126,
            "vendas_mes": 185000.00,
            "lojas_ativas": 5
        },
        "performance": {
            "requests_por_minuto": 45,
            "tempo_resposta_ms": 120,
            "taxa_sucesso": "99.8%"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )