#!/bin/bash

# Configuración base
BASE_URL="${API_URL:-http://localhost:8000}"
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "=== Iniciando Tests de Integración con CURL en $BASE_URL ==="

# Contadores
PASSED=0
FAILED=0

# Función para probar endpoints
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5
    
    # Ejecuta curl y extrae solo el código de estado HTTP
    if [ "$method" = "GET" ]; then
        status=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL$endpoint")
    elif [ "$method" = "POST" ]; then
        status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" -d "$data")
    elif [ "$method" = "PUT" ]; then
        status=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" -d "$data")
    elif [ "$method" = "DELETE" ]; then
        status=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE_URL$endpoint")
    fi

    # Validación
    if [ "$status" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC}: $name (Status: $status)"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}: $name (Esperado: $expected_status, Recibido: $status)"
        ((FAILED++))
    fi
}

# --- EJECUCIÓN DE PRUEBAS ---
# Esperar a que el servicio esté listo (Health check simple)
echo "Esperando disponibilidad de la API..."
until curl -s -f "$BASE_URL/" > /dev/null; do
    sleep 2
    echo "Reintentando conexión..."
done

# Pruebas definidas
test_endpoint "Health Check" "GET" "/" "" 200
test_endpoint "Listar Clientes" "GET" "/customers" "" 200
test_endpoint "Listar Películas" "GET" "/films" "" 200
test_endpoint "Crear Renta" "POST" "/rentals" '{"customer_id":1,"film_id":1,"staff_id":1,"days":3}' 200
test_endpoint "Reporte DVDs No Devueltos" "GET" "/reports/unreturned" "" 200

# --- RESUMEN ---
echo "------------------------------------------------"
echo "Tests Pasados: $PASSED"
echo "Tests Fallados: $FAILED"

if [ $FAILED -gt 0 ]; then
    exit 1
else
    exit 0
fi