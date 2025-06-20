from fastapi import APIRouter, HTTPException, Depends
from kerykeion import AstrologicalSubject
from app.models import NatalChartRequest, NatalChartResponse, PlanetData, HouseCuspData, AspectData
from app.security import verify_api_key
from app.utils.astro_helpers import create_subject, get_planet_data, PLANETS_MAP, HOUSE_NUMBER_TO_NAME_BASE
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/api/v1",
    tags=["Natal Chart"],
    dependencies=[Depends(verify_api_key)]
)

@router.post("/natal_chart", response_model=NatalChartResponse)
async def create_natal_chart(request: NatalChartRequest):
    try:
        # Validar que pelo menos city ou (latitude + longitude + tz_str) foram fornecidos
        if not request.city and not (request.latitude and request.longitude and request.tz_str):
            raise HTTPException(
                status_code=400, 
                detail="É necessário fornecer 'city' ou ('latitude' + 'longitude' + 'tz_str')"
            )
        
        # Usar a função utilitária para criar o subject (agora com resolução de localização)
        subject, location_info = create_subject(request, request.name if request.name else "NatalChart")
        
        # Dicionário para armazenar os planetas
        planets_dict: Dict[str, PlanetData] = {}
        for k_name, api_name in PLANETS_MAP.items():
            planet_data = get_planet_data(subject, k_name, api_name)
            if planet_data:
                # Converter PlanetPosition para PlanetData
                planets_dict[k_name] = PlanetData(
                    name=planet_data.name,
                    sign=planet_data.sign,
                    sign_num=planet_data.sign_num,
                    position=planet_data.position,
                    abs_pos=planet_data.abs_pos,
                    house_name=planet_data.house_name,
                    house_number=planet_data.house_number,
                    speed=planet_data.speed,
                    retrograde=planet_data.retrograde,
                    quality=planet_data.quality,
                    element=planet_data.element,
                    emoji=planet_data.emoji
                )
        
        if hasattr(subject, 'chiron') and subject.chiron:
            chiron_data = get_planet_data(subject, 'chiron', 'Chiron') # get_planet_data now returns PlanetPosition with new fields
            if chiron_data:
                planets_dict['chiron'] = PlanetData(
                    name=chiron_data.name,
                    sign=chiron_data.sign,
                    sign_num=chiron_data.sign_num,
                    position=chiron_data.position,
                    abs_pos=chiron_data.abs_pos,
                    house_name=chiron_data.house_name,
                    house_number=chiron_data.house_number,
                    speed=chiron_data.speed,
                    retrograde=chiron_data.retrograde,
                    quality=chiron_data.quality,
                    element=chiron_data.element,
                    emoji=chiron_data.emoji
                )
        
        # For Lilith, Kerykeion's subject.lilith might not have all these detailed fields like quality, element, emoji
        # It's typically a simpler point object. We'll populate what's available.
        if hasattr(subject, 'lilith') and subject.lilith and hasattr(subject.lilith, 'name') and subject.lilith.name:
            lilith_house_name_str = str(subject.lilith.house if hasattr(subject.lilith, 'house') else None)
            lilith_house_num = None
            if hasattr(subject.lilith, 'house'): # Try to get house number if possible
                try:
                    lilith_house_num = int(str(subject.lilith.house_number)) # Kerykeion 5 usually has house_number for points
                except: # Fallback if direct house_number is not found or not int
                    from app.utils.astro_helpers import get_house_from_kerykeion_attribute # Import if not already
                    lilith_house_num = get_house_from_kerykeion_attribute(subject.lilith)


            planets_dict['lilith'] = PlanetData(
                name="Lilith",
                sign=subject.lilith.sign,
                sign_num=subject.lilith.sign_num,
                position=round(subject.lilith.position, 4),
                abs_pos=round(subject.lilith.abs_pos, 4),
                house_name=lilith_house_name_str,
                house_number=lilith_house_num,
                speed=round(subject.lilith.speed, 4) if hasattr(subject.lilith, 'speed') else 0.0,
                retrograde=False, # Lilith usually not retrograde
                quality=subject.lilith.quality if hasattr(subject.lilith, 'quality') else None,
                element=subject.lilith.element if hasattr(subject.lilith, 'element') else None,
                emoji=subject.lilith.sign_emoji if hasattr(subject.lilith, 'sign_emoji') else None
            )

        # Dicionário para armazenar as casas
        houses_dict: Dict[str, HouseCuspData] = {}
        for i in range(1, 13):
            house_name_base = HOUSE_NUMBER_TO_NAME_BASE.get(i)
            if not house_name_base:
                continue
            
            house_obj_attr_name = f"{house_name_base}_house" # e.g., "first_house"
            house_obj = getattr(subject, house_obj_attr_name) # e.g., subject.first_house
            houses_dict[str(i)] = HouseCuspData(
                house=i,
                sign=house_obj.sign,
                position=round(house_obj.position, 4),
                quality=house_obj.quality if hasattr(house_obj, 'quality') else None,
                element=house_obj.element if hasattr(house_obj, 'element') else None,
                emoji=house_obj.sign_emoji if hasattr(house_obj, 'sign_emoji') else None
            )

        # Ascendente e Meio do Céu
        ascendant = HouseCuspData(
            house=1,
            sign=subject.first_house.sign,
            position=round(subject.first_house.position, 4),
            quality=subject.first_house.quality if hasattr(subject.first_house, 'quality') else None,
            element=subject.first_house.element if hasattr(subject.first_house, 'element') else None,
            emoji=subject.first_house.sign_emoji if hasattr(subject.first_house, 'sign_emoji') else None
        )
        
        midheaven = HouseCuspData(
            house=10,
            sign=subject.tenth_house.sign,
            position=round(subject.tenth_house.position, 4),
            quality=subject.tenth_house.quality if hasattr(subject.tenth_house, 'quality') else None,
            element=subject.tenth_house.element if hasattr(subject.tenth_house, 'element') else None,
            emoji=subject.tenth_house.sign_emoji if hasattr(subject.tenth_house, 'sign_emoji') else None
        )

        # Lista para armazenar os aspectos
        aspects_list: List[AspectData] = []
        main_planets_for_aspects = [
            subject.sun, subject.moon, subject.mercury, subject.venus, subject.mars,
            subject.jupiter, subject.saturn, subject.uranus, subject.neptune, subject.pluto
        ]

        processed_aspects = set()
        for p1 in main_planets_for_aspects:
            if not p1 or not hasattr(p1, 'aspects'): continue
            for asp in p1.aspects:
                p2_name = asp.p2_name
                pair = tuple(sorted((p1.name, p2_name)) + (asp.aspect_name,))
                if pair not in processed_aspects:
                    aspects_list.append(AspectData(
                        p1_name=p1.name,
                        p1_name_original=p1.name,
                        p1_owner="chart",
                        p2_name=p2_name,
                        p2_name_original=p2_name,
                        p2_owner="chart",
                        aspect=asp.aspect_name,
                        aspect_original=asp.aspect_name,
                        orbit=round(asp.orbit, 4),
                        aspect_degrees=float(asp.aspect_name.split("_")[0]) if "_" in asp.aspect_name else 0.0,
                        diff=abs(round(asp.orbit, 4)),
                        applying=False  # Valor padrão, não disponível diretamente
                    ))
                    processed_aspects.add(pair)
        
        # Criar o objeto de resposta
        response = NatalChartResponse(
            input_data=request,
            planets=planets_dict,
            houses=houses_dict,
            ascendant=ascendant,
            midheaven=midheaven,
            aspects=aspects_list,
            house_system=request.house_system,
            interpretations=None,
            resolved_location=location_info  # Incluir informações da localização resolvida
        )
        
        return response

    except ValueError as e:
        # Erro de validação de localização
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Erro de cálculo astrológico em natal_chart (Kerykeion ou outro): {type(e).__name__} - {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Erro de cálculo astrológico (Kerykeion): {str(e)}")