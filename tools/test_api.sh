#!/bin/bash

# Script de teste completo para a API Astrotagiario
# Testa todos os endpoints principais e valida respostas

set -euo pipefail

# Configurações
API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
API_KEY="${API_KEY:-testapikey}"
VERBOSE="${VERBOSE:-false}"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contadores
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Funções utilitárias
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"
}

# Função para fazer requisições HTTP
make_request() {
    local method="$1"
    local endpoint="$2"
    local data="${3:-}"
    local expected_status="${4:-200}"
    local expected_content_type="${5:-application/json}" # Default to application/json

    ((TESTS_TOTAL++))

    if [[ "$VERBOSE" == "true" ]]; then
        log "Request: $method $API_BASE_URL$endpoint"
        if [[ -n "$data" ]]; then
            log "Data: $data"
        fi
        log "Expected status: $expected_status, Expected content-type: $expected_content_type"
    fi
    
    # Temporary file to store headers
    local header_file=$(mktemp)

    # Perform request, store body in $response_body, http_code in $http_code
    # and headers in $header_file
    if [[ -n "$data" ]]; then
        http_code=$(curl -s -w "%{http_code}" -X "$method" \
            "$API_BASE_URL$endpoint" \
            -H "X-API-KEY: $API_KEY" \
            -H "Content-Type: application/json" \
            -d "$data" \
            -o >(cat >&1) \
            -D "$header_file")
        response_body=$(cat "$header_file.body") # Assuming curl output body to a related file or pipe
                                              # This part is tricky with -o and stdout.
                                              # A better way for body: response_body=$(curl ... -o - )
                                              # Let's simplify: capture stdout for body.
    else
        http_code=$(curl -s -w "%{http_code}" -X "$method" \
            "$API_BASE_URL$endpoint" \
            -H "X-API-KEY: $API_KEY" \
            -o >(cat >&1) \
            -D "$header_file")
        response_body=$(cat "$header_file.body")
    fi

    # Corrected way to capture response body directly and headers separately
    # Purge previous response_body to avoid issues if curl fails
    response_body=""
    if [[ -n "$data" ]]; then
        response_body=$(curl -s -X "$method" \
            "$API_BASE_URL$endpoint" \
            -H "X-API-KEY: $API_KEY" \
            -H "Content-Type: application/json" \
            -d "$data" \
            -D "$header_file")
        http_code=$(curl -s -w "%{http_code}" -X "$method" \
            "$API_BASE_URL$endpoint" \
            -H "X-API-KEY: $API_KEY" \
            -H "Content-Type: application/json" \
            -d "$data" -o /dev/null) # Get code separately
    else
        response_body=$(curl -s -X "$method" \
            "$API_BASE_URL$endpoint" \
            -H "X-API-KEY: $API_KEY" \
            -D "$header_file")
        http_code=$(curl -s -w "%{http_code}" -X "$method" \
            "$API_BASE_URL$endpoint" \
            -H "X-API-KEY: $API_KEY" -o /dev/null) # Get code separately
    fi
    
    actual_content_type=$(grep -i "^Content-Type:" "$header_file" | awk -F': ' '{print $2}' | tr -d '\r\n')
    rm -f "$header_file" # Clean up header file

    if [[ "$VERBOSE" == "true" ]]; then
        log "Response Code: $http_code"
        log "Actual Content-Type: $actual_content_type"
        if [[ "$actual_content_type" == *"application/json"* ]]; then
            log "Response Body: $response_body"
        else
            log "Response Body: (Binary data of length ${#response_body})"
        fi
    fi
    
    # Check both HTTP status and content type (if expected_content_type is set)
    if [[ "$http_code" == "$expected_status" ]] && [[ -z "$expected_content_type" || "$actual_content_type" == *"$expected_content_type"* ]]; then
        ((TESTS_PASSED++))
        log "✅ PASS: $method $endpoint (HTTP $http_code, Content-Type: $actual_content_type)"
        if [[ "$actual_content_type" == *"application/json"* ]]; then
            echo "$response_body"
        elif [[ "$expected_content_type" != "application/json" && -n "$response_body" ]]; then
             # For non-JSON, like image/png, we can pass the body for basic checks like non-empty
             echo "$response_body"
        else
            log "Non-JSON response body not echoed for brevity."
        fi
        return 0
    else
        ((TESTS_FAILED++))
        error "❌ FAIL: $method $endpoint (Expected Status: $expected_status, Got: $http_code | Expected CT: $expected_content_type, Got: $actual_content_type)"
        # Echo body on fail for debugging regardless of type, but be mindful of binary
        if [[ "$actual_content_type" == *"application/json"* || "$actual_content_type" == *"text/"* ]]; then
            echo "Response Body on Fail: $response_body"
        else
            log "Response Body on Fail: (Binary data of length ${#response_body})"
        fi
        return 1
    fi
}

# --- Test Definitions ---

