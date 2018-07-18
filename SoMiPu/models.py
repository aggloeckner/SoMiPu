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

with open("Trials.csv") as f:
    rdr = csv.reader(f, delimiter = ";")
    l = [r for r in rdr]
    d = [dict(zip(l[0],r)) for r in l[1:]]
    SoMiPu_Trials = dict( [(int(r["Trial"]),r) for r in d] )


class Constants(BaseConstants):
    name_in_url = 'SoMiPu'
    players_per_group = 2
    full_time = len(SoMiPu_Trials)
    half_time = full_time / 2
    num_rounds = full_time * 2
    



class Subsession(BaseSubsession):
    pass
        

class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # treatment des Players
    treatment = models.CharField()

    # id des Partners
    partner = models.CharField()

    # Für das Beispiel
    example_choice = models.CharField()

    # id der vom FirstChooser gewaehlten Checkbox
    firstChoice = models.CharField()

    # id der vom SecondChooser gewaehlten Checkbox in trial A
    secondChoice = models.CharField()

    # typ des gewählten items
    choice = models.CharField()

    # Set when an error is detected during submission
    error = models.BooleanField()

    # ID of the stimulus item
    stimulus = models.IntegerField()

    # Name of the stimulus item
    stimulus_name = models.CharField()

    # trial index in CSV
    trial = models.IntegerField()

    # Subtrial (which is double / single)
    subtrial = models.IntegerField()

    # Repeat (a or b)
    repeat = models.CharField()

    # Item variety that is displayed once
    single = models.CharField()

    # Item variety that is displayed twice
    double = models.CharField()

    # Display order
    item1 = models.CharField()
    item2 = models.CharField()
    item3 = models.CharField()

    # Was an ExclusionaryThreat shown?
    ExclusionaryThreat = models.BooleanField()

    # Feedback des SecondChoosers (Smilies)
    fb_s = models.IntegerField()

    # Feedback des SecondChoosers (Slider freundlich-feindselig)
    fb_ff = models.IntegerField()

    # Feedback des SecondChoosers (Slider fortsetzen-beenden)
    fb_fb = models.IntegerField()

    # Abbruch nach 12. Trial durch SecondChooser
    terminate_interaction = models.BooleanField(
        choices = [
            [True, "Interaktion beenden"],
            [False, "Weiter wählen lassen"] ],
        widget = widgets.RadioSelectHorizontal)

    # Overall Feedback (Slider freundlich-feindselig)
    overall_fb_ff = models.IntegerField()

    # Overall Feedback Half Time (Smilies)
    overall_fb_s_ht = models.IntegerField()

    # Overall Feedback Half Time (Slider freundlich-feindselig)
    overall_fb_ff_ht = models.IntegerField()

    # Overall Feedback (Smilies)
    overall_fb_s = models.IntegerField()

    # Overall Feedback (Gründe die Interaktion zu beenden)

    reason_to_finish = models.CharField(
        blank=True, 
        widget=widgets.Textarea(attrs={'rows': 4, 'cols': 100}))

    # Feedback (Checkboxen)
    overall_fb_cb1 = models.CharField(blank=True)
    overall_fb_cb2 = models.CharField(blank=True)
    overall_fb_cb3 = models.CharField(blank=True)
    overall_fb_cb4 = models.CharField(blank=True)
    overall_fb_cb5 = models.CharField(blank=True)
    overall_fb_cb6 = models.CharField(blank=True)

    # Feedback Textfelder
    overall_fb_tx1 = models.CharField(
        blank=True,
        widget=widgets.Textarea(attrs={'rows': 4, 'cols': 100}))
    overall_fb_tx2 = models.CharField(
        blank=True,
        widget=widgets.Textarea(attrs={'rows': 4, 'cols': 100}))
    overall_fb_tx3 = models.CharField(
        blank=True,
        widget=widgets.Textarea(attrs={'rows': 4, 'cols': 100}))

    # Persoenliche Angaben

    participant_sex = models.IntegerField(
        choices=[
            [1, 'weiblich'],
            [2, 'männlich'],
            [3, 'divers'] ],
        widget=widgets.RadioSelect )

    participant_lang_skills = models.IntegerField(
        choices=[
            [1, 'Muttersprache'],
            [2, 'sehr gut'],
            [3, 'gut'],
            [4, 'befriedigend'],
            [5, 'ausreichend'],
            [6, 'mangelhaft'] ],
        widget=widgets.RadioSelect )

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
        trials = SoMiPu_Trials.keys()
        tids = list( trials )
        random.shuffle( tids )
        
        subOrder = [[0,1] for _ in tids]
        itemOrder = [[[0,1,2],[0,1,2]] for _ in tids]
        for i,_ in enumerate(tids):
            random.shuffle( subOrder[i] )
            for j,_ in enumerate(itemOrder[i]):
                random.shuffle( itemOrder[i][j] )

        self.participant.vars["SoMiPu_Order"]     = tids
        self.participant.vars["SoMiPu_SubOrder"]  = subOrder
        self.participant.vars["SoMiPu_ItemOrder"] = itemOrder

    def trial_idx(self):
        return int( (self.subsession.round_number -1 ) / 2) + 1

    def repeat_idx(self):
        return (self.subsession.round_number - 1) % 2

    def repeat_name(self):
        repeats = ["a", "b"]
        return repeats[ self.repeat_idx() ]

    def get_fp(self):
        return self.group.get_player_by_role('FirstChooser')

    def get_sp(self):
        return self.group.get_player_by_role('SecondChooser')

    def get_order(self):
        return self.get_fp().participant.vars["SoMiPu_Order"]

    def get_item_idx(self):
        return self.get_order()[ self.trial_idx() - 1 ]

    def get_trial(self):
        return SoMiPu_Trials[ self.get_item_idx() ]

    def get_subtrial(self):
        return self.get_fp().participant.vars["SoMiPu_SubOrder"][ self.trial_idx() - 1 ][ self.repeat_idx() ]

    def get_itemOrder(self):
        return self.get_fp().participant.vars["SoMiPu_ItemOrder"][ self.trial_idx() - 1 ][ self.get_subtrial() ]

    def get_firstchoice(self):
        ret = self.get_fp().firstChoice
        if ret is None or ret == "":
            raise AssertionError("First choice not set!")
        return ret

    def get_secondchoice(self):
        ret = self.get_sp().secondChoice
        if ret is None or ret == "":
            raise AssertionError("Second choice not set!")
        return ret

    def get_smilyfeedback(self):
        ret = self.get_sp().fb_s
        if ret is None:
            raise AssertionError("Smily feedback not set!")
        return ret

    def is_halftime(self):
        return (self.trial_idx() == Constants.half_time) and (self.repeat_idx() == 1)

    def is_not_halftime(self):
        return not self.is_halftime()

    def after_halftime(self):
        return self.trial_idx() > Constants.half_time

    def before_halftime(self):
        return not self.after_halftime()

    def is_fulltime(self):
        return (self.trial_idx() == Constants.full_time) and (self.repeat_idx() == 1)

    def is_not_fulltime(self):
        return not self.is_fulltime()

    def terminate(self):
        self.get_fp().participant.vars["SoMiPu_terminated"] = True
        self.get_sp().participant.vars["SoMiPu_terminated"] = True

    def has_terminated(self):
        return ("SoMiPu_terminated" in self.participant.vars) and self.participant.vars["SoMiPu_terminated"]

    def has_not_terminated(self):
        return not self.has_terminated()

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
        assert self.condition() == self.get_fp().condition()
        assert self.condition() == self.get_sp().condition()

        # Termination status matches the one from our partner
        assert self.has_terminated() == self.get_fp().has_terminated()
        assert self.has_terminated() == self.get_sp().has_terminated()
