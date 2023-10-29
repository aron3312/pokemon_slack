import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from src.db.models import BaseModel


class Pokemons(BaseModel):
    __tablename__ = "pokemons"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    picture = sa.Column(sa.String)
    name = sa.Column(sa.String)
    hp = sa.Column(sa.Integer)
    str = sa.Column(sa.Integer)
    defense = sa.Column(sa.Integer)
    speed = sa.Column(sa.Integer)
    tg = sa.Column(sa.Integer)
    tf = sa.Column(sa.Integer)
    lv = sa.Column(sa.Integer)

    player_pokemons = sa.orm.relationship(
        "OwnPokemons",
        lazy="select",
        uselist=True,
        back_populates="original_pokemon",
        order_by="OwnPokemons.id.desc()",
    )


class Player(BaseModel):
    __tablename__ = "player"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, unique=True, nullable=False)
    lv = sa.Column(sa.Integer, nullable=False, default=1)

    pokemons = sa.orm.relationship(
        "OwnPokemons",
        lazy="joined",
        uselist=True,
        back_populates="owner",
        order_by="OwnPokemons.id.desc()",
    )


class OwnPokemons(BaseModel):
    __tablename__ = "own_pokemons"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    owner_id = sa.Column(sa.Integer, sa.ForeignKey("player.id"))
    pokemon_id = sa.Column(sa.Integer, sa.ForeignKey("pokemons.id"))
    hp = sa.Column(sa.Integer)
    str = sa.Column(sa.Integer)
    defense = sa.Column(sa.Integer)
    speed = sa.Column(sa.Integer)
    tg = sa.Column(sa.Integer)
    tf = sa.Column(sa.Integer)
    lv = sa.Column(sa.Integer)
    experience = sa.Column(sa.Integer, nullable=False, default=1)

    owner = sa.orm.relationship("Player", lazy="joined", back_populates="pokemons")
    original_pokemon = sa.orm.relationship("Pokemons", lazy="joined", back_populates="player_pokemons")
    events = sa.orm.relationship(
        "Event",
        lazy="select",
        uselist=True,
        back_populates="use_pokemon",
        order_by="Event.id.desc()",
    )


class Event(BaseModel):
    __tablename__ = "event"

    use_pokemon_id = sa.Column(sa.Integer, sa.ForeignKey("own_pokemons.id"))
    enemy_origin_hp = sa.Column(sa.Integer)
    enemy_hp = sa.Column(sa.Integer)
    enemy_str = sa.Column(sa.Integer)
    enemy_defense = sa.Column(sa.Integer)
    enemy_speed = sa.Column(sa.Integer)
    enemy_tg = sa.Column(sa.Integer)
    enemy_tf = sa.Column(sa.Integer)
    enemy_lv = sa.Column(sa.Integer)

    use_pokemon = sa.orm.relationship("OwnPokemons", lazy="joined", back_populates="events")
