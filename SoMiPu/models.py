from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
)

import itertools
import random


author = 'Carola Ortlepp-Appl'

doc = """
Entscheidungsaufgabe mit zwei Personen
"""


class Constants(BaseConstants):
    name_in_url = 'SoMiPu'
    players_per_group = 2
    num_rounds = 1



class Subsession(BaseSubsession):
    def creating_session(self):

        for group in self.get_groups():
            self.session.vars['treatment'] = 'control'


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # treatment des Players
    treatment = models.CharField()

    # id des Teilnehmers
    decision_lab_id = models.CharField()

    # id der vom FirstChooser gewaehlten Checkbox
    firstChoice = models.CharField()

    # id der vom SecondChooser gewaehlten Checkbox
    secondChoice = models.CharField()

    # trials - Auswahl des FirstChoosers
    trial_1a = models.CharField()
    trial_1b = models.CharField()
    trial_2a = models.CharField()
    trial_2b = models.CharField()
    trial_3a = models.CharField()
    trial_3b = models.CharField()
    trial_4a = models.CharField()
    trial_4b = models.CharField()
    trial_5a = models.CharField()
    trial_5b = models.CharField()
    trial_6a = models.CharField()
    trial_6b = models.CharField()
    trial_7a = models.CharField()
    trial_7b = models.CharField()
    trial_8a = models.CharField()
    trial_8b = models.CharField()
    trial_9a = models.CharField()
    trial_9b = models.CharField()
    trial_10a = models.CharField()
    trial_10b = models.CharField()
    trial_11a = models.CharField()
    trial_11b = models.CharField()
    trial_12a = models.CharField()
    trial_12b = models.CharField()

    # gespielte Reihenfolge der trials
    trial_1a_seq = models.IntegerField()
    trial_1b_seq = models.IntegerField()
    trial_2a_seq = models.IntegerField()
    trial_2b_seq = models.IntegerField()
    trial_3a_seq = models.IntegerField()
    trial_3b_seq = models.IntegerField()
    trial_4a_seq = models.IntegerField()
    trial_4b_seq = models.IntegerField()
    trial_5a_seq = models.IntegerField()
    trial_5b_seq = models.IntegerField()
    trial_6a_seq = models.IntegerField()
    trial_6b_seq = models.IntegerField()
    trial_7a_seq = models.IntegerField()
    trial_7b_seq = models.IntegerField()
    trial_8a_seq = models.IntegerField()
    trial_8b_seq = models.IntegerField()
    trial_9a_seq = models.IntegerField()
    trial_9b_seq = models.IntegerField()
    trial_10a_seq = models.IntegerField()
    trial_10b_seq = models.IntegerField()
    trial_11a_seq = models.IntegerField()
    trial_11b_seq = models.IntegerField()
    trial_12a_seq = models.IntegerField()
    trial_12b_seq = models.IntegerField()

    # Feedback des SecondChoosers (Smilies)
    trial_1a_fb_s = models.IntegerField()
    trial_1b_fb_s = models.IntegerField()
    trial_2a_fb_s = models.IntegerField()
    trial_2b_fb_s = models.IntegerField()
    trial_3a_fb_s = models.IntegerField()
    trial_3b_fb_s = models.IntegerField()
    trial_4a_fb_s = models.IntegerField()
    trial_4b_fb_s = models.IntegerField()
    trial_5a_fb_s = models.IntegerField()
    trial_5b_fb_s = models.IntegerField()
    trial_6a_fb_s = models.IntegerField()
    trial_6b_fb_s = models.IntegerField()
    trial_7a_fb_s = models.IntegerField()
    trial_7b_fb_s = models.IntegerField()
    trial_8a_fb_s = models.IntegerField()
    trial_8b_fb_s = models.IntegerField()
    trial_9a_fb_s = models.IntegerField()
    trial_9b_fb_s = models.IntegerField()
    trial_10a_fb_s = models.IntegerField()
    trial_10b_fb_s = models.IntegerField()
    trial_11a_fb_s = models.IntegerField()
    trial_11b_fb_s = models.IntegerField()
    trial_12a_fb_s = models.IntegerField()
    trial_12b_fb_s = models.IntegerField()

    # Feedback des SecondChoosers (Slider freundlich-feindselig)
    trial_1a_fb_ff = models.IntegerField()
    trial_1b_fb_ff = models.IntegerField()
    trial_2a_fb_ff = models.IntegerField()
    trial_2b_fb_ff = models.IntegerField()
    trial_3a_fb_ff = models.IntegerField()
    trial_3b_fb_ff = models.IntegerField()
    trial_4a_fb_ff = models.IntegerField()
    trial_4b_fb_ff = models.IntegerField()
    trial_5a_fb_ff = models.IntegerField()
    trial_5b_fb_ff = models.IntegerField()
    trial_6a_fb_ff = models.IntegerField()
    trial_6b_fb_ff = models.IntegerField()
    trial_7a_fb_ff = models.IntegerField()
    trial_7b_fb_ff = models.IntegerField()
    trial_8a_fb_ff = models.IntegerField()
    trial_8b_fb_ff = models.IntegerField()
    trial_9a_fb_ff = models.IntegerField()
    trial_9b_fb_ff = models.IntegerField()
    trial_10a_fb_ff = models.IntegerField()
    trial_10b_fb_ff = models.IntegerField()
    trial_11a_fb_ff = models.IntegerField()
    trial_11b_fb_ff = models.IntegerField()
    trial_12a_fb_ff = models.IntegerField()
    trial_12b_fb_ff = models.IntegerField()

    # Feedback des SecondChoosers (Slider fortsetzen-beenden)
    trial_1b_fb_fb = models.IntegerField()
    trial_2b_fb_fb = models.IntegerField()
    trial_3b_fb_fb = models.IntegerField()
    trial_4b_fb_fb = models.IntegerField()
    trial_5b_fb_fb = models.IntegerField()
    trial_6b_fb_fb = models.IntegerField()
    trial_7b_fb_fb = models.IntegerField()
    trial_8b_fb_fb = models.IntegerField()
    trial_9b_fb_fb = models.IntegerField()
    trial_10b_fb_fb = models.IntegerField()
    trial_11b_fb_fb = models.IntegerField()
    trial_12b_fb_fb = models.IntegerField()

    # Abbruch nach 12. Trial durch SecondChooser
    terminate_interaction = models.BooleanField()

    # Overall Feedback (Slider freundlich-feindselig)
    overall_fb_ff = models.IntegerField()

    # Overall Feedback Half Time (Smilies)
    overall_fb_s_ht = models.IntegerField()

    # Overall Feedback Half Time (Slider freundlich-feindselig)
    overall_fb_ff_ht = models.IntegerField()

    # Overall Feedback (Smilies)
    overall_fb_s = models.IntegerField()

    # Overall Feedback (Gründe die Interaktion zu beenden)

    reason_to_finish = models.CharField(blank=True)

    # Feedback (Checkboxen)
    overall_fb_cb1 = models.CharField(blank=True)
    overall_fb_cb2 = models.CharField(blank=True)
    overall_fb_cb3 = models.CharField(blank=True)
    overall_fb_cb4 = models.CharField(blank=True)
    overall_fb_cb5 = models.CharField(blank=True)
    overall_fb_cb6 = models.CharField(blank=True)

    # Feedback Textfelder
    overall_fb_tx1 = models.CharField(blank=True)
    overall_fb_tx2 = models.CharField(blank=True)
    overall_fb_tx3 = models.CharField(blank=True)

    # Persoenliche Angaben

    participant_sex = models.IntegerField\
            (choices=[
                [0, 'Bitte wählen Sie'],
                [1, 'weiblich'],
                [2, 'männlich'],
                [3, 'divers'],
            ]
    )

    participant_lang_skills = models.IntegerField\
            (choices=[
                [0, 'Bitte wählen Sie'],
                [1, 'Muttersprache'],
                [2, 'sehr gut'],
                [3, 'gut'],
                [4, 'befriedigend'],
                [5, 'ausreichend'],
                [6, 'mangelhaft'],
            ]
    )

    participant_age = models.IntegerField(min=18, max=99)



    def role(self):
        if self.id_in_group == 1:
            return 'FirstChooser'
        else:
            return 'SecondChooser'