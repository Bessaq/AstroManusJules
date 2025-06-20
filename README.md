# Astrological API Project

## 1. Project Overview

This project provides a comprehensive FastAPI-based API for astrological calculations. It leverages the Kerykeion library (v5.0.0a5) to offer a range of services, including natal chart data, transit information, synastry analysis, composite charts, solar/lunar returns, and enhanced SVG chart generation. The API is designed with a data-driven approach, making it suitable for integration into various applications, including those using AI and LLMs.

## 2. Features

*   **Natal Chart Data:** Detailed astrological information for a birth chart (planets, houses, aspects, elements, qualities).
*   **Transit Calculations:**
    *   Current transiting planet positions.
    *   Transits of current planets to a natal chart.
    *   Daily and weekly summaries of transit aspects.
    *   Detailed transit events over a specified date range, with selectable periodicity (exact, daily, weekly, monthly).
*   **Synastry Analysis:** Calculation of aspects and compatibility scores between two natal charts.
*   **Composite Charts:** Generation of midpoint composite chart data between two natal charts.
*   **Solar Returns:** Calculation of precise Solar Return dates and detailed chart data for the Solar Return moment.
*   **Lunar Returns:** Calculation of precise Lunar Return dates and detailed chart data for the Lunar Return moment.
*   **SVG Chart Generation (Enhanced v2 API - `/api/v2/svg_chart`):**
    *   Generates high-quality SVG charts for natal, transit, synastry, and composite types.
    *   Customizable themes (light, dark, colorful, strawberry).
    *   Option to specify active points to be drawn on the chart.
    *   Optional PNG output format for generated charts, with quality and dimension controls.
    *   Base64 encoded SVG option.
    *   Endpoint to get chart generation metadata (`/api/v2/svg_chart_info`).
*   **SVG to PNG Conversion Utility:** Dedicated endpoint (`/api/v2/convert/svg-to-png`) to convert arbitrary SVG content to PNG.
*   **Synastry PDF Reports:** Generates a PDF report summarizing synastry data.
*   **Moon Phases:** Provides the moon phase and illumination for a given date.
*   **Advanced Calculation Parameters:** Supports Tropical and Sidereal zodiacs (with various Ayanamsas/sidereal modes), multiple house systems, and different calculation perspectives (Geocentric, Heliocentric).
*   **Health Check:** `/health` endpoint to verify API status.

## 3. Getting Started / Setup

### Prerequisites

*   Python 3.9 or higher.
*   Access to a terminal or command prompt.
*   `pip` for installing Python packages.
*   Git for cloning the repository.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_folder_name>
    ```
    (Replace `<repository_url>` and `<repository_folder_name>` with actual values)

2.  **Create and activate a virtual environment (recommended):**

    *   **Linux/macOS:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

      #### System Dependencies for Image Conversion (for PNG output)

      The SVG to PNG conversion feature relies on the `cairosvg` library, which in turn depends on Cairo graphics libraries being installed on your system. If you encounter issues installing `cairosvg` or using PNG conversion, you may need to install these system packages:

      *   **Debian/Ubuntu:**
          ```bash
          sudo apt-get update && sudo apt-get install -y libcairo2-dev pkg-config python3-dev
          ```
      *   **Fedora/CentOS/RHEL:**
          ```bash
          sudo yum install cairo-devel pkgconfig python3-devel
          ```
      *   **macOS (using Homebrew):**
          ```bash
          brew install cairo pkg-config
          ```
      After installing these system dependencies, you might need to reinstall the Python packages:
      ```bash
      pip install --force-reinstall -r requirements.txt
      ```

4.  **(Optional) GeoNames Username for Live Geocoding:**
    If you intend to frequently use city/nation names for location input (instead of providing latitude/longitude/timezone directly), it's recommended to get a free GeoNames username from [http://www.geonames.org/login](http://www.geonames.org/login).
    You can then set it as an environment variable (e.g., `GEONAMES_USERNAME="your_username"`) or pass it as a parameter where supported by Kerykeion (though the current API abstracts this via `astro_helpers.py` which uses a default or expects manual geo-input). For robust applications, providing explicit lat/lon/tz_str is recommended.

### Running the Application

*   **Linux/macOS:**
    Make the startup script executable:
    ```bash
    chmod +x start.sh
    ```
    Then run:
    ```bash
    ./start.sh
    ```

*   **Windows:**
    ```batch
    start.bat
    ```

The API will typically be available at `http://localhost:8000` (or `http://0.0.0.0:8000`).
You can access the interactive API documentation (Swagger UI) at `http://localhost:8000/docs`.

## 4. API Endpoint Documentation

