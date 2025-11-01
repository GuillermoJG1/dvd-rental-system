#!/bin/bash

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# URL base de la API
BASE_URL="${API_URL:-http://localhost:8000}"

echo -e "${YELLOW}=== DVD Rental System API Tests ===${NC}\n"

# Contador de tests
PASSED=0
FAILED=0

# Función para tests
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5
    
    echo -e "${YELLOW}Testing: $name${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL$endpoint")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Status: $http_code"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} - Expected: $expected_status, Got: $http_code"
        echo "Response: $body"
        ((FAILED++))
    fi
    echo ""
}

# Esperar a que la API esté lista
echo "Esperando a que la API esté disponible..."
max_attempts=30
attempt=0
until curl -s "$BASE_URL/" > /dev/null 2>&1 || [ $attempt -eq $max_attempts ]; do
    attempt=$((attempt + 1))
    echo "Intento $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}API no disponible después de $max_attempts intentos${NC}"
    exit 1
fi

echo -e "${GREEN}API disponible!${NC}\n"

# === TESTS ===

# 1. Health Check
test_endpoint "Health Check" "GET" "/" "" "200"

# 2. Obtener clientes
test_endpoint "Get Customers" "GET" "/customers" "" "200"

# 3. Obtener DVDs
test_endpoint "Get DVDs" "GET" "/dvds" "" "200"

# 4. Obtener Staff
test_endpoint "Get Staff" "GET" "/staff" "" "200"

# 5. Crear una renta
test_endpoint "Create Rental" "POST" "/rentals" \
    '{"customer_id":1,"dvd_id":1,"staff_id":1,"days":7}' "200"

# 6. Obtener todas las rentas
test_endpoint "Get Rentals" "GET" "/rentals" "" "200"

# 7. Reporte: Rentas de cliente
test_endpoint "Customer Rentals Report" "GET" "/reports/customer/1" "" "200"

# 8. Reporte: DVDs no devueltos
test_endpoint "Unreturned DVDs Report" "GET" "/reports/unreturned" "" "200"

# 9. Reporte: DVDs más rentados
test_endpoint "Most Rented DVDs Report" "GET" "/reports/most-rented" "" "200"

# 10. Reporte: Ganancias por staff
test_endpoint "Staff Earnings Report" "GET" "/reports/staff-earnings" "" "200"

# 11. Devolver DVD (usando ID 1)
test_endpoint "Return DVD" "PUT" "/rentals/1/return" "" "200"

# 12. Crear otra renta para cancelar
test_endpoint "Create Rental for Cancel" "POST" "/rentals" \
    '{"customer_id":2,"dvd_id":2,"staff_id":2,"days":5}' "200"

# 13. Cancelar renta (usando ID 2)
test_endpoint "Cancel Rental" "DELETE" "/rentals/2" "" "200"

# 14. Crear cliente nuevo
test_endpoint "Create Customer" "POST" "/customers" \
    '{"name":"Test User","email":"test@example.com","phone":"1234567890"}' "200"

# 15. Crear DVD nuevo
test_endpoint "Create DVD" "POST" "/dvds" \
    '{"title":"Test Movie","genre":"Action","release_year":2024,"rental_price":5.0,"available_copies":3}' "200"

# 16. Crear Staff nuevo
test_endpoint "Create Staff" "POST" "/staff" \
    '{"name":"Test Staff","position":"Tester"}' "200"

# === RESUMEN ===
echo -e "${YELLOW}=== Test Summary ===${NC}"
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed ✗${NC}"
    exit 1
fi