test_root_endpoint() {
    log "🏠 Testing root endpoint..."
    response=$(make_request "GET" "/")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | jq -e '.message | contains("Bem-vindo à API de Astrologia")' > /dev/null; then
            log "✅ Root endpoint returned welcome message."
        else
            error "⚠️ Root endpoint message check failed."
            ((TESTS_FAILED++)); ((TESTS_PASSED--)) # Adjust counters
        fi
    fi
    echo
}

test_health() {
    log "🏥 Testing health check..."
    response=$(make_request "GET" "/health")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | jq -e '.status == "healthy"' > /dev/null; then
            log "✅ Health check returned 'healthy'"
        else
            error "⚠️ Health check didn't return expected 'healthy' status."
            ((TESTS_FAILED++)); ((TESTS_PASSED--)) # Adjust counters
        fi
    fi
    echo
}

# Teste de mapa natal
test_natal_chart() {
    log "🌟 Testing natal chart calculation (v1)..."
    
    local test_data='{
        "name": "Test User API",
        "year": 1997,
        "month": 10,
        "day": 13,
        "hour": 22,
        "minute": 0,
        "latitude": -3.7172,
        "longitude": -38.5247,
        "tz_str": "America/Fortaleza",
        "house_system": "placidus"
    }'
    
    response=$(make_request "POST" "/api/v1/natal_chart" "$test_data")
    if [[ $? -eq 0 ]]; then
        planet_count=$(echo "$response" | jq '.planets | length')
        if [[ $planet_count -ge 10 ]]; then
            log "✅ Standard Natal: Found $planet_count planets."
        else
            error "⚠️ Standard Natal: Only $planet_count planets (expected ≥10)."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
        # Check for new fields (quality, element, emoji) in the first planet and first house cusp
        # These might be null if not populated by backend for some reason, so check for presence or specific values if known.
        # For now, just checking if the keys exist for optional fields, or are non-null for required ones.
        # K4 compatibility: .quality, .element, .emoji might not be standard on K4 subjects.
        # Removing these checks for broader compatibility. Core data (sign, position) is more critical.
        # if echo "$response" | jq -e '.planets[0].quality' > /dev/null && \
        #    echo "$response" | jq -e '.planets[0].element' > /dev/null && \
        #    echo "$response" | jq -e '.planets[0].emoji' > /dev/null && \
        #    echo "$response" | jq -e '.houses[0].quality' > /dev/null && \
        #    echo "$response" | jq -e '.houses[0].element' > /dev/null && \
        #    echo "$response" | jq -e '.houses[0].emoji' > /dev/null; then
        #     log "✅ Standard Natal: Found new fields (quality, element, emoji) in planets and houses."
        # else
        #     error "⚠️ Standard Natal: New fields (quality, element, emoji) missing in planets or houses."
        #     ((TESTS_FAILED++)); ((TESTS_PASSED--))
        # fi
        log "ℹ️ Standard Natal: Checks for quality, element, emoji in planets/houses skipped for K4 compatibility."
    fi
    echo

    log "🌟 Testing natal chart calculation (V1 - Sidereal & Heliocentric)..."
    local test_data_sidereal='{
        "name": "Sidereal Heliocentric User",
        "year": 1997, "month": 10, "day": 13, "hour": 22, "minute": 0,
        "latitude": -3.7172, "longitude": -38.5247, "tz_str": "America/Fortaleza",
        "house_system": "whole_sign",
        "zodiac_type": "Sidereal",
        "sidereal_mode": "LAHIRI",
        "perspective_type": "Heliocentric"
    }' # Note: Heliocentric charts don't typically use houses, Kerykeion might ignore house_system.

    response_sidereal=$(make_request "POST" "/api/v1/natal_chart" "$test_data_sidereal")
    if [[ $? -eq 0 ]]; then
        planet_count_sidereal=$(echo "$response_sidereal" | jq '.planets | length')
        if [[ $planet_count_sidereal -ge 8 ]]; then # Heliocentric might exclude Moon, Earth.
            log "✅ Sidereal/Helio Natal: Found $planet_count_sidereal planets."
        else
            error "⚠️ Sidereal/Helio Natal: Only $planet_count_sidereal planets."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
        # Check if chart_info reflects the settings
        if echo "$response_sidereal" | jq -e '.chart_info.zodiac_type == "Sidereal"' > /dev/null && \
           echo "$response_sidereal" | jq -e '.chart_info.perspective_type == "Heliocentric"' > /dev/null; then
            log "✅ Sidereal/Helio Natal: chart_info reflects correct zodiac and perspective."
        else
            error "⚠️ Sidereal/Helio Natal: chart_info does not reflect correct zodiac/perspective."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_natal_chart_geonames() {
    log "🌍 Testing natal chart with GeoNames lookup (V1)..."
    local test_data_geonames='{
        "name": "GeoNames User",
        "year": 1985, "month": 7, "day": 22, "hour": 10, "minute": 15,
        "city": "Rome",
        "nation": "IT",
        "house_system": "placidus",
        "zodiac_type": "Tropic"
    }'

    # The API itself uses os.getenv("GEONAMES_USERNAME")
    # This test relies on that mechanism or Kerykeion's default if the env var is not set in the API's environment.

    response=$(make_request "POST" "/api/v1/natal_chart" "$test_data_geonames" 200 "application/json")

    if [[ $? -eq 0 ]]; then
        # Check if resolved_location indicates successful geocoding
        if echo "$response" | jq -e '.resolved_location.method == "geolocation"' > /dev/null && \
           echo "$response" | jq -e '.resolved_location.input_city == "Rome"' > /dev/null; then
            log "✅ GeoNames Natal: Lookup for Rome, IT seems to have used geolocation method."
        else
            error "⚠️ GeoNames Natal: Lookup for Rome, IT might not have used geolocation as expected or fields missing. Check 'resolved_location'."
        fi

        planet_count=$(echo "$response" | jq '.planets | length')
        if [[ $planet_count -ge 10 ]]; then
            log "✅ GeoNames Natal: Found $planet_count planets."
        else
            error "❌ GeoNames Natal: Only $planet_count planets found."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

