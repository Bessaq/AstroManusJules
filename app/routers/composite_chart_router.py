from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional, Any
from app.models import (
    CompositeChartRequest, CompositeChartResponse, CompositeChartDetails,
    NatalChartRequest, PlanetData, HouseCuspData, AspectData
)
from app.security import verify_api_key
from app.utils.astro_helpers import create_subject, get_planet_data, PLANETS_MAP, HOUSE_NUMBER_TO_NAME_BASE, get_house_from_kerykeion_attribute, HOUSE_SYSTEM_MAP
from kerykeion import AstrologicalSubject # Base class for subjects
try:
    from kerykeion.factory import CompositeSubjectFactory # K4 Guide: Use factory
except ImportError:
    CompositeSubjectFactory = None # Placeholder if import fails


router = APIRouter(
    prefix="/api/v1",
    tags=["Composite Chart"],
    dependencies=[Depends(verify_api_key)]
)

def get_aspects_from_subject(subject: AstrologicalSubject) -> List[AspectData]:
    aspects_list: List[AspectData] = []
    if hasattr(subject, 'aspects') and subject.aspects:
        for asp in subject.aspects:
            if all(hasattr(asp, attr) for attr in ['p1_name', 'p2_name', 'aspect_name', 'orbit']):
                is_applying = False
                if hasattr(asp, 'state') and asp.state == 'applying':
                    is_applying = True
                elif hasattr(asp, 'applying') and isinstance(asp.applying, bool):
                    is_applying = asp.applying

                aspects_list.append(AspectData(
                    planet1=str(asp.p1_name),
                    planet2=str(asp.p2_name),
                    aspect=str(asp.aspect_name),
                    orb=round(float(asp.orbit), 2),
                    applying=is_applying
                ))
    return aspects_list

