from fastapi import APIRouter, HTTPException, Depends
from kerykeion import AstrologicalSubject
try:
    from kerykeion.report import TransitsTimeRangeFactory # Attempt import from kerykeion.report for K4
except ImportError:
    try:
        from kerykeion.factory import TransitsTimeRangeFactory # Fallback to kerykeion.factory
    except ImportError:
        TransitsTimeRangeFactory = None # Placeholder if import fails
from app.models import (
    TransitRequest, NatalChartRequest,
    TransitRangeRequest, TransitRangeResponse, TransitEventData
)
from app.security import verify_api_key
from app.utils.astro_helpers import create_subject
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import math

router = APIRouter(
    prefix="/api/v1",
    tags=["Daily & Weekly Transits"],
    dependencies=[Depends(verify_api_key)]
)

# Modelos específicos para trânsitos diários e semanais
class DailyTransitRequest(BaseModel):
    year: int = Field(..., description="Ano")
    month: int = Field(..., description="Mês (1-12)")
    day: int = Field(..., description="Dia")

class TransitAspectDaily(BaseModel):
    p1: str = Field(..., description="Primeiro planeta")
    p2: str = Field(..., description="Segundo planeta")
    type: str = Field(..., description="Tipo do aspecto (sextile, square, etc)")
    orb: float = Field(..., description="Orbe do aspecto")

class DailyTransitsResponse(BaseModel):
    aspects: List[TransitAspectDaily]

class WeeklyDay(BaseModel):
    date: str
    aspects: List[TransitAspectDaily]
    summary: str

class WeeklyTransitsResponse(BaseModel):
    days: List[WeeklyDay]

def calculate_aspect_angle(pos1: float, pos2: float) -> float:
    """Calcula o ângulo entre duas posições planetárias."""
    diff = abs(pos1 - pos2)
    if diff > 180:
        diff = 360 - diff
    return diff

def get_aspect_name_simple(angle: float, orb_tolerance: float = 8.0) -> tuple:
    """Determina o nome do aspecto baseado no ângulo."""
    aspects = {
        0: "conjunction",
        30: "semi_sextile",
        45: "semi_square",
        60: "sextile",
        90: "square",
        120: "trine",
        135: "sesquiquadrate",
        150: "quincunx",
        180: "opposition"
    }

    for aspect_angle, name in aspects.items():
        if abs(angle - aspect_angle) <= orb_tolerance:
            return name, abs(angle - aspect_angle)

    return None, None

def calculate_daily_aspects(year: int, month: int, day: int) -> List[TransitAspectDaily]:
    """Calcula aspectos planetários para um dia específico."""
    try:
        # Criar subject para o dia específico (meio-dia GMT)
        subject = AstrologicalSubject(
            name=f"Transits_{year}_{month}_{day}",
            year=year, month=month, day=day,
            hour=12, minute=0,
            lat=0.0, lng=0.0,  # GMT
            tz_str="UTC"
        )

        # Planetas principais para análise
        main_planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']

        # Obter posições dos planetas
        planet_positions = {}
        for planet in main_planets:
            if hasattr(subject, planet):
                p_obj = getattr(subject, planet)
                if p_obj and hasattr(p_obj, 'position'):
                    planet_positions[planet] = {
                        'name': p_obj.name,
                        'position': p_obj.position
                    }

        # Calcular aspectos entre planetas
        aspects = []
        planet_keys = list(planet_positions.keys())

        for i, p1_key in enumerate(planet_keys):
            for p2_key in planet_keys[i+1:]:
                p1_data = planet_positions[p1_key]
                p2_data = planet_positions[p2_key]

                angle = calculate_aspect_angle(p1_data['position'], p2_data['position'])
                aspect_name, orb = get_aspect_name_simple(angle)

                if aspect_name and orb is not None and orb <= 5.0:  # Orbe mais apertado para trânsitos diários
                    aspects.append(TransitAspectDaily(
                        p1=p1_data['name'],
                        p2=p2_data['name'],
                        type=aspect_name,
                        orb=round(orb, 2)
                    ))

        return aspects

    except Exception as e:
        print(f"Erro no cálculo de aspectos diários: {e}")
        return []

@router.post("/transits/daily", response_model=DailyTransitsResponse)
async def get_daily_transits(request: DailyTransitRequest):
    """
    Retorna todos os aspectos planetários ativos para um dia específico.
    Lista trânsitos do dia (GMT-0).
    """
    try:
        aspects = calculate_daily_aspects(request.year, request.month, request.day)

        return DailyTransitsResponse(aspects=aspects)

    except Exception as e:
        print(f"Erro no endpoint de trânsitos diários: {e}")
        raise HTTPException(status_code=400, detail=f"Erro no cálculo de trânsitos diários: {str(e)}")

