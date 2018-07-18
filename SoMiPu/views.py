from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from .trialList import TrialList

from string import digits
import random

# Global variables for design

SMILEY_IMG_URL      = "img/SoMiPu/Smiley-Skala.png"
SMILEY_LIST_WIDTH   = 500

############ Decorators   ###########

def DisplayAt(when):
    def _wrapper(cls):
        orig_is_displayed = cls.is_displayed
        def is_displayed(self):
            return (orig_is_displayed(self) and when(self) )
        cls.is_displayed = is_displayed
        return cls
    return _wrapper

OnlyFirstRound      = lambda page: page.round_number == 1
OnlyHalfTime        = lambda page: page.player.is_halftime()
OnlyFullTime        = lambda page: page.player.is_fulltime()
OnlyFirstPlayer     = lambda page: page.player.is_first()
OnlySecondPlayer    = lambda page: page.player.is_second()
HasNotTerminated    = lambda page: page.player.has_not_terminated()
HasTerminated       = lambda page: page.player.has_terminated()
ConditionExp        = lambda page: page.player.is_experimental()
ConditionCont       = lambda page: page.player.is_control()



############ Base classes ###########

class SoMiPu_Page(Page):
    def is_displayed(self):
        self.player.check_consistency()
        return True


# Base class for all trials including example trials
class SoMiPu_Trial(SoMiPu_Page):
    def vars_for_template(self):
        ret = {
            "condition"         : self.player.condition(),
            "role"              : self.player.role(),
            "smilyImgUrl"       : SMILEY_IMG_URL,
            "smilyListWidth"    : SMILEY_LIST_WIDTH,
            "feedback"          : False }

        return ret

class SoMiPu_MainTrial(SoMiPu_Trial):

    def get_form_fields(self):
        ret = [ 'stimulus', 'stimulus_name', 'trial', 'subtrial', 'repeat',
                'single', 'double',
                'item1', 'item2', 'item3',
                'firstChoice', 'choice',
                'ExclusionaryThreat' ]

        if self.player.is_second():
            ret.append("secondChoice")
            ret.append("fb_ff")
            if self.player.is_experimental():
                ret.append("fb_s")
            if self.player.repeat_name() == "b":
                ret.append("fb_fb")

        return ret


    def vars_for_template(self):
        ret = super(SoMiPu_MainTrial, self).vars_for_template()

        trial  = self.player.get_trial()
        stid   = trial["Trial"]
        tidx   = self.player.trial_idx()
        repeat = self.player.repeat_name()
        item   = trial["Item"]
        vr1    = trial["Variety1"]
        vr2    = trial["Variety2"]

        subtrial  = self.player.get_subtrial()
        itemOrder = self.player.get_itemOrder()

        ret["repeat"]           = repeat
        ret["stimulus"]         = stid
        ret["stimulus_name"]    = item
        ret["trial"]            = tidx
        ret["subtrial"]         = subtrial

        if subtrial == 0:
            # Subtrial 0:
            # First item single, second item double
            single = vr1
            double = vr2
        else:
            # Subtrial 1:
            # First item double, second item single
            single = vr2
            double = vr1

        ret["single"] = single
        ret["double"] = double
    

        choiceList = [
            { "id"      :   "item_{}{}_1".format(stid, repeat),
              "value"   :   "single",
              "url"     :   "img/SoMiPu/{}_{}.png".format(item,single) },

            { "id"      :   "item_{}{}_2".format(stid,repeat),
              "value"   :   "double",
              "url"     :   "img/SoMiPu/{}_{}.png".format(item,double) },

            { "id"      :   "item_{}{}_3".format(stid,repeat),
              "value"   :   "double",
              "url"     :   "img/SoMiPu/{}_{}.png".format(item,double) } ]

        ret["choiceList"] = [choiceList[itemOrder[i]] for i in range(3)]

        ret["ExclusionaryThreat"] = ((repeat == "b") and self.player.before_halftime())

        ret["choiceName"] = "choice"

        if self.player.is_first():
            ret["firstChoice"]  = ""
        else:
            ret["firstChoice"] = self.player.get_firstchoice()

        ret["smilyName"] = "fb_s"
        ret["smilyFeedback"] = ""

        if not (ret["firstChoice"] == "" or ret["firstChoice"] in [c["id"] for c in choiceList]):
            raise AssertionError("First choice {} not a valid first choice!".format(ret["firstChoice"]))

        return ret

    def firstChoice_error_message(self, value):
        trial  = self.player.get_trial()
        stid   = trial["Trial"]
        repeat = self.player.repeat_name()

        choices = ["item_{}{}_{}".format(stid, repeat, i) for i in [1,2,3]]
        if not value in choices:
            return """
                Es ist ein Fehler aufgetreten!\n
                Auswahl {} ist keine verfügbare Auswahl.\n
                Bitte melden Sie sich beim Versuchsleiter!""".format(value)

    def secondChoice_error_message(self, value):
        trial  = self.player.get_trial()
        stid   = trial["Trial"]
        repeat = self.player.repeat_name()

        choices = ["item_{}{}_{}".format(stid, repeat, i) for i in [1,2,3]]
        if not value in choices:
            return """
                Es ist ein Fehler aufgetreten!\n
                Auswahl {} ist keine verfügbare Auswahl.\n
                Bitte melden Sie sich beim Versuchsleiter!""".format(value)

        if value == self.player.get_firstchoice():
            return """
                Es ist ein Fehler aufgetreten!\n
                Auswahl {} wurde bereits gewählt.\n
                Bitte melden Sie sich beim Versuchsleiter!""".format(value)


    def choice_error_message(self, value):
        trial  = self.player.get_trial()
        stid   = trial["Trial"]
        repeat = self.player.repeat_name()

        if value not in ["single", "double"]:
            return """
                Es ist ein Fehler aufgetreten!\n
                Auswahl {} ist kein verfügbarer Auswahltyp.\n
                Bitte melden Sie sich beim Versuchsleiter!""".format(value)

        if self.player.is_second() and value == "single" and self.player.get_fp().choice == "single":
            return """
                Es ist ein Fehler aufgetreten!\n
                Auswahltyp bereits vom ersten Spieler gewählt.\n
                Bitte melden Sie sich beim Versuchsleiter!"""


        