The API provides several endpoints for various astrological calculations and chart generation.

**Authentication:** Most endpoints require an API key passed in the `X-API-KEY` header. For development and testing, the default key is often `testapikey` (this might be configured in `app/security.py` or via environment variables).

### 4.1 Health Check

*   **Endpoint:** `GET /health`
*   **Description:** Verifies that the API is running and responsive.
*   **Request:** None
*   **Response (200 OK):**
    ```json
    {
      "status": "healthy"
    }
    ```

### 4.2 Natal Chart Data

*   **Endpoint:** `POST /api/v1/natal_chart`
*   **Description:** Calculates and returns detailed natal chart data.
*   **Request Body (`NatalChartRequest`):**
    ```json
    {
      "name": "Test Subject",
      "year": 1990,
      "month": 1,
      "day": 15,
      "hour": 10,
      "minute": 30,
      "latitude": -23.5505,
      "longitude": -46.6333,
      "tz_str": "America/Sao_Paulo",
      "city": "Sao Paulo",
      "nation": "BR",
      "house_system": "placidus",
      "zodiac_type": "Tropic",
      "sidereal_mode": null,
      "perspective_type": "Apparent Geocentric"
    }
    ```
*   **Response (200 OK - `NatalChartResponse`):** Contains `input_data`, `resolved_location`, `planets` (dictionary with detailed `PlanetData` including quality, element, emoji), `houses` (dictionary with detailed `HouseCuspData` including quality, element, emoji), `ascendant`, `midheaven`, `aspects`, `house_system`.

### 4.3 Transit Data

#### 4.3.1 Current Transits
*   **Endpoint:** `POST /api/v1/current_transits`
*   **Description:** Returns the current positions of transiting planets.
*   **Request Body (`TransitRequest`):** Contains date, time, and location data (lat, lon, tz_str, or city/nation) for the desired transit moment. Also accepts `zodiac_type`, `sidereal_mode`, `perspective_type`.
*   **Response (200 OK - `CurrentTransitsResponse`):** Contains `input_data` and `planets` (list of `PlanetPosition` data for transiting planets).

#### 4.3.2 Transits to Natal Chart
*   **Endpoint:** `POST /api/v1/transits_to_natal`
*   **Description:** Calculates aspects of transiting planets to natal chart positions.
*   **Request Body (`TransitsToNatalRequest`):**
    ```json
    {
      "natal_data": { /* NatalChartRequest object */ },
      "transit_data": { /* TransitRequest object for the transit moment */ }
    }
    ```
*   **Response (200 OK - `TransitsToNatalResponse`):** Contains `natal_input`, `transit_input`, `transit_planets_positions`, and `aspects_to_natal`.

#### 4.3.3 Daily Transits Summary
*   **Endpoint:** `POST /api/v1/transits/daily`
*   **Description:** Returns active planetary aspects for a specific day (GMT).
*   **Request Body (`DailyTransitRequest`):** `{"year": 2024, "month": 8, "day": 15}`
*   **Response (200 OK - `DailyTransitsResponse`):** Contains `aspects` list for the day.

#### 4.3.4 Weekly Transits Summary
*   **Endpoint:** `POST /api/v1/transits/weekly`
*   **Description:** Returns a 7-day summary of transit aspects starting from a given date.
*   **Request Body (`DailyTransitRequest` for start date):** `{"year": 2024, "month": 8, "day": 15}`
*   **Response (200 OK - `WeeklyTransitsResponse`):** Contains a list of `days`, each with `date`, `aspects`, and `summary`.

#### 4.3.5 Transit Events Over a Range
*   **Endpoint:** `POST /api/v1/transits/range`
*   **Description:** Calculates detailed transit events (aspects of transiting planets to a natal chart) over a specified period, or periodic snapshots.
*   **Request Body (`TransitRangeRequest`):**
    ```json
    {
      "natal_data": { /* NatalChartRequest object */ },
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD",
      "step": "exact",
      "transiting_planets": ["Mars", "Jupiter"],
      "natal_points": ["Sun", "Moon"],
      "aspect_types": ["conjunction", "square"]
    }
    ```
*   **Response (200 OK - `TransitRangeResponse`):** Contains `request_data`, `events` (list of `TransitEventData`), and `summary`.

### 4.4 Synastry & Composite Charts

#### 4.4.1 Synastry (Relationship Analysis)
*   **Endpoint:** `POST /api/v1/synastry`
*   **Description:** Calculates aspects and a compatibility score between two natal charts.
*   **Request Body (`SynastryRequest`):** Contains `person1: NatalChartRequest` and `person2: NatalChartRequest`.
*   **Response (200 OK - `SynastryResponse`):** Contains input data, `aspects`, `compatibility_score`, and `summary`.

