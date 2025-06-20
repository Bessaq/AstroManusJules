from fastapi import APIRouter, HTTPException, Depends
from kerykeion import AstrologicalSubject
try:
    from kerykeion.planetary_return import SolarReturn
except ImportError:
    SolarReturn = None # Placeholder if import fails
from app.security import verify_api_key
from app.utils.astro_helpers import create_subject, get_house_from_kerykeion_attribute, PLANETS_MAP, HOUSE_NUMBER_TO_NAME_BASE # Added PLANETS_MAP, HOUSE_NUMBER_TO_NAME_BASE
from app.models import (
    NatalChartRequest, SolarReturnRequestModel as SolarReturnRequest,
    SolarReturnResponseModel as SolarReturnResponse, SolarReturnChartDetails,
    PlanetData, HouseCuspData, AspectData, # Added these for later use
    LunarReturnRequest, LunarReturnResponse, LunarReturnChartDetails # Lunar Return Models
)
from typing import List, Dict, Optional, Any, Tuple # Added Optional, Any, Tuple
from pydantic import BaseModel, Field # BaseModel, Field already here but kept for clarity
from datetime import datetime, timedelta
import math
import pytz # For timezone aware datetime in mock

# Speculative import for Kerykeion Lunar Return
try:
    # Option 1: from kerykeion.planetary_return import LunarReturn, PlanetaryReturn (if generic)
    # Option 2: from kerykeion.returns import LunarReturn
    # For now, let's assume a similar structure to SolarReturn if it exists directly
    from kerykeion.planetary_return import LunarReturn
    KERYKEION_LUNAR_RETURN_AVAILABLE = True
except ImportError:
    KERYKEION_LUNAR_RETURN_AVAILABLE = False
    LunarReturn = None # Placeholder

router = APIRouter(
    prefix="/api/v1",
    tags=["Moon Phase & Solar Return"],
    dependencies=[Depends(verify_api_key)]
)

# Modelos para fases da lua
class MoonPhaseRequest(BaseModel):
    year: int = Field(..., description="Ano")
    month: int = Field(..., description="Mês (1-12)")
    day: int = Field(..., description="Dia")

class MoonPhaseResponse(BaseModel):
    phase: str = Field(..., description="Fase da lua")
    illumination: float = Field(..., description="Percentual de iluminação (0-100)")

# Modelos para retorno solar agora são importados de app.models

def calculate_moon_phase(year: int, month: int, day: int) -> tuple:
    """
    Calcula a fase da lua para uma data específica.
    Baseado no algoritmo de cálculo de fases lunares.
    """
    try:
        # Criar subject para obter posição da lua
        subject = AstrologicalSubject(
            name=f"Moon_{year}_{month}_{day}",
            year=year, month=month, day=day,
            hour=12, minute=0,
            lat=0.0, lng=0.0,
            tz_str="UTC"
        )

        if not hasattr(subject, 'moon') or not subject.moon:
            return "unknown", 0.0

        moon_pos = subject.moon.position
        sun_pos = subject.sun.position

        # Calcular diferença angular entre Sol e Lua
        diff = moon_pos - sun_pos
        if diff < 0:
            diff += 360

        # Calcular iluminação baseada na diferença angular
        # 0° = Lua Nova (0%), 180° = Lua Cheia (100%)
        illumination = (1 - math.cos(math.radians(diff))) / 2 * 100

        # Determinar fase baseada na diferença angular
        if diff < 45 or diff >= 315:
            phase = "Nova"
        elif 45 <= diff < 135:
            phase = "Crescente"
        elif 135 <= diff < 225:
            phase = "Cheia"
        else:
            phase = "Minguante"

        return phase, round(illumination, 1)

    except Exception as e:
        print(f"Erro no cálculo da fase da lua: {e}")
        return "unknown", 0.0

