import re

from fastapi import APIRouter, Depends, Response, status

from src import config
from src.apps.pokemon.utils.template import TemplateGenerator
from src.apps.pokemon import models, schemas
from src.apps.pokemon.service.pokemon_service import PokemonService

TEMPLATE_GENERATOR = TemplateGenerator()

router = APIRouter()


@router.get("/status")
def get_status():
    return {"status": "OK"}


@router.post('/help')
async def help():
    return TEMPLATE_GENERATOR.render_help_messages()


@router.post('/create_player')
async def create_player(data: schemas.PlayerCreate):
    instance = models.Player(**data.dict())
    try:
        await instance.save()
        message = f"訓練家:{instance.name} 創建成功 您可以開啟您的訓練之旅"
    except Exception as e:
        if re.search("UNIQUE constraint failed: player.name", e.orig.args[0] if e.orig.args else ""):
            message = f"訓練家{instance.name}已存在，請直接遊玩。"
        else:
            message = f"有些錯誤發生，請洽客服。"
    return TEMPLATE_GENERATOR.render_pure_text_message(message)

@router.post('/catch_first_pokemon')
async def catch_first_pokemon(data: schemas.PlayerCreate):
    player = await PokemonService.get_user_by_name(data.name)
    if player:
        if player.pokemons:
            response = TEMPLATE_GENERATOR.render_pure_text_message('你已經有寶可夢囉！')
        else:
            pokemon = await PokemonService.get_random_pokemon()
            success = await PokemonService.add_pokemon_to_player(pokemon, player)
            if success:
                pokemon_dict = PokemonService.transform_to_pokemon_info_template(pokemon)
                response = TEMPLATE_GENERATOR.render_catch_first_pokemon_message(pokemon_dict)
    else:
        response = TEMPLATE_GENERATOR.render_no_account_notice()
    return response


@router.post('/check_my_pokemon')
async def check_my_pokemon(data: schemas.PlayerCreate):
    player = await PokemonService.get_user_by_name(data.name)
    if player:
        own_pokemons_dict_lst = [PokemonService.transform_to_pokemon_info_template(pokemon, owned=True) for pokemon in player.pokemons]
        response = TEMPLATE_GENERATOR.render_own_pokemons_message(own_pokemons_dict_lst)
    else:
        response = TEMPLATE_GENERATOR.render_no_account_notice()
    return response


@router.post('/release')
async def release_pokemon(data: schemas.PlayerCreate):
    player = await PokemonService.get_user_by_name(data.name)
    if player:
        target_pokemon = await PokemonService.get_own_pokemon_by_id(data.text)
        if target_pokemon:
            success = await PokemonService.delete_own_pokemon(target_pokemon)
            if success:
                response = TEMPLATE_GENERATOR.render_pure_text_message(f"你已經讓 {target_pokemon.name} 回到他的棲息地了！")
        else:
            response = TEMPLATE_GENERATOR.render_pure_text_message("你沒有這個id的寶可夢喔！")
    else:
        response = TEMPLATE_GENERATOR.render_no_account_notice()
    return response