#### 4.4.2 Synastry PDF Report
*   **Endpoint:** `POST /api/v1/synastry-pdf-report`
*   **Description:** Generates a URL for a PDF report of synastry data. (Relies on `manus-md-to-pdf` in the server environment).
*   **Request Body (`SynastryRequest`):** Same as `/api/v1/synastry`.
*   **Response (200 OK - `SynastryPDFResponse`):** `{"pdf_url": "path_to_report.pdf"}`

#### 4.4.3 Composite Chart Data (Midpoint Method)
*   **Endpoint:** `POST /api/v1/composite_chart`
*   **Description:** Calculates a composite chart using the midpoint method for two natal charts.
*   **Request Body (`CompositeChartRequest`):**
    ```json
    {
      "person1_natal_data": { /* NatalChartRequest object */ },
      "person2_natal_data": { /* NatalChartRequest object */ }
    }
    ```
*   **Response (200 OK - `CompositeChartResponse`):** Contains `request_data` and `composite_chart_details` (with planets, aspects; houses/angles are optional as their calculation varies for composites).

### 4.5 Returns & Cycles

#### 4.5.1 Solar Return
*   **Endpoint:** `POST /api/v1/solar_return`
*   **Description:** Calculates the precise Solar Return date/time and full chart data for that moment.
*   **Request Body (`SolarReturnRequest`):** Contains natal chart data and the `return_year` (target year for the SR).
*   **Response (200 OK - `SolarReturnResponse`):** Contains `precise_solar_return_datetime_utc`, `solar_return_chart_details` (full chart data including planets, houses, aspects for the SR chart), and `highlights`.

#### 4.5.2 Lunar Return
*   **Endpoint:** `POST /api/v1/lunar_return`
*   **Description:** Calculates the next Lunar Return date/time and full chart data for that moment.
*   **Request Body (`LunarReturnRequest`):** Contains `natal_data` and `search_start_date` (YYYY-MM-DD).
*   **Response (200 OK - `LunarReturnResponse`):** Contains `precise_lunar_return_datetime_utc`, `lunar_return_chart_details` (full chart data), and `highlights`. (Note: Kerykeion v5 integration for exact calculation is speculative).

#### 4.5.3 Moon Phase
*   **Endpoint:** `POST /api/v1/moon_phase`
*   **Description:** Provides the moon phase and illumination percentage for a given date.
*   **Request Body (`MoonPhaseRequest`):** `{"year": 2024, "month": 8, "day": 15}`
*   **Response (200 OK - `MoonPhaseResponse`):** `{"phase": "Waning Gibbous", "illumination": 75.2}`

### 4.6 Enhanced SVG Chart Generation (v2)

These endpoints generate high-quality SVG charts.

#### 4.6.1 Generate SVG Chart
*   **Endpoint:** `POST /api/v2/svg_chart`
*   **Description:** Generates an SVG chart based on the provided data and parameters.
*   **Query Parameters:**
    *   `theme: str` - Optional. "light" (default), "dark", "colorful", "strawberry".
    *   `high_quality: bool` - Optional. Default `True`.
    *   `show_aspects: bool` - Optional. Default `True`.
    *   `active_points: List[str]` - Optional. E.g., `active_points=Sun&active_points=Moon`. Filters points drawn.
    *   `format: Literal["svg", "png"]` - Optional. Default "svg". Output format.
    *   `png_quality: int` - Optional. Default 300 (configurable via `IMG_DEFAULT_PNG_QUALITY`). DPI for PNG output (e.g., 72-600, configurable via `IMG_MIN/MAX_PNG_QUALITY`).
    *   `png_width: Optional[int]` - Optional. Desired width in pixels for PNG output (max configurable via `IMG_MAX_PNG_WIDTH`).
    *   `png_height: Optional[int]` - Optional. Desired height in pixels for PNG output (max configurable via `IMG_MAX_PNG_HEIGHT`).
*   **Request Body (`SVGChartRequest`):**
    ```json
    {
      "chart_type": "natal",
      "natal_chart": { /* NatalChartRequest object for person 1 or main subject */ },
      "transit_chart": { /* NatalChartRequest object for transit date/time or person 2 */ }

    }
    ```
*   **Response (200 OK):** SVG image (`image/svg+xml`).

