# 🔍 Elasticsearch Test Report - DD Environment

**Tester**: Diego Jácome  
**Fecha**: 2025-05-19  
**Entorno**: QA  
**Objetivo**: Validar índices, mappings y resultados de queries en el clúster de Elasticsearch usado por Dynamic Docs.

---

## 1. 🔧 Configuración inicial

| Parámetro | Valor |
|----------|-------|
| Endpoint base | `https://dd-integrated-search-test.kb.southcentralus.azure.elastic-cloud.com/app/dev_tools#/console` |
| Tenant | `25` |
| Índice evaluado | `25_documents` |
| Herramienta utilizada | Elasticsearch console |
| Autenticación | User and password |

---

## 2. ✅ Casos de prueba ejecutados

### TC01 - Validar existencia del índice

- **Query**:
  ```http
  GET /_cat/indices?v
