from fastapi import APIRouter, HTTPException, Depends
from kerykeion import AstrologicalSubject
from app.models import SynastryRequest, SynastryResponse, SynastryAspect, NatalChartRequest # Added NatalChartRequest for create_subject
from app.security import verify_api_key
from app.utils.astro_helpers import create_subject, PLANETS_MAP # Added PLANETS_MAP
from typing import List, Dict, Optional, Any # Added Optional, Any
import math

# Speculative import for Kerykeion SynastryAspects
try:
    from kerykeion.aspects import SynastryAspects
    KERYKEION_SYNASTRY_ASPECTS_CLASS_AVAILABLE = True
except ImportError:
    try:
        from kerykeion import SynastryAspects # Older location
        KERYKEION_SYNASTRY_ASPECTS_CLASS_AVAILABLE = True
    except ImportError:
        KERYKEION_SYNASTRY_ASPECTS_CLASS_AVAILABLE = False
        SynastryAspects = None

router = APIRouter(
    prefix="/api/v1",
    tags=["Synastry"],
    dependencies=[Depends(verify_api_key)]
)

def calculate_aspect_angle(pos1: float, pos2: float) -> float:
    """Calcula o ângulo entre duas posições planetárias."""
    diff = abs(pos1 - pos2)
    if diff > 180:
        diff = 360 - diff
    return diff

def get_aspect_name(angle: float, orb_tolerance: float = 8.0) -> tuple:
    """Determina o nome do aspecto baseado no ângulo."""
    aspects = {
        0: ("conjunction", "harmonic"),
        30: ("semi_sextile", "neutral"),
        45: ("semi_square", "tense"),
        60: ("sextile", "harmonic"),
        90: ("square", "tense"),
        120: ("trine", "harmonic"),
        135: ("sesquiquadrate", "tense"),
        150: ("quincunx", "neutral"),
        180: ("opposition", "tense")
    }

    for aspect_angle, (name, type_) in aspects.items():
        if abs(angle - aspect_angle) <= orb_tolerance:
            return name, type_, abs(angle - aspect_angle)

    return None, None, None

def calculate_compatibility_score(aspects: List[SynastryAspect]) -> float:
    """Calcula um score de compatibilidade baseado nos aspectos."""
    if not aspects:
        return 0.0

    score = 0.0
    total_weight = 0.0

    # Pesos por tipo de aspecto
    _ASPECT_NAME_TO_TYPE = {
        "conjunction": "harmonic", # Can be neutral or vary; simplified here
        "opposition": "tense",
        "trine": "harmonic",
        "square": "tense",
        "sextile": "harmonic",
        "quincunx": "neutral", # Often seen as requiring adjustment
        "semi_sextile": "neutral",
        "semi_square": "tense",
        "sesquiquadrate": "tense", # Kerykeion might use sesquisquare
        "quintile": "harmonic", # Often seen as minor creative
        "biquintile": "harmonic" # Often seen as minor creative
        # Add other aspect names Kerykeion might return if necessary
    }
    aspect_type_weights = {
        "harmonic": 2.0,
        "neutral": 1.0,
        "tense": -1.0
    }

    # Pesos por planetas envolvidos
    planet_weights = {
        "Sun": 3.0, "Moon": 3.0, "Venus": 2.5, "Mars": 2.0,
        "Mercury": 1.5, "Jupiter": 2.0, "Saturn": 1.5,
        "Uranus": 1.0, "Neptune": 1.0, "Pluto": 1.0,
        # Default for other points if they appear in aspects
        "Default": 0.5
    }

    for aspect_detail in aspects: # aspect_detail is SynastryAspect Pydantic model
        # Derive aspect_type from aspect_detail.aspect (name)
        aspect_type = _ASPECT_NAME_TO_TYPE.get(aspect_detail.aspect.lower(), "neutral")

        aspect_weight = aspect_type_weights.get(aspect_type, 1.0)
        # Use aspect_detail.planet1 and aspect_detail.planet2 which are the planet names
        p1_weight = planet_weights.get(aspect_detail.planet1, planet_weights["Default"])
        p2_weight = planet_weights.get(aspect_detail.planet2, planet_weights["Default"])
        
        # Peso diminui com orbe maior
        orb_factor = max(0.1, 1.0 - (aspect_detail.orb / 10.0)) # Using aspect_detail.orb
        
        final_weight = aspect_weight * p1_weight * p2_weight * orb_factor
        score += final_weight
        total_weight += abs(final_weight)

    # Normalizar score para 0-100
    if total_weight > 0:
        normalized_score = ((score + total_weight) / (2 * total_weight)) * 100
        return round(max(0, min(100, normalized_score)), 1)
    
    return 50.0  # Score neutro se não houver aspectos

