from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
)

import itertools
import random
import csv


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
        with open("Trials.csv") as f:
            rdr = csv.reader(f, delimiter = ";")
            l = [r for r in rdr]
            d = [dict(zip(l[0],r)) for r in l[1:]]
            trials = dict( [(int(r["Trial"]),r) for r in d] )
            self.session.vars["SoMiPu_Trials"] = trials



class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # treatment des Players
    treatment = models.CharField()

    # id des Partners
    partner = models.CharField()

    # Für das Beispiel
    example_choice = models.CharField()

    ##### Fields for A Trials

    # id der vom FirstChooser gewaehlten Checkbox
    firstChoice_a = models.CharField()

    # id der vom SecondChooser gewaehlten Checkbox in trial A
    secondChoice_a = models.CharField()

    # ID of the stimulus item
    stimulus_a = models.IntegerField()

    # Name of the stimulus item
    stimulus_name_a = models.CharField()

    subtrial_a = models.IntegerField()

    # Item variety that is displayed once
    single_a = models.CharField()

    # Item variety that is displayed twice
    double_a = models.CharField()

    # Display order
    item1_a = models.CharField()
    item2_a = models.CharField()
    item3_a = models.CharField()

    ##### Fields for B Trials

    # id der vom FirstChooser gewaehlten Checkbox
    firstChoice_b = models.CharField()

    # id der vom SecondChooser gewaehlten Checkbox in trial A
    secondChoice_b = models.CharField()

    # ID of the stimulus item
    stimulus_b = models.IntegerField()

    # Name of the stimulus item
    stimulus_name_b = models.CharField()

    subtrial_b = models.IntegerField()

    # Item variety that is displayed once
    single_b = models.CharField()

    # Item variety that is displayed twice
    double_b = models.CharField()

    # Display order
    item1_b = models.CharField()
    item2_b = models.CharField()
    item3_b = models.CharField()

    
    


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

    def is_first(self):
        return self.role() == "FirstChooser"

    def is_second(self):
        return self.role() == "SecondChooser"

    def condition(self):
        return self.participant.vars["treatment"]

    def is_experimental(self):
        return self.condition() == "experimental"

    def is_control(self):
        return self.condition() == "control"

    def randomize_trials(self):
        trials = self.session.vars["SoMiPu_Trials"].keys()
        tids = list( trials )
        random.shuffle( tids )
        self.participant.vars["SoMiPu_Order"]     = tids
        self.participant.vars["SoMiPu_CompFirst"] = [random.randrange(2) for _ in tids]


        itemOrder = [[[0,1,2],[0,1,2]] for _ in tids]
        for i,_ in enumerate(itemOrder):
            for j,_ in enumerate(itemOrder[i]):
                random.shuffle( itemOrder[i][j] )

        self.participant.vars["SoMiPu_ItemOrder"] = itemOrder

    def get_fp(self):
        return self.group.get_player_by_role('FirstChooser')

    def get_sp(self):
        return self.group.get_player_by_role('SecondChooser')

    def get_order(self, round_number):
        return self.get_fp().participant.vars["SoMiPu_Order"][round_number - 1]

    def get_trial(self, round_number):
        return self.session.vars["SoMiPu_Trials"][ self.get_order( round_number ) ]

    def get_subtrial(self, round_number):
        return self.get_fp().participant.vars["SoMiPu_CompFirst"][ round_number - 1 ]

    def get_itemOrder(self, round_number, subtrial):
        return self.get_fp().participant.vars["SoMiPu_ItemOrder"][ round_number - 1 ][ subtrial ]

    def check_consistency(self):
        mycode = self.participant.code
        fpcode = self.get_fp().participant.code
        spcode = self.get_sp().participant.code
        partner = self.participant.vars["partner"]

        # Checks for first player
        if self.is_first():
            if mycode != fpcode:
                raise AssertionError( "Player {} is first player, but first by role is {}".format( mycode, fpcode ))
            if partner != spcode:
                raise AssertionError( "First player {} has partner {}, but second by role is {}".format( mycode, partner, spcode ))

        # Checks for second player
        if self.is_second():
            if mycode != spcode:
                raise AssertionError( "Player {} is second player, but second by role is {}".format( mycode, spcode ))
            if partner != fpcode:
                raise AssertionError( "Second player {} has partner {}, but first by role is {}".format( mycode, partner, fpcode ))


        # Our condition matches the one from our partner
        assert self.condition() == self.group.get_player_by_role('FirstChooser').condition()
        assert self.condition() == self.group.get_player_by_role('SecondChooser').condition()