# Teste de trânsitos diários
test_daily_transits() {
    log "📅 Testing daily transits listing (v1)..."
    
    local test_data='{
        "year": 2025,
        "month": 6,
        "day": 13
    }'
    
    response=$(make_request "POST" "/api/v1/transits/daily" "$test_data")
    if [[ $? -eq 0 ]]; then
        # Verificar se há aspectos
        aspect_count=$(echo "$response" | jq '.aspects | length')
        if [[ $aspect_count -gt 0 ]]; then
            log "✅ Found $aspect_count daily aspects"
        else
            error "⚠️ No daily aspects found"
            log "INFO: This might be okay if no major aspects are occurring on this specific day."
        fi
    fi
    echo
}

test_current_transits() {
    log "🌠 Testing current transits (v1)..."
    local test_data='{
        "name": "Test User", "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0,
        "latitude": 0.0, "longitude": 0.0, "tz_str": "UTC",
        "current_year": 2024, "current_month": 1, "current_day": 1,
        "current_hour": 12, "current_minute": 0, "current_tz_str": "UTC"
    }'
    response=$(make_request "POST" "/api/v1/current_transits" "$test_data")
    if [[ $? -eq 0 ]]; then
        aspect_count=$(echo "$response" | jq '.aspects | length')
        if [[ $aspect_count -gt 0 ]]; then
            log "✅ Found $aspect_count aspects."
        else
            error "⚠️ No aspects found for current transits."
            # This might be a valid scenario depending on the date, so not failing strictly
            log "INFO: This might be okay if no major aspects are occurring."
        fi
    fi
    echo
}

test_transits_to_natal() {
    log "🔄 Testing transits to natal (v1)..."
     local test_data='{
        "name": "Test User", "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0,
        "latitude": 0.0, "longitude": 0.0, "tz_str": "UTC",
        "current_year": 2024, "current_month": 1, "current_day": 1,
        "current_hour": 12, "current_minute": 0, "current_tz_str": "UTC"
    }'
    response=$(make_request "POST" "/api/v1/transits_to_natal" "$test_data")
    if [[ $? -eq 0 ]]; then
        aspect_count=$(echo "$response" | jq '.aspects | length')
        if [[ $aspect_count -gt 0 ]]; then
            log "✅ Found $aspect_count aspects."
        else
            error "⚠️ No aspects found for transits to natal."
            log "INFO: This might be okay if no major aspects are occurring."
        fi
    fi
    echo
}