def calculate_solar_return(birth_year: int, birth_month: int, birth_day: int,
                          birth_hour: int, birth_minute: int,
                          lat: float, lng: float, tz_str: str,
                          target_sr_year: int,
                          # Pass natal chart request model attributes for SR subject creation
                          natal_name: Optional[str],
                          natal_house_system: Optional[Any], # HouseSystem Enum or str
                          natal_zodiac_type: Optional[str],
                          natal_sidereal_mode: Optional[str],
                          natal_perspective_type: Optional[str]
                          ) -> tuple[Optional[datetime], Optional[SolarReturnChartDetails], List[str]]:
    """
    Calcula a data do próximo retorno solar, detalhes do mapa SR e gera destaques.
    Tenta usar Kerykeion v5 SolarReturn, senão usa fallback.
    Returns a tuple: (precise_datetime_obj, chart_details_obj, highlights_list)
    """
    precise_sr_datetime: Optional[datetime] = None
    sr_chart_details: Optional[SolarReturnChartDetails] = None
    sr_subject_for_calculations: Optional[AstrologicalSubject] = None # Subject for the SR moment
    highlights: List[str] = []

    try:
        # 1. Create Natal Subject (base for Solar Return)
        # Use all fields from SolarReturnRequest which now mirrors NatalChartRequest for these
        natal_data_for_sr_base = NatalChartRequest(
            name=natal_name or "NatalBaseSR",
            year=birth_year, month=birth_month, day=birth_day,
            hour=birth_hour, minute=birth_minute,
            latitude=lat, longitude=lng, tz_str=tz_str,
            house_system=natal_house_system, # Pass the original request's house system
            zodiac_type=natal_zodiac_type,
            sidereal_mode=natal_sidereal_mode,
            perspective_type=natal_perspective_type
        )
        natal_subject, _ = create_subject(natal_data_for_sr_base, natal_data_for_sr_base.name)

        # 2. Attempt to use Kerykeion v4 SolarReturn
        if SolarReturn:
            try:
                # Kerykeion v4 constructor: SolarReturn(kerykeion_subject, year_integer_for_the_return)
                # The SolarReturn object itself is the astrological subject for the return moment.
                sr_event_subject = SolarReturn(natal_subject, target_sr_year)

                # The sr_event_subject's date/time attributes are updated to the precise SR time.
                # Kerykeion subjects have year, month, day, hour, minute attributes.
                # We need to construct a datetime object from these.
                # The timezone of the SR event subject will be the same as the natal subject's tz.
                # For precise_sr_datetime, we should aim for a timezone-aware UTC datetime.

                # Create datetime from subject's attributes
                # Assuming sr_event_subject.tz_str holds the timezone string (e.g., "America/New_York")
                # If sr_event_subject.tz_str is not available, this might need adjustment or default to UTC
                # For Kerykeion v4, the subject itself usually has tz_str attribute from its creation.
                # The time (hour, minute) on the sr_event_subject should be in the local time of that tz_str.

                event_tz_str = getattr(sr_event_subject, 'tz_str', 'UTC') # Default to UTC if not found
                local_sr_dt = datetime(
                    sr_event_subject.year, sr_event_subject.month, sr_event_subject.day,
                    sr_event_subject.hour, sr_event_subject.minute
                )

                # If tz_str is something like 'UTC+3' or 'UTC-5', simple parsing is needed.
                # If it's a full timezone name like 'America/New_York', use pytz.
                try:
                    event_timezone = pytz.timezone(event_tz_str)
                    aware_local_sr_dt = event_timezone.localize(local_sr_dt)
                    precise_sr_datetime = aware_local_sr_dt.astimezone(pytz.utc)
                except pytz.UnknownTimeZoneError:
                    # Handle cases like "UTC+3", "GMT-5" etc. if Kerykeion uses them.
                    # This is a simplified handling; a robust solution would parse offset.
                    if "utc" in event_tz_str.lower() or "gmt" in event_tz_str.lower():
                         # Assuming format like UTC+03:00 or GMT-05:00 or simple UTC
                        # For simplicity, if it contains UTC/GMT, assume it's close enough or needs parsing logic
                        # For now, if direct pytz fails, treat as naive and let it be potentially UTC later
                        print(f"Warning: Could not parse timezone '{event_tz_str}' with pytz. Assuming naive or simple UTC offset.")
                        # Fallback: treat as naive, or if it's like "UTC", it's already UTC.
                        if event_tz_str.upper() == "UTC":
                            precise_sr_datetime = datetime(sr_event_subject.year, sr_event_subject.month, sr_event_subject.day,
                                                           sr_event_subject.hour, sr_event_subject.minute, tzinfo=pytz.utc)
                        else: # Could be an offset like "+03:00", needs parsing not done here. For now, naive.
                             precise_sr_datetime = local_sr_dt # This will be naive
                    else: # Unknown format
                        print(f"Error: Unknown timezone format '{event_tz_str}'. Defaulting to naive datetime.")
                        precise_sr_datetime = local_sr_dt # This will be naive

                sr_subject_for_calculations = sr_event_subject
                # Update name for clarity
                sr_subject_for_calculations.name = f"Retorno Solar {target_sr_year}"
                print(f"K4 SolarReturn success. Date (from subject): {precise_sr_datetime}")

            except Exception as e_k4_sr:
                print(f"K4 SolarReturn error: {e_k4_sr}. Fallback.")
                precise_sr_datetime = None # Ensure it's None for fallback
                sr_subject_for_calculations = None # Ensure it's None for fallback
        else:
            print("K4 SolarReturn not imported (SolarReturn is None). Fallback.")
            precise_sr_datetime = None
            sr_subject_for_calculations = None

        # 3. Fallback if K4 SolarReturn failed or precise date could not be determined
        if not sr_subject_for_calculations or not precise_sr_datetime:
            print(f"Using Fallback for SR. Current precise_sr_datetime: {precise_sr_datetime}")
            # Use natal birth time for the target SR year as an approximation for the SR event.
            # The SR chart is cast for the natal location.
            # Fallback datetime should be made timezone-aware (UTC for consistency)
            # natal_data_for_sr_base.tz_str is the birth timezone
            try:
                birth_local_dt = datetime(target_sr_year, birth_month, birth_day, birth_hour, birth_minute)
                birth_timezone = pytz.timezone(tz_str) # tz_str is natal tz_str
                aware_birth_local_dt = birth_timezone.localize(birth_local_dt)
                precise_sr_datetime = aware_birth_local_dt.astimezone(pytz.utc)
                print(f"Fallback SR datetime (UTC): {precise_sr_datetime}")
            except Exception as e_tz:
                print(f"Error creating fallback datetime with timezone: {e_tz}. Using naive UTC.")
                precise_sr_datetime = datetime(target_sr_year, birth_month, birth_day, birth_hour, birth_minute, tzinfo=pytz.utc)


            sr_moment_data_fallback = NatalChartRequest(
                name=f"Retorno Solar {target_sr_year} (Aprox.)",
                # Use the components of the (now UTC) precise_sr_datetime for the subject creation
                year=precise_sr_datetime.year, month=precise_sr_datetime.month, day=precise_sr_datetime.day,
                hour=precise_sr_datetime.hour, minute=precise_sr_datetime.minute,
                # SR chart is cast for natal location (lat, lng) but with UTC time for the subject
                latitude=lat, longitude=lng, tz_str="UTC", # Explicitly UTC for this subject
                house_system=natal_house_system,
                # These tropic/sidereal etc. should ideally come from the natal chart's settings
                zodiac_type=natal_zodiac_type,
                sidereal_mode=natal_sidereal_mode,
                perspective_type=natal_perspective_type
            )
            # create_subject expects tz_str to be a valid timezone name for Kerykeion.
            # If we pass "UTC" and Kerykeion processes it, the internal time should be correct.
            sr_subject_for_calculations, _ = create_subject(sr_moment_data_fallback, sr_moment_data_fallback.name)
            if sr_subject_for_calculations:
                 sr_subject_for_calculations.name = f"Retorno Solar {target_sr_year} (Aprox.)" # Ensure name is set

        # 4. Populate SolarReturnChartDetails if sr_subject_for_calculations exists
        if sr_subject_for_calculations and precise_sr_datetime: # Ensure precise_sr_datetime is also available
            planets_sr_dict: Dict[str, PlanetData] = {}
            for k_name, api_name in PLANETS_MAP.items():
                planet_pos_data = get_planet_data(sr_subject_for_calculations, k_name, api_name)
                if planet_pos_data:
                    planets_sr_dict[api_name] = PlanetData(**planet_pos_data.model_dump()) # Convert PlanetPosition to PlanetData

            houses_sr_dict: Dict[str, HouseCuspData] = {}
            for i in range(1, 13):
                house_name_key = HOUSE_NUMBER_TO_NAME_BASE.get(i)
                if house_name_key:
                    cusp_obj = getattr(sr_subject_for_calculations, f"{house_name_key}_house")
                    houses_sr_dict[str(i)] = HouseCuspData(
                        house=i, sign=cusp_obj.sign, position=round(cusp_obj.position, 4),
                        quality=cusp_obj.quality, element=cusp_obj.element, emoji=cusp_obj.sign_emoji
                    )

            aspects_sr_list: List[AspectData] = []
            # Simplified aspects for SR chart (planet to planet in SR)
            for p1_k_name in sr_subject_for_calculations.planets_list:
                p1_obj = getattr(sr_subject_for_calculations, p1_k_name.lower())
                if hasattr(p1_obj, 'aspects'):
                    for asp in p1_obj.aspects:
                        aspects_sr_list.append(AspectData(
                            planet1=p1_obj.name, planet2=asp.p2_name, aspect=asp.aspect_name, orb=round(asp.orbit,2)
                        ))


            sr_chart_details = SolarReturnChartDetails(
                name=sr_subject_for_calculations.name,
                planets=planets_sr_dict,
                houses=houses_sr_dict,
                ascendant=houses_sr_dict.get("1"),
                midheaven=houses_sr_dict.get("10"),
                aspects=aspects_sr_list, # Placeholder, real aspects needed
                house_system=str(sr_subject_for_calculations.houses_system_name), # Get actual house system name
                zodiac_type=str(sr_subject_for_calculations.zodiac_type)
            )

            # 5. Generate Highlights
            highlights.append(f"Lua em {sr_subject_for_calculations.moon.sign} - foco nas emoções e intuição.")
            highlights.append(f"Ascendente do Retorno Solar em {sr_subject_for_calculations.first_house.sign} - nova perspectiva para o ano.")
            if hasattr(sr_subject_for_calculations, 'sun'):
                 sun_in_sr_house = get_house_from_kerykeion_attribute(sr_subject_for_calculations.sun)
                 highlights.append(f"Sol na Casa {sun_in_sr_house} do Retorno Solar - principal área de foco e expressão.")
        else:
            highlights.append("Não foi possível gerar detalhes completos do mapa de Retorno Solar.")

        highlights.append("Ano de renovação e novos ciclos pessoais.")
        return precise_sr_datetime, sr_chart_details, highlights

    except Exception as e:
        print(f"General error in calculate_solar_return: {type(e).__name__} - {e}")
        return datetime(target_sr_year, birth_month, birth_day), None, ["Erro no cálculo do Retorno Solar."]