class SoMiPu_Wait(WaitPage):
    template_name = "SoMiPu/WaitPage.html"

    def vars_for_template(self):
        return {'body_text': "Sobald die andere Person ihre Wahl getroffen hat, geht es weiter.",
                'title_text': "Bitte warten Sie ..."}

    def is_displayed(self):
        self.player.check_consistency()
        return True



############# Actual Pages ###########

@DisplayAt(OnlyFirstRound)
class GroupingWaitPage(WaitPage):
    group_by_arrival_time = True

    def get_players_for_group(self, waiting_players):
        if len(waiting_players) >= 2:

            treatment = self.session.config['treatment']
            if treatment != 'experimental' and treatment != 'control':
                treatment = random.choice(["experimental", "control"])

            p1 = waiting_players[0]
            p2 = waiting_players[1]

            p1.treatment = p2.treatment = treatment
            p1.participant.vars["treatment"] = p2.participant.vars["treatment"] = treatment
            p1.partner = p1.participant.vars["partner"] = p2.participant.code
            p2.partner = p2.participant.vars["partner"] = p1.participant.code

            p1.randomize_trials()

            return [p1, p2]

    # template_name = 'GroupingWaitPage.html'
    def vars_for_template(self):
        return {'body_text': "Sobald die nächste Person eintrifft, geht es los.",
                'title_text': "Bitte warten Sie."}


@DisplayAt(OnlyFirstRound)
class Decision(SoMiPu_Page):
    def vars_for_template(self):
        return {
            "condition" : self.player.condition(),
            "role"      : self.player.role()
        }


@DisplayAt(OnlyFirstRound)
class Example(SoMiPu_Trial):
    form_model = 'player'
    form_fields = ['example_choice']

    def vars_for_template(self):
        ret = super(Example,self).vars_for_template()
        ret["choiceName"] =  "example_choice"

        ret["choiceList"] = [
            {
                "id"            : "example0",
                "url"           : "img/SoMiPu/MM_green.png",
                "value"         : "double"
            },
            {
                "id"            : "example1",
                "url"           : "img/SoMiPu/MM_blue.png",
                "value"         : "single"
            },
            {
                "id"            : "example2",
                "url"           : "img/SoMiPu/MM_green.png",
                "value"         : "double"

            }]

        ret["smilyName"] = "smily_example"

        if self.player.is_second():
            ret["firstChoice"]   = "example0"
            ret["smilyFeedback"] = ""
        else:
            ret["firstChoice"]   = ""
            ret["smilyFeedback"] = "-1"

        return ret

    def before_next_page(self):
        # Initial payoff of 2 points for the experiment
        # 2 more points if the last page is reached
        self.player.payoff = c(2)

@DisplayAt(HasNotTerminated)
@DisplayAt(OnlyFirstPlayer)
class Trials_FP (SoMiPu_MainTrial):
    template_name = "SoMiPu/Trials_FirstPlayer.html"
    form_model = models.Player


@DisplayAt(HasNotTerminated)
class Wait_Trials_FP(SoMiPu_Wait):
    pass

@DisplayAt(HasNotTerminated)
@DisplayAt(OnlySecondPlayer)
class Trials_SP (SoMiPu_MainTrial):
    template_name = "SoMiPu/Trials_SecondPlayer.html"
    form_model = models.Player