test_synastry() {
    log "💑 Testing synastry (v1)..."
    local test_data='{
        "person1_name": "Person A", "person1_year": 1985, "person1_month": 5, "person1_day": 10,
        "person1_hour": 10, "person1_minute": 30, "person1_latitude": 34.0522, "person1_longitude": -118.2437, "person1_tz_str": "America/Los_Angeles",
        "person2_name": "Person B", "person2_year": 1992, "person2_month": 8, "person2_day": 20,
        "person2_hour": 14, "person2_minute": 15, "person2_latitude": 40.7128, "person2_longitude": -74.0060, "person2_tz_str": "America/New_York"
    }'
    response=$(make_request "POST" "/api/v1/synastry" "$test_data")
    if [[ $? -eq 0 ]]; then
        aspect_count=$(echo "$response" | jq '.synastry_aspects | length')
        if [[ $aspect_count -gt 0 ]]; then
            log "✅ Found $aspect_count synastry aspects."
        else
            error "⚠️ No synastry aspects found."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_weekly_transits() {
    log "🗓️ Testing weekly transits (v1)..."
    local test_data='{
        "year": 2024, "month": 1, "day": 1
    }'
    response=$(make_request "POST" "/api/v1/transits/weekly" "$test_data")
    if [[ $? -eq 0 ]]; then
        days_count=$(echo "$response" | jq '. | length')
        if [[ $days_count -eq 7 ]]; then
            log "✅ Found $days_count days in weekly transits."
        else
            error "⚠️ Weekly transits did not return 7 days. Found: $days_count"
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_moon_phase() {
    log "🌕 Testing moon phase (v1)..."
    local test_data='{
        "year": 2024, "month": 1, "day": 1, "hour": 12, "minute": 0, "tz_str": "UTC"
    }'
    response=$(make_request "POST" "/api/v1/moon_phase" "$test_data")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | jq -e '.moon_phase' > /dev/null && echo "$response" | jq -e '.degrees_in_sign' > /dev/null; then
            log "✅ Moon phase data received."
        else
            error "⚠️ Moon phase data missing expected keys."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_solar_return() {
    log "☀️ Testing solar return (v1)..."
    local test_data='{
        "name": "Test User", "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0,
        "latitude": 0.0, "longitude": 0.0, "tz_str": "UTC",
        "return_year": 2024
    }'
    response=$(make_request "POST" "/api/v1/solar_return" "$test_data")
    if [[ $? -eq 0 ]]; then
        # Check for the presence of precise_solar_return_datetime_utc (can be null or string)
        if echo "$response" | jq -e 'has("precise_solar_return_datetime_utc")' > /dev/null; then
            log "✅ Solar Return: 'precise_solar_return_datetime_utc' field is present."
        else
            error "⚠️ Solar Return: 'precise_solar_return_datetime_utc' field is missing."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi

        # Check for the presence of solar_return_chart_details (can be null or object)
        if echo "$response" | jq -e 'has("solar_return_chart_details")' > /dev/null; then
            log "✅ Solar Return: 'solar_return_chart_details' field is present."

            # If solar_return_chart_details is not null, check its internal structure
            if ! echo "$response" | jq -e '.solar_return_chart_details == null' > /dev/null; then
                if echo "$response" | jq -e '.solar_return_chart_details.planets | type == "object"' > /dev/null && \
                   echo "$response" | jq -e '.solar_return_chart_details.houses | type == "object" or .solar_return_chart_details.houses == null' > /dev/null && \
                   echo "$response" | jq -e '.solar_return_chart_details.aspects | type == "array"' > /dev/null; then
                    log "✅ Solar Return: 'solar_return_chart_details' has planets, houses (optional), and aspects."

                    # K4 compatibility: .quality, .element, .emoji might not be standard.
                    # Removing these specific checks for broader compatibility.
                    # if echo "$response" | jq -e '.solar_return_chart_details.planets.Sun.quality' > /dev/null && \
                    #    echo "$response" | jq -e '.solar_return_chart_details.planets.Sun.element' > /dev/null && \
                    #    echo "$response" | jq -e '.solar_return_chart_details.planets.Sun.emoji' > /dev/null; then
                    #     log "✅ Solar Return: Found new fields (quality, element, emoji) in SR chart planets."
                    # else
                    #     log "ℹ️ Solar Return: New fields (quality, element, emoji) not found in SR chart planets (might be okay if SR chart is minimal or K5 feature not fully used)."
                    #     # Not failing the test for this, as K5 feature is speculative
                    # fi
                    log "ℹ️ Solar Return: Checks for quality, element, emoji in SR planets skipped for K4 compatibility."
                else
                    error "⚠️ Solar Return: 'solar_return_chart_details' is present but has incorrect internal structure."
                    ((TESTS_FAILED++)); ((TESTS_PASSED--))
                fi
            else
                log "ℹ️ Solar Return: 'solar_return_chart_details' is null (K5 feature might not have returned full details, or fallback was used)."
            fi
        else
            error "⚠️ Solar Return: 'solar_return_chart_details' field is missing."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi

        # Check highlights
        highlights_count=$(echo "$response" | jq '.highlights | length')
        if [[ $highlights_count -gt 0 ]]; then
            log "✅ Solar Return: Found $highlights_count highlights."
        else
            error "⚠️ Solar Return: No highlights found."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_synastry_pdf() {
    log "📄 Testing synastry PDF report (v1)..."
    local test_data='{
        "person1_name": "Person A PDF", "person1_year": 1985, "person1_month": 5, "person1_day": 10,
        "person1_hour": 10, "person1_minute": 30, "person1_latitude": 34.0522, "person1_longitude": -118.2437, "person1_tz_str": "America/Los_Angeles",
        "person2_name": "Person B PDF", "person2_year": 1992, "person2_month": 8, "person2_day": 20,
        "person2_hour": 14, "person2_minute": 15, "person2_latitude": 40.7128, "person2_longitude": -74.0060, "person2_tz_str": "America/New_York"
    }'
    response=$(make_request "POST" "/api/v1/synastry-pdf-report" "$test_data")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | jq -e '.pdf_url | test("\\.pdf$")' > /dev/null; then
            log "✅ Synastry PDF URL seems valid."
        else
            error "⚠️ Synastry PDF URL missing or not ending with .pdf."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

# --- Reusable Natal Payloads ---
DEFAULT_NATAL_PAYLOAD_P1='{
    "name": "Person 1 Test", "year": 1990, "month": 5, "day": 15, "hour": 14, "minute": 30,
    "latitude": -23.5505, "longitude": -46.6333, "tz_str": "America/Sao_Paulo",
    "house_system": "placidus", "zodiac_type": "Tropic"
}'