@router.post("/transits/weekly", response_model=WeeklyTransitsResponse)
async def get_weekly_transits(request: DailyTransitRequest):
    """
    Entrega predição de 7 dias resumida (bom para alertas semanais).
    Calcula aspectos para os próximos 7 dias a partir da data fornecida.
    """
    try:
        weekly_data = []
        base_date = datetime(request.year, request.month, request.day)

        for i in range(7):
            current_date = base_date + timedelta(days=i)
            aspects = calculate_daily_aspects(current_date.year, current_date.month, current_date.day)

            # Gerar resumo do dia
            if not aspects:
                summary = "Dia tranquilo, sem aspectos planetários significativos."
            else:
                harmonic_count = len([a for a in aspects if a.type in ["sextile", "trine", "conjunction"]])
                tense_count = len([a for a in aspects if a.type in ["square", "opposition", "semi_square", "sesquiquadrate"]])

                if harmonic_count > tense_count:
                    summary = f"Dia harmonioso com {len(aspects)} aspectos, predominando energias positivas."
                elif tense_count > harmonic_count:
                    summary = f"Dia desafiador com {len(aspects)} aspectos, requer atenção e paciência."
                else:
                    summary = f"Dia equilibrado com {len(aspects)} aspectos mistos."

            weekly_data.append(WeeklyDay(
                date=current_date.strftime("%Y-%m-%d"),
                aspects=aspects,
                summary=summary
            ))

        return WeeklyTransitsResponse(days=weekly_data)

    except Exception as e:
        print(f"Erro no endpoint de trânsitos semanais: {e}")
        raise HTTPException(status_code=400, detail=f"Erro no cálculo de trânsitos semanais: {str(e)}")


