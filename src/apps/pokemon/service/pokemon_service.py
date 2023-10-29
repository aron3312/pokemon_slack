from sqlalchemy.sql.expression import func, select
from sqlalchemy.exc import IntegrityError

from src.db.base import async_session
from src.apps.pokemon.models import Pokemons, OwnPokemons, Player

SESSION = async_session()


class PokemonService(object):
    pokemon_info_fields = ["id", "name", "lv", "hp", "str", "speed", "defense", "tg", "tf", ]

    @classmethod
    def transform_to_pokemon_info_template(cls, pokemon, owned=False):
        pokemon_info = {}
        for field in cls.pokemon_info_fields:
            pokemon_info[field] = getattr(pokemon, field)
        pokemon_info["picture"] = getattr(pokemon, "picture") if not owned else pokemon.original_pokemon.picture
        return pokemon_info

    @classmethod
    async def get_user_by_name(cls, user_name: str) -> Player:
        result = await SESSION.execute(select(Player).where(Player.name == user_name))
        return result.scalar()

    @classmethod
    async def get_own_pokemon_by_id(cls, own_pokemon_id: int) -> OwnPokemons:
        result = await SESSION.execute(select(OwnPokemons).where(OwnPokemons.id == own_pokemon_id))
        return result.scalar()

    @classmethod
    async def get_random_pokemon(cls) -> Pokemons:
        result = await SESSION.execute(select(Pokemons).order_by(func.random()).limit(1))
        return result.scalar()

    @classmethod
    async def add_pokemon_to_player(cls, pokemon: Pokemons, player: Player) -> Player:
        own_pokemon = OwnPokemons()
        own_pokemon.original_pokemon = pokemon
        own_pokemon.hp = pokemon.hp
        own_pokemon.str = pokemon.str
        own_pokemon.speed = pokemon.speed
        own_pokemon.defense = pokemon.defense
        own_pokemon.tg = pokemon.tg
        own_pokemon.tf = pokemon.tf
        own_pokemon.lv = pokemon.lv
        own_pokemon.name = pokemon.name
        player.pokemons.append(own_pokemon)
        SESSION.add(player)
        try:
            await SESSION.commit()
        except IntegrityError as ex:
            await SESSION.rollback()
            raise ex
        return True

    @classmethod
    async def delete_own_pokemon(cls, own_pokemon: OwnPokemons) -> bool:
        try:
            await SESSION.delete(own_pokemon)
            await SESSION.commit()
        except IntegrityError as ex:
            await SESSION.rollback()
            raise ex
        return True