def generate_summary(aspects: List[SynastryAspect], score: float) -> str:
    """Gera um resumo textual da compatibilidade."""
    if not aspects:
        return "Não foram encontrados aspectos significativos entre os mapas."
    
    # Re-use the _ASPECT_NAME_TO_TYPE from calculate_compatibility_score
    _ASPECT_NAME_TO_TYPE = {
        "conjunction": "harmonic", "opposition": "tense", "trine": "harmonic",
        "square": "tense", "sextile": "harmonic", "quincunx": "neutral",
        "semi_sextile": "neutral", "semi_square": "tense", "sesquiquadrate": "tense",
        "quintile": "harmonic", "biquintile": "harmonic"
    }

    harmonic_count = 0
    tense_count = 0
    neutral_count = 0

    for aspect_detail in aspects:
        aspect_type = _ASPECT_NAME_TO_TYPE.get(aspect_detail.aspect.lower(), "neutral")
        if aspect_type == "harmonic":
            harmonic_count += 1
        elif aspect_type == "tense":
            tense_count += 1
        else:
            neutral_count += 1

    total_aspects = len(aspects)
    summary_parts = []
    
    if score >= 80: summary_parts.append("Esta é uma combinação altamente compatível.")
    elif score >= 65: summary_parts.append("Esta é uma combinação muito promissora.")
    elif score >= 50: summary_parts.append("Esta combinação tem potencial com algum trabalho.")
    elif score >= 35: summary_parts.append("Esta combinação apresenta desafios significativos.")
    else: summary_parts.append("Esta combinação requer muito trabalho e compreensão.")
    
    if harmonic_count > tense_count: summary_parts.append(f"Com {harmonic_count} de {total_aspects} aspectos sendo majoritariamente harmônicos, a energia geral é de apoio mútuo.")
    elif tense_count > harmonic_count: summary_parts.append(f"Com {tense_count} de {total_aspects} aspectos sendo majoritariamente tensos, há desafios que podem gerar crescimento.")
    else: summary_parts.append(f"Com um equilíbrio de {harmonic_count} aspectos harmônicos e {tense_count} tensos (de {total_aspects}), a relação tem dinâmicas variadas.")
    
    if neutral_count > 0: summary_parts.append(f"Os {neutral_count} aspectos neutros adicionam mais camadas à interação.")
    
    return " ".join(summary_parts)