@router.post("/moon_phase", response_model=MoonPhaseResponse)
async def get_moon_phase(request: MoonPhaseRequest):
    """
    Informa a fase da Lua para uma data específica.
    Ótimo para push "Lua Cheia hoje!".
    """
    try:
        phase, illumination = calculate_moon_phase(request.year, request.month, request.day)

        return MoonPhaseResponse(
            phase=phase,
            illumination=illumination
        )

    except Exception as e:
        print(f"Erro no endpoint de fase da lua: {e}")
        raise HTTPException(status_code=400, detail=f"Erro no cálculo da fase da lua: {str(e)}")

@router.post("/solar_return", response_model=SolarReturnResponse)
async def get_solar_return(request: SolarReturnRequest):
    """
    Calcula o próximo retorno solar e fornece destaques astrológicos.
    Retorna a data exata do aniversário solar e principais influências.
    """
    try:
        # Pass all necessary fields from SolarReturnRequest (which now includes natal fields)
        precise_datetime, chart_details, highlights = calculate_solar_return(
            birth_year=request.year,
            birth_month=request.month,
            birth_day=request.day,
            birth_hour=request.hour,
            birth_minute=request.minute,
            lat=request.latitude,
            lng=request.longitude,
            tz_str=request.tz_str,
            target_sr_year=request.return_year,
            natal_name=request.name, # Pass new fields from SolarReturnRequestModel
            natal_house_system=request.house_system,
            natal_zodiac_type=request.zodiac_type,
            natal_sidereal_mode=request.sidereal_mode,
            natal_perspective_type=request.perspective_type
        )

        return SolarReturnResponse(
            precise_solar_return_datetime_utc=precise_datetime.strftime("%Y-%m-%dT%H:%M:%SZ") if precise_datetime else None,
            solar_return_chart_details=chart_details,
            highlights=highlights
        )

    except Exception as e:
        print(f"Erro no endpoint de retorno solar: {e}")
        raise HTTPException(status_code=400, detail=f"Erro no cálculo do retorno solar: {str(e)}")


