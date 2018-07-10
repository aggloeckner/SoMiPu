from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from .trialList import TrialList

from string import digits
import random

# Global variables for design

IMG_WIDTH           = 100
IMG_COLUMN_WIDTH    = 210
SMILEY_IMG_URL      = "img/SoMiPu/Smiley-Skala.png"
SMILEY_LIST_WIDTH   = 500

############ Base classes ###########

# Base class for all trials including example trials
class SoMiPu_Trial(Page):
    def vars_for_template(self):
        ret = {
            "condition"         : self.player.condition(),
            "role"              : self.player.role(),
            "smilyImgUrl"       : SMILEY_IMG_URL,
            "smilyListWidth"    : SMILEY_LIST_WIDTH,
            "choiceColumnWidth" : IMG_COLUMN_WIDTH,
            "choiceWidth"       : IMG_WIDTH,
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

class SoMiPu_Wait(WaitPage):
    template_name = "SoMiPu/WaitPage.html"

    def vars_for_template(self):
        return {'body_text': "Sobald die andere Person ihre Wahl getroffen hat, geht es weiter.",
                'title_text': "Bitte warten Sie ..."}



############# Actual Pages ###########


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

    def is_displayed(self):
        return self.round_number == 1

class Decision(Page):
    def vars_for_template(self):
        return {
            "condition" : self.player.condition(),
            "role"      : self.player.role()
        }

    def is_displayed(self):
        self.player.check_consistency()
        return self.round_number == 1

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

    def is_displayed(self):
        self.player.check_consistency()
        return self.round_number == 1



class Trials_FP (SoMiPu_MainTrial):
    template_name = "SoMiPu/Trials_FirstPlayer.html"
    form_model = models.Player

    def is_displayed(self):
        self.player.check_consistency()
        return self.player.is_first() and self.player.has_not_terminated()


class Wait_Trials_FP(SoMiPu_Wait):
    def is_displayed(self):
        return self.player.has_not_terminated()


class Trials_SP (SoMiPu_MainTrial):
    template_name = "SoMiPu/Trials_SecondPlayer.html"
    form_model = models.Player

    def is_displayed(self):
        self.player.check_consistency()
        return self.player.is_second() and self.player.has_not_terminated()

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

    def is_displayed(self):
        self.player.check_consistency()
        return self.player.is_second() and self.player.is_halftime()

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

    def is_displayed(self):
        return (
            self.player.is_second() and
            self.player.has_not_terminated() and
            self.player.is_fulltime() )

class HT_ExTh(Page):
    template_name = "SoMiPu/ExclusionaryThreat_SecondPlayer.html"
    form_model = models.Player

    def get_form_fields(self):
        fields = ['terminate_interaction']
        return fields

    def is_displayed(self):
        self.player.check_consistency()
        return ( 
            self.player.is_second() and 
            self.player.is_experimental() and 
            self.player.is_halftime() )


    def before_next_page(self):
        terminate = self.player.terminate_interaction
        self.player.get_fp().terminate_interaction = terminate
        if terminate:
            self.player.terminate()

class FB_RTF(Page):
    template_name = "SoMiPu/Reason_To_Finish_SecondPlayer.html"
    form_model = models.Player

    def get_form_fields(self):
        return ['reason_to_finish']

    def is_displayed(self):
        self.player.check_consistency()
        return (
            self.player.is_second() and 
            self.player.is_experimental() and 
            self.player.is_halftime() and
            self.player.has_terminated() )


class Wait_Trials_SP(SoMiPu_Wait):
    def is_displayed(self):
        return self.player.has_not_terminated()


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
        self.player.check_consistency()
        return (
            self.player.is_first() and 
            self.player.is_experimental() and
            (self.player.before_halftime() or self.player.has_not_terminated()) )


class CB1_AP (Page):
    template_name = "SoMiPu/Checkbox1_AllPlayers.html"
    form_model = models.Player
    
    def get_form_fields(self):
        return ['overall_fb_cb1', 'overall_fb_cb2','overall_fb_cb3', 'overall_fb_cb4','overall_fb_cb5', 'overall_fb_cb6']
    
    def is_displayed(self):
        self.player.check_consistency()
        return self.player.is_fulltime()

class CB2_AP(Page):
    template_name = "SoMiPu/Checkbox2_AllPlayers.html"
    form_model = models.Player
    form_fields = ['overall_fb_tx1', 'overall_fb_tx2', 'overall_fb_tx3']

    def vars_for_template(self):
        return {"role": self.player.role()}

    def is_displayed(self):
        return self.player.is_fulltime()

class A_PersonalData(Page):
    form_model = models.Player
    def get_form_fields(self):
        return ['participant_sex', 'participant_age', 'participant_lang_skills']

    def is_displayed(self):
        return self.player.is_fulltime()

class LastPage (Page):
    def vars_for_template(self):
        # Additional 2 Euro if this page is reached without termination
        if self.player.has_not_terminated():
            self.player.payoff = c(2)
        return { 
            "payoff":           self.participant.payoff,
            "condition":        self.player.condition()
         }

    def is_displayed(self):
        return self.player.is_fulltime()



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