@router.post("/synastry", response_model=SynastryResponse)
async def calculate_synastry(request: SynastryRequest):
    """
    Calcula a compatibilidade astrológica entre duas pessoas.
    Analisa aspectos entre planetas de ambos os mapas natais.
    """
    try:
        subject1, _ = create_subject(request.person1, request.person1.name or "Person1")
        subject2, _ = create_subject(request.person2, request.person2.name or "Person2")

        aspects: List[SynastryAspect] = []
        use_manual_calculation = True # Default to manual, override if K5 works

        if KERYKEION_SYNASTRY_ASPECTS_CLASS_AVAILABLE and SynastryAspects:
            print("Attempting to use Kerykeion SynastryAspects class...")
            try:
                synastry_calculator = SynastryAspects(subject1, subject2)
                kerykeion_aspect_list = []

                # Attempt to get aspects using common Kerykeion patterns
                if hasattr(synastry_calculator, 'get_relevant_aspects'):
                    kerykeion_aspect_list = synastry_calculator.get_relevant_aspects()
                elif hasattr(synastry_calculator, 'aspect_list'):
                     kerykeion_aspect_list = synastry_calculator.aspect_list()
                elif hasattr(synastry_calculator, 'aspects'):
                     kerykeion_aspect_list = synastry_calculator.aspects
                
                if kerykeion_aspect_list: # If any aspects were retrieved
                    for k_asp in kerykeion_aspect_list:
                        is_applying_status = False
                        if hasattr(k_asp, 'state') and k_asp.state == 'applying':
                            is_applying_status = True
                        elif hasattr(k_asp, 'is_applying') and isinstance(k_asp.is_applying, bool):
                            is_applying_status = k_asp.is_applying

                        aspects.append(SynastryAspect(
                            planet1=str(getattr(k_asp, 'p1_name', 'Unknown')),
                            person1=str(subject1.name), # Use the name from the subject
                            planet2=str(getattr(k_asp, 'p2_name', 'Unknown')),
                            person2=str(subject2.name), # Use the name from the subject
                            aspect=str(getattr(k_asp, 'aspect_name', 'Unknown')),
                            orb=round(float(getattr(k_asp, 'orbit', 0.0)), 2),
                            applying=is_applying_status
                        ))
                    print(f"Successfully processed {len(aspects)} aspects using Kerykeion SynastryAspects.")
                    use_manual_calculation = False # K5 method succeeded
                else:
                    print("Kerykeion SynastryAspects returned no aspects. Will try manual calculation.")

            except Exception as e_k5_synastry:
                print(f"Error using Kerykeion SynastryAspects: {type(e_k5_synastry).__name__} - {e_k5_synastry}. Falling back to manual calculation.")
        else:
            print("Kerykeion SynastryAspects class not available. Using manual calculation.")

        if use_manual_calculation:
            main_planets_k_names = list(PLANETS_MAP.keys())

            # Prepare planet data for manual calculation
            # Ensure planet names used for SynastryAspect match what calculate_compatibility_score expects (e.g., "Sun", "Moon")
            # The PLANETS_MAP maps kerykeion names ('sun') to display names ('Sun')

            s1_planets_data = {PLANETS_MAP.get(k, k.capitalize()): getattr(subject1, k).abs_pos
                               for k in main_planets_k_names if hasattr(subject1, k) and getattr(subject1, k)}
            s2_planets_data = {PLANETS_MAP.get(k, k.capitalize()): getattr(subject2, k).abs_pos
                               for k in main_planets_k_names if hasattr(subject2, k) and getattr(subject2, k)}

            for p1_name, p1_abs_pos in s1_planets_data.items():
                for p2_name, p2_abs_pos in s2_planets_data.items():
                    angle = calculate_aspect_angle(p1_abs_pos, p2_abs_pos)
                    aspect_name_calc, _, orb_calc = get_aspect_name(angle)

                    if aspect_name_calc and orb_calc is not None and orb_calc <= 6.0: # Synastry orb
                        aspects.append(SynastryAspect(
                            planet1=p1_name,
                            person1=str(subject1.name),
                            planet2=p2_name,
                            person2=str(subject2.name),
                            aspect=aspect_name_calc,
                            orb=round(orb_calc, 2),
                            applying=False
                        ))
            if aspects: print(f"Manual synastry calculation resulted in {len(aspects)} aspects.")

        aspects.sort(key=lambda x: x.orb)
        compatibility_score = calculate_compatibility_score(aspects)
        summary = generate_summary(aspects, compatibility_score)

        return SynastryResponse(
            person1_data=request.person1, # Return the input request data
            person2_data=request.person2,
            aspects=aspects,
            compatibility_score=compatibility_score,
            summary=summary
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Erro no cálculo de sinastria: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Erro no cálculo de sinastria: {str(e)}")