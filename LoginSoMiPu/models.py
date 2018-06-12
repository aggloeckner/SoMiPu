from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

author = 'Carola Ortlepp-Appl'

doc = """
Login für SoMiPu, Entscheidungsaufgabe mit zwei Personen
"""


class Constants(BaseConstants):
    name_in_url = 'LoginSoMiPu'
    players_per_group = None
    num_rounds = 1



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # id des Teilnehmers
    decision_lab_id = models.CharField()