@router.post("/composite_chart", response_model=CompositeChartResponse, summary="Calcula um Mapa Composto de pontos médios entre dois mapas natais.")
async def get_composite_chart(request: CompositeChartRequest):
    try:
        if not CompositeSubjectFactory:
            raise ImportError("CompositeSubjectFactory não pôde ser importado da Kerykeion. Verifique a instalação e versão.")

        # Create AstrologicalSubject instances for Person1 and Person2
        person1_subject, loc_info1 = create_subject(request.person1_natal_data, request.person1_natal_data.name or "Person1")
        person2_subject, loc_info2 = create_subject(request.person2_natal_data, request.person2_natal_data.name or "Person2")

        # Composite chart settings from request
        settings = request.composite_settings

        factory = CompositeSubjectFactory(person1_subject, person2_subject)

        composite_subject: Optional[AstrologicalSubject] = None
        if settings.method.lower() == 'davison':
            # Assuming the factory method might need location/house system for Davison if it calculates a full chart
            # However, Kerykeion factories often return a subject primarily with planet data,
            # and houses might be calculated separately or based on a default/provided location later.
            # The guide does not specify parameters for these factory methods.
            # For now, assume they don't take location/house system.
            # Location and house system from `settings.location` and `settings.house_system`
            # would need to be applied to the `composite_subject` after creation if it's a plain AstrologicalSubject
            # that needs these for house calculation by KerykeionChartSVG, or if the factory itself takes them.
            # This part might need further refinement based on actual K4 CompositeSubjectFactory behavior.
            composite_subject = factory.get_davison_composite_subject_model(
                lat=settings.location.latitude,
                lon=settings.location.longitude,
                tz_str=settings.location.tz_str
                # house_system_code = HOUSE_SYSTEM_MAP.get(settings.house_system.lower(), "P")
                # If the factory method supports house_system, it should be passed.
            )
            if composite_subject:
                 composite_subject.name = f"Composto Davison {request.person1_natal_data.name or 'P1'} & {request.person2_natal_data.name or 'P2'}"
        else: # Default to midpoint
            composite_subject = factory.get_midpoint_composite_subject_model(
                lat=settings.location.latitude,
                lon=settings.location.longitude,
                tz_str=settings.location.tz_str
                # house_system_code = HOUSE_SYSTEM_MAP.get(settings.house_system.lower(), "P")
            )
            if composite_subject:
                composite_subject.name = f"Composto Midpoint {request.person1_natal_data.name or 'P1'} & {request.person2_natal_data.name or 'P2'}"

        if not composite_subject:
            raise HTTPException(status_code=500, detail="Falha ao gerar o modelo de mapa composto pela Kerykeion (v4 factory).")

        # If house system needs to be explicitly set on the subject created by the factory:
        # (This depends on whether the factory methods return a subject that already has houses,
        # or if it's a more basic subject where houses are determined later, e.g., by KerykeionChartSVG)
        # Assuming the factory methods already account for house calculations if lat/lon/tz are passed.
        # If not, and if the returned subject is a standard AstrologicalSubject, one might set:
        # composite_subject.houses_system = HOUSE_SYSTEM_MAP.get(settings.house_system.lower(), "P")
        # composite_subject.lat = settings.location.latitude
        # composite_subject.lon = settings.location.longitude
        # composite_subject.tz_str = settings.location.tz_str
        # And then potentially a method on the subject to calculate houses if not done by factory.
        # For now, we assume the factory methods, if they take lat/lon/tz, handle house setup.

        # Populate CompositeChartDetails
        planets_dict: Dict[str, PlanetData] = {}
        for k_name_lower, api_name in PLANETS_MAP.items(): # k_name_lower e.g. "sun", "moon"
            if hasattr(composite_subject, k_name_lower):
                planet_k_obj = getattr(composite_subject, k_name_lower)
                if planet_k_obj and hasattr(planet_k_obj, 'name'):
                    planets_dict[api_name] = PlanetData(
                        name=api_name,
                        sign=planet_k_obj.sign,
                        sign_num=planet_k_obj.sign_num,
                        position=round(planet_k_obj.position, 4),
                        abs_pos=round(planet_k_obj.abs_pos, 4),
                        house_name=None, # Houses typically handled differently or not at all for midpoints
                        house_number=None,
                        speed=0.0, # Not applicable for composite points
                        retrograde=False, # Not applicable
                        quality=getattr(planet_k_obj, 'quality', None),
                        element=getattr(planet_k_obj, 'element', None),
                        emoji=getattr(planet_k_obj, 'sign_emoji', None)
                    )

        aspects_list = get_aspects_from_subject(composite_subject)

        houses_data: Optional[Dict[str, HouseCuspData]] = None
        asc_data: Optional[HouseCuspData] = None
        mc_data: Optional[HouseCuspData] = None

        # Check if composite_subject has house attributes (e.g., first_house, second_house)
        # Kerykeion's CompositeSubject might not calculate traditional houses or might do so differently.
        # This part is speculative and depends on Kerykeion v5's CompositeSubjectFactory output.
        if hasattr(composite_subject, 'first_house') and composite_subject.first_house and hasattr(composite_subject.first_house, 'sign'):
            houses_data = {}
            for i in range(1, 13):
                house_name_base = HOUSE_NUMBER_TO_NAME_BASE.get(i) # e.g. "first"
                if not house_name_base: continue

                # Kerykeion subjects usually have attributes like 'first_house', 'second_house'
                k_house_obj = getattr(composite_subject, f"{house_name_base}_house", None)
                if k_house_obj and hasattr(k_house_obj, 'sign'):
                    houses_data[str(i)] = HouseCuspData(
                        house=i,
                        sign=k_house_obj.sign,
                        position=round(k_house_obj.position, 4),
                        quality=getattr(k_house_obj, 'quality', None),
                        element=getattr(k_house_obj, 'element', None),
                        emoji=getattr(k_house_obj, 'sign_emoji', None)
                    )

            # Ascendant and Midheaven from the composite subject if available
            if hasattr(composite_subject, 'ascendant') and composite_subject.ascendant and hasattr(composite_subject.ascendant, 'sign'):
                k_asc = composite_subject.ascendant
                asc_data = HouseCuspData(house=1, sign=k_asc.sign, position=round(k_asc.position,4), quality=getattr(k_asc, 'quality', None), element=getattr(k_asc, 'element', None), emoji=getattr(k_asc, 'sign_emoji', None))
            elif houses_data.get("1"): # Fallback to first house cusp if direct ascendant not found
                asc_data = houses_data.get("1")

            if hasattr(composite_subject, 'medium_coeli') and composite_subject.medium_coeli and hasattr(composite_subject.medium_coeli, 'sign'):
                k_mc = composite_subject.medium_coeli
                mc_data = HouseCuspData(house=10, sign=k_mc.sign, position=round(k_mc.position,4), quality=getattr(k_mc, 'quality', None), element=getattr(k_mc, 'element', None), emoji=getattr(k_mc, 'sign_emoji', None))
            elif houses_data.get("10"): # Fallback to tenth house cusp if direct MC not found
                 mc_data = houses_data.get("10")

        # Determine the zodiac_type for the composite chart, default to person1's setting
        composite_zodiac_type = request.person1_natal_data.zodiac_type
        if hasattr(composite_subject, 'zodiac_type') and composite_subject.zodiac_type:
            composite_zodiac_type = str(composite_subject.zodiac_type)

        chart_details = CompositeChartDetails(
            name=f"Composto {request.person1_natal_data.name or 'P1'} & {request.person2_natal_data.name or 'P2'}",
            planets=planets_dict,
            houses=houses_data,
            ascendant=asc_data,
            midheaven=mc_data,
            aspects=aspects_list,
            zodiac_type=composite_zodiac_type
        )

        return CompositeChartResponse(request_data=request, composite_chart_details=chart_details)

    except ImportError as ie:
        print(f"ImportError in /composite_chart: {str(ie)}")
        raise HTTPException(status_code=501, detail="Funcionalidade de Mapa Composto não disponível (CompositeSubjectFactory não encontrado).")
    except Exception as e:
        print(f"Error in /composite_chart: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao calcular Mapa Composto: {type(e).__name__} - {str(e)}")
