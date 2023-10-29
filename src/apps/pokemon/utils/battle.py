from src.apps.pokemon.utils.info import PokemonInfo


class BattleHandler(object):
    def __init__(self, init_info: PokemonInfo, opponent_info: PokemonInfo):
        self.init_info = init_info
        self.opponent_info = opponent_info