@DisplayAt(OnlyHalfTime)
@DisplayAt(OnlySecondPlayer)
class OFB_SP_HT(SoMiPu_Trial):
    template_name = "SoMiPu/Overall_Feedback_SecondPlayer_Half_Time.html"
    form_model = models.Player


    def get_form_fields(self):
        return ['overall_fb_s_ht', 'overall_fb_ff_ht']

    def vars_for_template(self):
        ret = super(OFB_SP_HT, self).vars_for_template()
        ret["smilyName"] = "overall_fb_s_ht"
        ret["smilyFeedback"] = ""

        return ret

@DisplayAt(OnlyFullTime)
@DisplayAt(HasNotTerminated)
@DisplayAt(OnlySecondPlayer)
class OFB_SP(SoMiPu_Trial):
    template_name = "SoMiPu/Overall_Feedback_SecondPlayer.html"
    form_model = models.Player
    
    def get_form_fields(self):
        return ['overall_fb_s', 'overall_fb_ff']

    def vars_for_template(self):
        ret = super(OFB_SP, self).vars_for_template()
        ret["smilyName"] = "overall_fb_s"
        ret["smilyFeedback"] = ""

        return ret


@DisplayAt(OnlyHalfTime)
@DisplayAt(ConditionExp)
@DisplayAt(OnlySecondPlayer)
class HT_ExTh(Page):
    template_name = "SoMiPu/ExclusionaryThreat_SecondPlayer.html"
    form_model = models.Player

    def get_form_fields(self):
        fields = ['terminate_interaction']
        return fields

    def before_next_page(self):
        terminate = self.player.terminate_interaction
        self.player.get_fp().terminate_interaction = terminate
        if terminate:
            self.player.terminate()


@DisplayAt(HasTerminated)
@DisplayAt(OnlyHalfTime)
@DisplayAt(ConditionExp)
@DisplayAt(OnlySecondPlayer)
class FB_RTF(Page):
    template_name = "SoMiPu/Reason_To_Finish_SecondPlayer.html"
    form_model = models.Player

    def get_form_fields(self):
        return ['reason_to_finish']


@DisplayAt(HasNotTerminated)
class Wait_Trials_SP(SoMiPu_Wait):
    def is_displayed(self):
        return self.player.has_not_terminated()


@DisplayAt(ConditionExp)
@DisplayAt(OnlyFirstPlayer)
class Exp_FB(SoMiPu_MainTrial):
    form_model = models.Player
    template_name = "SoMiPu/Experimental_Feedback_FirstPlayer.html"
    
    def get_form_fields(self):
        return []


    def vars_for_template(self):
        ret = super(Exp_FB,self).vars_for_template()

        ret["firstChoice"] = self.player.get_firstchoice()
        ret["secondChoice"] = self.player.get_secondchoice()
        ret["smilyFeedback"] = self.player.get_smilyfeedback()
        ret["hasTerminated"] = self.player.has_terminated()
        ret["halfTime"] = self.player.is_halftime()
        ret["feedback"] = True

        return ret

    def is_displayed(self):
        return (
            super(Exp_FB,self).is_displayed() and
            (self.player.before_halftime() or self.player.has_not_terminated()) )


@DisplayAt(OnlyFullTime)
class CB1_AP (SoMiPu_Page):
    template_name = "SoMiPu/Checkbox1_AllPlayers.html"
    form_model = models.Player
    
    def get_form_fields(self):
        return ['overall_fb_cb1', 'overall_fb_cb2','overall_fb_cb3', 'overall_fb_cb4','overall_fb_cb5', 'overall_fb_cb6']
    

@DisplayAt(OnlyFullTime)
class CB2_AP(SoMiPu_Page):
    template_name = "SoMiPu/Checkbox2_AllPlayers.html"
    form_model = models.Player
    form_fields = ['overall_fb_tx1', 'overall_fb_tx2', 'overall_fb_tx3']

    def vars_for_template(self):
        return {"role": self.player.role()}


@DisplayAt(OnlyFullTime)
class A_PersonalData(SoMiPu_Page):
    form_model = models.Player
    def get_form_fields(self):
        return ['participant_sex', 'participant_age', 'participant_lang_skills']


@DisplayAt(OnlyFullTime)
class LastPage (SoMiPu_Page):
    def vars_for_template(self):
        # Additional 2 Euro if this page is reached without termination
        if self.player.has_not_terminated():
            self.player.payoff = c(2)
        return { 
            "payoff":           self.participant.payoff,
            "condition":        self.player.condition()
         }



page_sequence = [
    # This block only run for round_number == 1
    GroupingWaitPage,
    Decision,
    Example,

    # First player does not depend on P2 (no wait!)
    Trials_FP,
    Wait_Trials_FP,
    Trials_SP,
    OFB_SP_HT,
    OFB_SP,
    HT_ExTh,
    FB_RTF,
    Wait_Trials_SP,
    Exp_FB,
    CB1_AP,
    CB2_AP,
    A_PersonalData,
    LastPage ]