@router.post("/transits/range", response_model=TransitRangeResponse, summary="Calcula eventos de trânsito detalhados para um período")
async def get_transit_range_events(request: TransitRangeRequest):
    try:
        # 1. Create natal subject
        # create_subject already handles new zodiac/perspective parameters from NatalChartRequest
        natal_subject_obj, _ = create_subject(request.natal_data, request.natal_data.name or "NatalBase")

        processed_events: List[TransitEventData] = []
        summary_details: Dict[str, Any] = {}

        if request.step == "exact":
            if not TransitsTimeRangeFactory:
                raise ImportError("TransitsTimeRangeFactory não pôde ser importado. Verifique a instalação e versão do Kerykeion.")

            start_date_dt = datetime.strptime(request.start_date, "%Y-%m-%d")
            end_date_dt = datetime.strptime(request.end_date, "%Y-%m-%d")

            # K4 constructor: TransitsTimeRangeFactory(natal_subject, start_date_dt, end_date_dt, list_of_transiting_planets)
            # Ensure request.transiting_planets is a list of strings. Kerykeion default might be all major planets.
            # If request.transiting_planets is None or empty, consider passing Kerykeion's default list or all planets.
            # For now, assume it's provided or Kerykeion handles None.
            transit_planets_for_factory = request.transiting_planets or [
                "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
            ]

            transit_event_generator = TransitsTimeRangeFactory(
                first_subject=natal_subject_obj,
                start_date=start_date_dt,
                end_date=end_date_dt,
                transiting_planets_list=transit_planets_for_factory # K4 specific parameter
            )

            # Method to get events and its parameters need to align with K4
            # Assuming get_transits_event_list is still the method, and it takes these filters.
            kerykeion_events = transit_event_generator.get_transits_event_list(
                target_chart_points_list=request.natal_points,
                aspects_list=request.aspect_types
            )

            if kerykeion_events:
                for event in kerykeion_events:
                    # Adapt K4 event structure to TransitEventData
                    # K4 event might have: event_time, transiting_planet_name, target_planet_name, aspect_name, orb, is_applying_str
                    event_time_str = getattr(event, 'time', None) or getattr(event, 'event_time', None)
                    if isinstance(event_time_str, datetime): # If it's a full datetime, format it
                        event_time_str = event_time_str.strftime("%H:%M:%S")

                    event_date_obj = getattr(event, 'date', None)
                    event_date_str = event_date_obj.strftime("%Y-%m-%d") if isinstance(event_date_obj, datetime) else str(event_date_obj)

                    is_applying_val = False
                    if hasattr(event, 'is_applying'):
                        is_applying_val = bool(event.is_applying)
                    elif hasattr(event, 'is_applying_str'): # Some K4 versions might use string state
                        is_applying_val = (str(getattr(event, 'is_applying_str', '')).lower() == 'applying')

                    processed_events.append(
                        TransitEventData(
                            date=event_date_str,
                            time=event_time_str,
                            transiting_planet=str(getattr(event, 'transiting_planet', None) or getattr(event, 'transiting_planet_name', 'Unknown')),
                            aspect_type=str(getattr(event, 'aspect_type', None) or getattr(event, 'aspect_name', 'Unknown')),
                            natal_planet_or_point=str(getattr(event, 'target_planet', None) or getattr(event, 'target_planet_name', 'Unknown')),
                            orb=float(getattr(event, 'orb', 0.0)),
                            is_applying=is_applying_val
                        )
                    )
            summary_details = {
                "calculation_mode": "exact",
                "total_events": len(processed_events),
                "date_range": f"{request.start_date} to {request.end_date}",
                "filters_applied": {
                    "transiting_planets": request.transiting_planets,
                    "natal_points": request.natal_points,
                    "aspect_types": request.aspect_types
                }
            }
        else: # Daily, Weekly, Monthly snapshots (existing logic should be fine)
            start_date_loop = datetime.strptime(request.start_date, "%Y-%m-%d").date()
            end_date_loop = datetime.strptime(request.end_date, "%Y-%m-%d").date()
            current_date_loop = start_date_loop

            delta: Optional[timedelta] = None
            if request.step == "day": # Changed from effective_step
                delta = timedelta(days=1)
            elif request.step == "week": # Changed from effective_step
                delta = timedelta(weeks=1)
            elif request.step == "month": # Changed from effective_step
                delta = timedelta(days=30)

            if not delta:
                raise ValueError(f"Invalid step value '{request.step}' for periodic transit calculation.")

            while current_date_loop <= end_date_loop:
                transit_req_for_step = TransitRequest(
                    year=current_date_loop.year, month=current_date_loop.month, day=current_date_loop.day,
                    hour=12, minute=0,
                    latitude=request.natal_data.latitude, longitude=request.natal_data.longitude,
                    tz_str=request.natal_data.tz_str,
                    zodiac_type=request.natal_data.zodiac_type,
                    sidereal_mode=request.natal_data.sidereal_mode,
                    perspective_type=request.natal_data.perspective_type
                )
                transit_moment_subject, _ = create_subject(transit_req_for_step, f"TransitAt{current_date_loop.isoformat()}")

                aspects_at_step = transit_moment_subject.aspects_to_subject(
                     target_subject=natal_subject_obj,
                     aspects_list=request.aspect_types,
                     planets_list1=request.transiting_planets,
                     planets_list2=request.natal_points
                )

                if aspects_at_step:
                    for aspect in aspects_at_step:
                        processed_events.append(
                            TransitEventData(
                                date=current_date_loop.strftime("%Y-%m-%d"),
                                time="12:00:00",
                                transiting_planet=str(aspect.p1_name),
                                aspect_type=str(aspect.aspect_name),
                                natal_planet_or_point=str(aspect.p2_name),
                                orb=float(aspect.orb),
                                is_applying=(aspect.state == 'applying' if hasattr(aspect, 'state') else None)
                            )
                        )
                current_date_loop += delta

            summary_details = {
                "calculation_mode": request.step,
                "total_events": len(processed_events), # Corrected from total_snapshots_taken
                "date_range": f"{request.start_date} to {request.end_date}",
                 "filters_applied": {
                    "transiting_planets": request.transiting_planets,
                    "natal_points": request.natal_points,
                    "aspect_types": request.aspect_types
                }
            }

        return TransitRangeResponse(
            request_data=request,
            events=processed_events,
            summary=summary_details
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Erro de formatação de data ou dados inválidos: {str(ve)}")
    except ImportError as ie: # Specific catch for ImportError if factory is None
        print(f"ImportError in /transits/range: {str(ie)}")
        raise HTTPException(status_code=501, detail=str(ie))
    except Exception as e:
        # Log the full error for debugging
        print(f"Error in /transits/range: {type(e).__name__} - {str(e)}")
        # Consider logging traceback as well in a real scenario
        # import traceback
        # traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno ao calcular trânsitos em range: {type(e).__name__} - {str(e)}")