#### 4.6.2 Generate SVG Chart (Base64 Encoded)
*   **Endpoint:** `POST /api/v2/svg_chart_base64`
*   **Description:** Generates an SVG chart and returns it as a Base64 encoded string within a JSON response.
*   **Query Parameters:** Same as `/api/v2/svg_chart`.
*   **Request Body (`SVGChartRequest`):** Same as `/api/v2/svg_chart`.
*   **Response (200 OK):**
    ```json
    {
      "svg_base64": "...",
      "data_uri": "data:image/svg+xml;base64,...",
      "chart_info": { /* metadata about the generated chart */ }
    }
    ```

#### 4.6.3 Get SVG Chart Info
*   **Endpoint:** `POST /api/v2/svg_chart_info`
*   **Description:** Returns metadata about the chart that *would be* generated with the given data, without generating the full SVG.
*   **Request Body (`SVGChartRequest`):** Same as `/api/v2/svg_chart`.
*   **Response (200 OK):** JSON object with chart information.

#### 4.6.4 Get Available Themes
*   **Endpoint:** `GET /api/v2/themes`
*   **Description:** Lists available themes for SVG charts.
*   **Response (200 OK):** JSON object with theme details.

#### 4.6.5 Get Available Chart Types (for SVG)
*   **Endpoint:** `GET /api/v2/chart_types`
*   **Description:** Lists chart types supported by the enhanced SVG generator and their configurations.
*   **Response (200 OK):** JSON object with chart type details.

      #### 4.6.6 Convert Arbitrary SVG to PNG
      *   **Endpoint:** `POST /api/v2/convert/svg-to-png`
      *   **Description:** Converts an arbitrary SVG string (provided in the request body) to a PNG image.
      *   **Request Body (`SVGToPNGConversionRequest`):**
          ```json
          {
            "svg_content": "<svg>...</svg>",
            "quality": 300, // Optional, DPI, default from IMG_DEFAULT_PNG_QUALITY
            "width": null,  // Optional, desired width
            "height": null, // Optional, desired height
            "optimize": true, // Optional, default from IMG_ENABLE_PNG_OPTIMIZATION
            "compression_level": 6 // Optional, default from IMG_PNG_COMPRESSION_LEVEL (0-9)
          }
          ```
      *   **Response (200 OK):** PNG image (`image/png`).

## 5. Kerykeion Library & Development Notes

### 5.1 Kerykeion Version
This project currently uses **Kerykeion v5.0.0a5**. As this is an alpha version, some of its newer features (especially those related to specific factories or modules like Planetary Returns) are integrated speculatively based on available information. Full behavior and API stability of these alpha features will become clearer with further testing and official Kerykeion v5 documentation. The core astrological calculations provided by Kerykeion are expected to be highly accurate, building upon the Swiss Ephemeris.

### 5.2 Data-Driven Approach
A key design philosophy of this API, inherited from Kerykeion, is its data-driven approach. Most endpoints provide rich JSON responses containing detailed astrological data (e.g., planet positions, signs, elements, qualities, aspects, house cusps). This structured data is ideal for integration into other applications, data analysis pipelines, or for use with AI/LLM systems.

### 5.3 Testing
The project includes a comprehensive API test script located at `tools/test_api.sh`. This script can be used by developers to:
*   Verify that all API endpoints are operational.
*   Check basic request/response integrity.
*   Confirm that new features and parameters are working as expected.

To run the tests, ensure the API server is running (e.g., using `start.sh` or `start.bat`), and then execute the script from the project root:
```bash
# Ensure the script is executable (Linux/macOS)
chmod +x tools/test_api.sh

# Run the tests
./tools/test_api.sh
```
The script uses `curl` and `jq` (command-line JSON processor), so these tools should be installed on your system if you wish to run it.

### 5.4 SVG Generation
The primary SVG generation is handled by the `/api/v2/svg_chart` endpoint, which uses a custom `EnhancedSVGGenerator`. This generator provides high-quality, themed charts with various customization options. While Kerykeion itself has SVG generation capabilities (`KerykeionChartSVG`), this project uses its own enhanced generator for the v2 API to offer specific visual styles and features.

   ### 5.5 Configuration via Environment Variables
   Some application settings can be configured using environment variables:
   *   **GeoNames:** Set `GEONAMES_USERNAME` with your personal GeoNames username for robust geocoding.
   *   **Image Conversion (PNG):** Settings for default DPI, max/min dimensions, and optimization for PNG conversion can be set with variables prefixed by `IMG_` (e.g., `IMG_DEFAULT_PNG_QUALITY=250`, `IMG_ENABLE_PNG_OPTIMIZATION=false`). Refer to `app/config/image_settings.py` for all available image settings.

## 6. Contribution & Future Development
(Placeholder for future contribution guidelines or notes on planned features beyond the current scope.)

---
*This README was last updated on $(date +'%Y-%m-%d').*