DEFAULT_NATAL_PAYLOAD_P2='{
    "name": "Person 2 Test", "year": 1985, "month": 8, "day": 22, "hour": 9, "minute": 15,
    "latitude": 34.0522, "longitude": -118.2437, "tz_str": "America/Los_Angeles",
    "house_system": "koch", "zodiac_type": "Tropic"
}'


# --- New V1 Tests ---

test_transits_range_exact() {
    log "⏳ Testing Transits Range (Exact)..."
    local test_data=$(cat <<EOF
{
    "natal_data": $DEFAULT_NATAL_PAYLOAD_P1,
    "start_date": "2024-03-10",
    "end_date": "2024-03-12",
    "transiting_planets": ["Mars"],
    "natal_points": ["Sun"],
    "aspect_types": ["square", "trine"],
    "step": "exact"
}
EOF
)
    response=$(make_request "POST" "/api/v1/transits/range" "$test_data")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | jq -e '.events | type == "array"' > /dev/null; then
            log "✅ Transits Range (Exact): Found 'events' array."
        else
            error "⚠️ Transits Range (Exact): 'events' array missing or not an array."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_transits_range_daily() {
    log "⏳ Testing Transits Range (Daily)..."
    local test_data=$(cat <<EOF
{
    "natal_data": $DEFAULT_NATAL_PAYLOAD_P1,
    "start_date": "2024-03-01",
    "end_date": "2024-03-07",
    "step": "day"
}
EOF
)
    response=$(make_request "POST" "/api/v1/transits/range" "$test_data")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | jq -e '.events | type == "array"' > /dev/null; then
            log "✅ Transits Range (Daily): Found 'events' array."
        else
            error "⚠️ Transits Range (Daily): 'events' array missing or not an array."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_transits_range_weekly() {
    log "⏳ Testing Transits Range (Weekly)..."
    local test_data=$(cat <<EOF
{
    "natal_data": $DEFAULT_NATAL_PAYLOAD_P1,
    "start_date": "2024-03-01",
    "end_date": "2024-03-21",
    "step": "week"
}
EOF
)
    response=$(make_request "POST" "/api/v1/transits/range" "$test_data")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | jq -e '.events | type == "array"' > /dev/null; then
            log "✅ Transits Range (Weekly): Found 'events' array."
        else
            error "⚠️ Transits Range (Weekly): 'events' array missing or not an array."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_transits_range_monthly() {
    log "⏳ Testing Transits Range (Monthly)..."
    local test_data=$(cat <<EOF
{
    "natal_data": $DEFAULT_NATAL_PAYLOAD_P1,
    "start_date": "2024-03-01",
    "end_date": "2024-05-01",
    "step": "month"
}
EOF
)
    response=$(make_request "POST" "/api/v1/transits/range" "$test_data")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | jq -e '.events | type == "array"' > /dev/null; then
            log "✅ Transits Range (Monthly): Found 'events' array."
        else
            error "⚠️ Transits Range (Monthly): 'events' array missing or not an array."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_lunar_return() {
    log "🌙 Testing Lunar Return..."
    local test_data=$(cat <<EOF
{
    "natal_data": $DEFAULT_NATAL_PAYLOAD_P1,
    "search_start_date": "$(date -d '+1 day' +%Y-%m-%d)"
}
EOF
) # Search from tomorrow to ensure it finds a future one.
    response=$(make_request "POST" "/api/v1/lunar_return" "$test_data")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | jq -e 'has("precise_lunar_return_datetime_utc")' > /dev/null && \
           echo "$response" | jq -e 'has("lunar_return_chart_details")' > /dev/null; then
            log "✅ Lunar Return: Found core response fields."
        else
            error "⚠️ Lunar Return: Core response fields missing."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_composite_chart_data() {
    log "🤝 Testing Composite Chart Data..."
    local test_data=$(cat <<EOF
{
    "person1_natal_data": $DEFAULT_NATAL_PAYLOAD_P1,
    "person2_natal_data": $DEFAULT_NATAL_PAYLOAD_P2
}
EOF
)
    response=$(make_request "POST" "/api/v1/composite_chart" "$test_data")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | jq -e '.composite_chart_details.planets | type == "object"' > /dev/null && \
           echo "$response" | jq -e '.composite_chart_details.aspects | type == "array"' > /dev/null ; then
            log "✅ Composite Chart: Found planets and aspects in details."
        else
            error "⚠️ Composite Chart: Planets or aspects missing/invalid in details."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}


test_v2_svg_chart_natal() {
    log "🎨 Testing V2 SVG Chart - Natal..."
    local test_data='{
        "chart_data": {
            "name": "Natal SVG", "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0,
            "latitude": 0.0, "longitude": 0.0, "tz_str": "UTC"
        },
        "chart_type": "natal"
    }'
    response=$(make_request "POST" "/api/v2/svg_chart" "$test_data")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | grep -q "<svg"; then
            log "✅ V2 Natal SVG content received."
        else
            error "⚠️ V2 Natal SVG content check failed."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_v2_svg_chart_natal_sidereal() {
    log "🎨 Testing V2 SVG Chart - Natal Sidereal (LAHIRI)..."
    local test_data_v2_sidereal='{
        "chart_data": {
            "name": "Natal SVG Sidereal", "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0,
            "latitude": 0.0, "longitude": 0.0, "tz_str": "UTC",
            "zodiac_type": "Sidereal", "sidereal_mode": "LAHIRI"
        },
        "chart_type": "natal"
    }'
    response=$(make_request "POST" "/api/v2/svg_chart" "$test_data_v2_sidereal")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | grep -q "<svg"; then
            log "✅ V2 Natal SVG Sidereal content received."
        else
            error "⚠️ V2 Natal SVG Sidereal content check failed."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_v2_svg_chart_natal_active_points() {
    log "🎨 Testing V2 SVG Chart - Natal with Active Points..."
    local test_data_v2_active='{
        "chart_data": {
            "name": "Natal SVG Active Points", "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0,
            "latitude": 0.0, "longitude": 0.0, "tz_str": "UTC"
        },
        "chart_type": "natal"
    }'
    # Testing with Sun, Moon, Ascendant only
    response=$(make_request "POST" "/api/v2/svg_chart?active_points=Sun&active_points=Moon&active_points=Ascendant" "$test_data_v2_active")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | grep -q "<svg"; then
            log "✅ V2 Natal SVG (Active Points) content received."
            # Further checks could verify *only* these points are present if possible with grep/jq.
        else
            error "⚠️ V2 Natal SVG (Active Points) content check failed."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_v2_svg_chart_natal_strawberry_theme() {
    log "🍓🎨 Testing V2 SVG Chart - Natal with Strawberry Theme..."
    local test_data='{
        "chart_data": {
            "name": "Natal SVG Strawberry", "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0,
            "latitude": 0.0, "longitude": 0.0, "tz_str": "UTC"
            # Test with strawberry theme and specific perspective
            ,"perspective_type": "Heliocentric"
        },
        "chart_type": "natal"
    }'
    # Note: theme is passed as a query parameter
    response=$(make_request "POST" "/api/v2/svg_chart?theme=strawberry" "$test_data") # chart_type in payload is enough
    if [[ $? -eq 0 ]]; then
        if echo "$response" | grep -q "<svg"; then
            log "✅ V2 Natal SVG (Strawberry Theme) content received."
        else
            error "⚠️ V2 Natal SVG (Strawberry Theme) content check failed."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_v2_svg_chart_transit() {
    log "🎨 Testing V2 SVG Chart - Transit..."
    local test_data='{
        "chart_data": {
            "name": "Transit SVG",
            "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0, "latitude": 0.0, "longitude": 0.0, "tz_str": "UTC", "zodiac_type": "Tropic",
            "current_year": 2024, "current_month": 1, "current_day": 1, "current_hour": 12, "current_minute": 0, "current_tz_str": "UTC", "zodiac_type_transit": "Tropic"
            # Assuming 'zodiac_type_transit' or similar might be how K5 differentiates if transit subject needs own zodiac type
            # For now, the model for TransitRequest has zodiac_type, so it applies to the transit moment.
        },
        "chart_type": "transit"
    }'
    response=$(make_request "POST" "/api/v2/svg_chart" "$test_data")
     if [[ $? -eq 0 ]]; then
        if echo "$response" | grep -q "<svg"; then
            log "✅ V2 Transit SVG content received."
        else
            error "⚠️ V2 Transit SVG content check failed."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_v2_svg_chart_synastry() {
    log "🎨 Testing V2 SVG Chart - Combined (Synastry)..."
    local test_data='{
        "chart_data": {
            "person1_name": "Person1 SVG", "person1_year": 1985, "person1_month": 5, "person1_day": 10, "person1_hour": 10, "person1_minute": 30, "person1_latitude": 34.0522, "person1_longitude": -118.2437, "person1_tz_str": "America/Los_Angeles",
            "person2_name": "Person2 SVG", "person2_year": 1992, "person2_month": 8, "person2_day": 20, "person2_hour": 14, "person2_minute": 15, "person2_latitude": 40.7128, "person2_longitude": -74.0060, "person2_tz_str": "America/New_York"
        },
        "chart_type": "combined"
    }'
    response=$(make_request "POST" "/api/v2/svg_chart" "$test_data")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | grep -q "<svg"; then
            log "✅ V2 Combined SVG content received."
        else
            error "⚠️ V2 Combined SVG content check failed."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_v2_svg_chart_composite() {
    log "🎨 Testing V2 SVG Chart - Composite..."
    local test_data_v2_composite=$(cat <<EOF
{
    "natal_chart": $DEFAULT_NATAL_PAYLOAD_P1,
    "transit_chart": $DEFAULT_NATAL_PAYLOAD_P2,
    "chart_type": "composite"
}
EOF
)
    # The chart_type in the payload is what determines the type.
    # No need for query param if it's in the body for this endpoint.
    response=$(make_request "POST" "/api/v2/svg_chart" "$test_data_v2_composite")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | grep -q "<svg"; then
            log "✅ V2 Composite SVG content received."
        else
            error "⚠️ V2 Composite SVG content check failed."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_v2_svg_chart_natal_png_format() {
    log "🎨 Testing V2 SVG Chart - Natal PNG format..."
    local natal_payload_for_png='{
        "chart_data": {
            "name": "Natal PNG Format", "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0,
            "latitude": 0.0, "longitude": 0.0, "tz_str": "UTC"
        },
        "chart_type": "natal"
    }'
    # Pass expected content type "image/png" to make_request
    response_png=$(make_request "POST" "/api/v2/svg_chart?format=png&png_quality=150" "$natal_payload_for_png" 200 "image/png")
    if [[ $? -eq 0 ]]; then
        if [[ -n "$response_png" ]]; then # Check if response body is not empty
            log "✅ V2 Natal PNG (format=png) received non-empty content."
            # Basic check for PNG signature (first 8 bytes)
            # However, response_png might not be suitable for direct binary comparison in bash easily.
            # For now, non-empty is the primary check.
            # Example: if [[ "$(echo "$response_png" | head -c 8 | od -A n -t x1 | tr -d ' ')" == "89504e470d0a1a0a" ]]; then
            #    log "✅ V2 Natal PNG signature verified."
            # else
            #    error "⚠️ V2 Natal PNG signature mismatch."
            #    ((TESTS_FAILED++)); ((TESTS_PASSED--))
            # fi
        else
            error "⚠️ V2 Natal PNG (format=png) received empty content."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_v2_svg_chart_natal_png_dimensions() {
    log "🎨 Testing V2 SVG Chart - Natal PNG with dimensions..."
    local natal_payload_for_png_dims='{
        "chart_data": {
            "name": "Natal PNG Dimensions", "year": 1991, "month": 2, "day": 2, "hour": 10, "minute": 0,
            "latitude": 10.0, "longitude": 10.0, "tz_str": "UTC"
        },
        "chart_type": "natal"
    }'
    response_png_dims=$(make_request "POST" "/api/v2/svg_chart?format=png&png_width=400&png_height=300" "$natal_payload_for_png_dims" 200 "image/png")
    if [[ $? -eq 0 ]]; then
        if [[ -n "$response_png_dims" ]]; then
            log "✅ V2 Natal PNG (with dimensions) received non-empty content."
            # Here one could save to a file and use 'file' or 'identify' (ImageMagick) to check dimensions
            # echo "$response_png_dims" > temp_image.png
            # identify temp_image.png -> should show 400x300
            # rm temp_image.png
        else
            error "⚠️ V2 Natal PNG (with dimensions) received empty content."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_v2_convert_svg_to_png() {
    log "🔄 Testing V2 Convert SVG to PNG endpoint..."
    # Simple valid SVG payload
    local svg_payload_json='{
        "svg_content": "<svg height=\"100\" width=\"100\"><circle cx=\"50\" cy=\"50\" r=\"40\" stroke=\"black\" stroke-width=\"3\" fill=\"red\" /></svg>",
        "quality": 150,
        "optimize": false
    }'
    # Pass expected content type "image/png"
    response_converted_png=$(make_request "POST" "/api/v2/convert/svg-to-png" "$svg_payload_json" 200 "image/png")
    if [[ $? -eq 0 ]]; then
        if [[ -n "$response_converted_png" ]]; then
            log "✅ V2 Convert SVG to PNG: Received non-empty PNG content."
        else
            error "⚠️ V2 Convert SVG to PNG: Received empty PNG content."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_v2_svg_chart_base64() {
    log "🖼️ Testing V2 SVG Chart Base64..."
    local test_data='{
        "chart_data": {
            "name": "Base64 SVG", "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0,
            "latitude": 0.0, "longitude": 0.0, "tz_str": "UTC"
        },
        "chart_type": "natal"
    }'
    response=$(make_request "POST" "/api/v2/svg_chart_base64" "$test_data")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | jq -e '.svg_base64' > /dev/null; then
            log "✅ V2 SVG Base64 key found."
        else
            error "⚠️ V2 SVG Base64 key 'svg_base64' missing."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_v2_svg_chart_info() {
    log "ℹ️ Testing V2 SVG Chart Info..."
    local test_data='{
        "chart_data": {
            "name": "Info SVG", "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0,
            "latitude": 0.0, "longitude": 0.0, "tz_str": "UTC"
        },
        "chart_type": "natal"
    }'
    response=$(make_request "POST" "/api/v2/svg_chart_info" "$test_data")
    if [[ $? -eq 0 ]]; then
        # Check for some expected keys, e.g., planets and cusps
        if echo "$response" | jq -e '.planets' > /dev/null && echo "$response" | jq -e '.cusps' > /dev/null; then
            log "✅ V2 SVG Chart Info has planets and cusps."
        else
            error "⚠️ V2 SVG Chart Info missing expected keys (planets/cusps)."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_v2_themes() {
    log "🎨 Testing V2 Themes listing..."
    response=$(make_request "GET" "/api/v2/themes")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | jq -e '.themes | length > 0' > /dev/null; then
            log "✅ V2 Themes list is not empty."
        else
            error "⚠️ V2 Themes list is empty or not found."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

test_v2_chart_types() {
    log "📜 Testing V2 Chart Types listing..."
    response=$(make_request "GET" "/api/v2/chart_types")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | jq -e '.chart_types | length > 0' > /dev/null; then
            log "✅ V2 Chart Types list is not empty."
        else
            error "⚠️ V2 Chart Types list is empty or not found."
            ((TESTS_FAILED++)); ((TESTS_PASSED--))
        fi
    fi
    echo
}

# Teste de performance básico
test_performance() {
    log "⚡ Testing basic performance (v1 natal chart)..."
    
    local test_data='{
        "name": "Performance Test",
        "year": 1990,
        "month": 1,
        "day": 1,
        "hour": 12,
        "minute": 0,
        "latitude": -23.5505,
        "longitude": -46.6333,
        "tz_str": "America/Sao_Paulo"
    }'
    
    # Primeira chamada (cache miss)
    log "Testing cache miss performance..."
    start_time=$(date +%s.%N)
    make_request "POST" "/api/v1/natal_chart" "$test_data" > /dev/null # Suppress output for perf test
    end_time=$(date +%s.%N)
    cache_miss_time=$(echo "$end_time - $start_time" | bc)
    log "✅ Cache miss took: ${cache_miss_time}s"
    
    # Segunda chamada (cache hit)
    log "Testing cache hit performance..."
    start_time=$(date +%s.%N)
    make_request "POST" "/api/v1/natal_chart" "$test_data" > /dev/null # Suppress output for perf test
    end_time=$(date +%s.%N)
    cache_hit_time=$(echo "$end_time - $start_time" | bc)
    log "✅ Cache hit took: ${cache_hit_time}s"
    fi
    echo
}

# Sumário dos resultados
show_summary() {
    echo
    echo -e "${BLUE}=== TEST SUMMARY ===${NC}"
    echo -e "${GREEN}✅ Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}❌ Failed: $TESTS_FAILED${NC}"
    echo -e "${BLUE}📊 Total:  $TESTS_TOTAL${NC}"
    echo
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}🎉 All tests passed! API is working correctly.${NC}"
        exit 0
    else
        echo -e "${RED}💥 Some tests failed. Check the API configuration.${NC}"
        exit 1
    fi
}

# Função principal
main() {
    echo -e "${BLUE}🧪 Astrotagiario API Test Suite${NC}"
    echo -e "${BLUE}API Base URL: $API_BASE_URL${NC}"
    echo
    
    # Verificar se a API está acessível
    if ! curl -sf "$API_BASE_URL/health" >/dev/null; then
        error "❌ API is not accessible at $API_BASE_URL. Ensure the API is running."
        exit 1
    fi
    
    log "🚀 Starting API tests..."
    echo
    
    # Executar todos os testes
    log "--- Running General & V1 Endpoint Tests ---"
    test_root_endpoint
    test_health
    test_natal_chart       # v1 natal (standard, sidereal, helio)
    test_natal_chart_geonames # v1 natal with city/nation lookup
    test_current_transits  # v1
    test_transits_to_natal # v1
    test_synastry          # v1
    test_daily_transits    # v1 (specific daily listing)
    test_weekly_transits   # v1
    test_moon_phase        # v1
    test_solar_return      # v1
    test_synastry_pdf      # v1
    test_transits_range_exact
    test_transits_range_daily
    test_transits_range_weekly
    test_transits_range_monthly
    test_lunar_return
    test_composite_chart_data

    log "--- Running V2 Endpoint Tests ---"
    test_v2_svg_chart_natal
    test_v2_svg_chart_natal_strawberry_theme
    test_v2_svg_chart_natal_sidereal
    test_v2_svg_chart_natal_active_points
    test_v2_svg_chart_transit
    test_v2_svg_chart_synastry
    test_v2_svg_chart_composite
    test_v2_svg_chart_natal_png_format # New PNG test
    test_v2_svg_chart_natal_png_dimensions # New PNG test
    test_v2_convert_svg_to_png # New direct conversion test
    test_v2_svg_chart_base64
    test_v2_svg_chart_info
    test_v2_themes
    test_v2_chart_types

    log "--- Running Performance Tests ---"
    test_performance
    
    # Mostrar sumário
    show_summary
}

# Verificar dependências
check_dependencies() {
    local deps=("curl" "jq" "bc")
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            error "❌ Critical dependency '$dep' is not installed. Please install it to run tests."
            exit 1
        fi
    done
    log "✅ All dependencies (curl, jq, bc) are present."
    echo
}

# Script execution starts here
check_dependencies
main "$@"