# --- Lunar Return ---

async def calculate_lunar_return_data(
    natal_request_data: NatalChartRequest, # Changed from natal_request to avoid conflict with FastAPI request
    search_start_date_str: str
) -> Tuple[Optional[datetime], Optional[LunarReturnChartDetails], Optional[List[str]]]:

    # Ensure create_subject receives all necessary fields from natal_request_data
    # natal_request_data should be an instance of NatalChartRequest from app.models
    natal_subject, _ = create_subject(natal_request_data, natal_request_data.name or "NatalBaseLR")

    try:
        # Kerykeion v4 LunarReturn likely expects a datetime object for search start.
        # Convert search_start_date_str to a datetime object, e.g., noon UTC on that day.
        parsed_date = datetime.strptime(search_start_date_str, "%Y-%m-%d")
        search_start_dt = datetime(parsed_date.year, parsed_date.month, parsed_date.day, 12, 0, 0, tzinfo=pytz.utc)
    except ValueError as ve:
        raise ValueError(f"Invalid search_start_date format: {search_start_date_str}. Expected YYYY-MM-DD. Error: {ve}")

    precise_lr_dt_obj: Optional[datetime] = None
    lr_chart_details: Optional[LunarReturnChartDetails] = None
    highlights: List[str] = []
    lr_subject_instance: Optional[AstrologicalSubject] = None

    if KERYKEION_LUNAR_RETURN_AVAILABLE and LunarReturn:
        try:
            print(f"Attempting K4 LunarReturn with natal subject: {natal_subject.name} and search_start_dt: {search_start_dt}")
            # Kerykeion v4 constructor: LunarReturn(kerykeion_subject, search_start_datetime_object)
            # The LunarReturn object itself is the astrological subject for the return moment.
            lr_event_subject = LunarReturn(natal_subject, search_start_dt)

            # Extract precise datetime from lr_event_subject's attributes (year, month, day, hour, minute)
            # and convert to aware UTC datetime. The subject's tz_str should be from the natal location.
            event_tz_str = getattr(lr_event_subject, 'tz_str', 'UTC') # Default to UTC
            local_lr_dt = datetime(
                lr_event_subject.year, lr_event_subject.month, lr_event_subject.day,
                lr_event_subject.hour, lr_event_subject.minute
            )

            try:
                event_timezone = pytz.timezone(event_tz_str)
                aware_local_lr_dt = event_timezone.localize(local_lr_dt)
                precise_lr_dt_obj = aware_local_lr_dt.astimezone(pytz.utc)
            except pytz.UnknownTimeZoneError:
                if "utc" in event_tz_str.lower() or "gmt" in event_tz_str.lower():
                    if event_tz_str.upper() == "UTC":
                        precise_lr_dt_obj = datetime(lr_event_subject.year, lr_event_subject.month, lr_event_subject.day,
                                                       lr_event_subject.hour, lr_event_subject.minute, tzinfo=pytz.utc)
                    else: # Offset like "+03:00", needs robust parsing. For now, treat as naive then UTC.
                        print(f"Warning: Timezone '{event_tz_str}' requires offset parsing. Treating as naive then UTC.")
                        precise_lr_dt_obj = local_lr_dt.replace(tzinfo=pytz.utc) # Simplified
                else:
                    print(f"Error: Unknown timezone format '{event_tz_str}'. Defaulting to naive datetime then UTC.")
                    precise_lr_dt_obj = local_lr_dt.replace(tzinfo=pytz.utc) # Simplified

            lr_subject_instance = lr_event_subject
            lr_subject_instance.name = f"Retorno Lunar {precise_lr_dt_obj.year}-{precise_lr_dt_obj.month}"
            highlights.append(f"Retorno Lunar calculado com Kerykeion v4 para {precise_lr_dt_obj.strftime('%Y-%m-%d %H:%M:%S %Z')}.")
            print(f"K4 LunarReturn success. Date (UTC): {precise_lr_dt_obj}")

        except Exception as e_k4_lr:
            print(f"K4 LunarReturn error: {type(e_k4_lr).__name__} - {e_k4_lr}. Fallback.")
            # Ensure these are None so fallback is triggered
            precise_lr_dt_obj = None
            lr_subject_instance = None
            highlights.append(f"Não foi possível calcular o Retorno Lunar preciso com Kerykeion v4: {e_k4_lr}. Usando estimativa.")
    else:
        highlights.append("Módulo Kerykeion LunarReturn não disponível ou não importado. Usando estimativa.")
        # Ensure these are None so fallback is triggered
        precise_lr_dt_obj = None
        lr_subject_instance = None

    # Fallback logic if K4 LunarReturn failed or not available
    if not lr_subject_instance or not precise_lr_dt_obj:
        print("Executing fallback logic for Lunar Return.")
        # Approximate LR date: search_start_date + ~28 days, using natal time, at natal location.
        # Convert to UTC.
        approx_lr_local_dt = datetime(
            search_start_dt.year, search_start_dt.month, search_start_dt.day, # Use search_start_dt as base
            natal_request_data.hour, natal_request_data.minute
        ) + timedelta(days=28) # Average lunar month approximation

        try:
            natal_timezone = pytz.timezone(natal_request_data.tz_str)
            aware_approx_lr_local_dt = natal_timezone.localize(approx_lr_local_dt)
            precise_lr_dt_obj = aware_approx_lr_local_dt.astimezone(pytz.utc)
        except Exception as e_tz:
            print(f"Error creating fallback LR datetime with natal timezone: {e_tz}. Using naive UTC from approximation.")
            precise_lr_dt_obj = approx_lr_local_dt.replace(tzinfo=pytz.utc) # Make it timezone aware (UTC)

        highlights.append(f"Data do Retorno Lunar é uma estimativa: {precise_lr_dt_obj.strftime('%Y-%m-%d %H:%M:%S %Z')}.")

        lr_chart_request_fallback = NatalChartRequest(
            name=f"Retorno Lunar {precise_lr_dt_obj.year}-{precise_lr_dt_obj.month} (Aprox.)",
            year=precise_lr_dt_obj.year, month=precise_lr_dt_obj.month, day=precise_lr_dt_obj.day,
            hour=precise_lr_dt_obj.hour, minute=precise_lr_dt_obj.minute,
            latitude=natal_request_data.latitude, longitude=natal_request_data.longitude,
            tz_str="UTC", # Subject created with UTC time
            house_system=natal_request_data.house_system,
            zodiac_type=natal_request_data.zodiac_type,
            sidereal_mode=natal_request_data.sidereal_mode,
            perspective_type=natal_request_data.perspective_type
        )
        lr_subject_instance, _ = create_subject(lr_chart_request_fallback, lr_chart_request_fallback.name)
        if lr_subject_instance:
            lr_subject_instance.name = f"Retorno Lunar {precise_lr_dt_obj.year}-{precise_lr_dt_obj.month} (Aprox.)"


    if lr_subject_instance and precise_lr_dt_obj: # Proceed only if we have a subject and a datetime
        planets_lr_dict: Dict[str, PlanetData] = {}
        for k_name, api_name in PLANETS_MAP.items():
            planet_pos_data = get_planet_data(lr_subject_instance, k_name, api_name)
            if planet_pos_data:
                planets_lr_dict[api_name] = PlanetData(**planet_pos_data.model_dump())

        houses_lr_dict: Dict[str, HouseCuspData] = {}
        for i in range(1, 13):
            house_name_key = HOUSE_NUMBER_TO_NAME_BASE.get(i)
            if house_name_key:
                cusp_obj = getattr(lr_subject_instance, f"{house_name_key}_house")
                houses_lr_dict[str(i)] = HouseCuspData(
                    house=i, sign=cusp_obj.sign, position=round(cusp_obj.position, 4),
                    quality=cusp_obj.quality, element=cusp_obj.element, emoji=cusp_obj.sign_emoji
                )

        aspects_lr_list: List[AspectData] = []
        for p1_k_name in lr_subject_instance.planets_list:
            p1_obj = getattr(lr_subject_instance, p1_k_name.lower())
            if hasattr(p1_obj, 'aspects'):
                for asp in p1_obj.aspects: # These are aspects to other planets in the same chart
                    aspects_lr_list.append(AspectData(
                        planet1=p1_obj.name, planet2=asp.p2_name, aspect=asp.aspect_name, orb=round(asp.orbit,2)
                    ))

        lr_chart_details = LunarReturnChartDetails(
            name=lr_subject_instance.name,
            planets=planets_lr_dict,
            houses=houses_lr_dict,
            ascendant=houses_lr_dict.get("1"), # type: ignore
            midheaven=houses_lr_dict.get("10"), # type: ignore
            aspects=aspects_lr_list,
            house_system=str(lr_subject_instance.houses_system_name),
            zodiac_type=str(lr_subject_instance.zodiac_type)
        )
        highlights.append(f"Retorno Lunar (simulado) para {precise_lr_dt_obj.strftime('%Y-%m-%d %H:%M:%S')} UTC.")
        if lr_subject_instance.ascendant: highlights.append(f"Ascendente do Retorno Lunar: {lr_subject_instance.ascendant.sign}")
        if lr_subject_instance.moon: highlights.append(f"Lua do Retorno Lunar em: {lr_subject_instance.moon.sign} na casa {lr_subject_instance.moon.house_name}")

    except NotImplementedError:
            highlights.append("Cálculo preciso do Retorno Lunar com Kerykeion v5 ainda não implementado.")
        except Exception as e_k5_lr: # Corrected indentation for except block
            print(f"Erro ao calcular Retorno Lunar com Kerykeion v5 (ou mock): {str(e_k5_lr)}")
            highlights.append(f"Não foi possível calcular o Retorno Lunar preciso: {str(e_k5_lr)}")
    else: # Corresponds to 'if KERYKEION_LUNAR_RETURN_AVAILABLE and LunarReturn:'
        highlights.append("Funcionalidade de Retorno Lunar não disponível (Kerykeion v5 módulo não encontrado).")

    if not precise_lr_dt_obj: # Fallback if everything failed
        mock_date = datetime.strptime(search_start_date_str, "%Y-%m-%d") + timedelta(days=28)
        precise_lr_dt_obj = datetime(mock_date.year, mock_date.month, mock_date.day, 12, 0, 0, tzinfo=pytz.utc) # Fallback time
        highlights.append("Data do Retorno Lunar é uma estimativa aproximada.")

    return precise_lr_dt_obj, lr_chart_details, highlights

@router.post("/lunar_return", response_model=LunarReturnResponse, summary="Calcula o próximo Retorno Lunar e dados do mapa.")
async def get_lunar_return(request: LunarReturnRequest):
    try:
        precise_dt, chart_details, highlights = await calculate_lunar_return_data(
            request.natal_data,
            request.search_start_date
        )

        dt_str = precise_dt.strftime("%Y-%m-%dT%H:%M:%SZ") if precise_dt else None

        return LunarReturnResponse(
            request_data=request,
            precise_lunar_return_datetime_utc=dt_str,
            lunar_return_chart_details=chart_details,
            highlights=highlights
        )
    except ValueError as ve: # For date parsing errors from calculate_lunar_return_data
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Erro no endpoint de retorno lunar: {type(e).__name__} - {str(e)}")
        # import traceback
        # traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno no cálculo do Retorno Lunar: {str(e)}")
