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
        self.player.check_consistency()
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
                'firstChoice', 'choice' ]

        if self.player.is_second():
            ret.append("secondChoice")
            ret.append("fb_ff")
            if self.player.is_experimental():
                ret.append("fb_s")
            if self.player.repeat_name( self.round_number ) == "b":
                ret.append("fb_fb")

        return ret


    def vars_for_template(self):
        ret = super(SoMiPu_MainTrial, self).vars_for_template()

        trial  = self.player.get_trial(self.round_number)
        stid   = trial["Trial"]
        tidx   = self.player.trial_idx( self.round_number )
        repeat = self.player.repeat_name( self.round_number )
        item   = trial["Item"]
        vr1    = trial["Variety1"]
        vr2    = trial["Variety2"]

        subtrial  = self.player.get_subtrial(self.round_number)
        itemOrder = self.player.get_itemOrder(self.round_number, subtrial)

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

        ret["ExclusionaryThreat"] = (repeat == "b")

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

class WaitPe(WaitPage):
    template_name = "SoMiPu/WaitPage.html"

    def vars_for_template(self):
        return {'body_text': "Sobald die andere Person ihre Wahl getroffen hat, geht es weiter.",
                'title_text': "Bitte warten Sie ..."}

    def is_displayed(self):
        if self.session.vars['treatment'] == 'control':
            return False

        if self.player.__getattribute__('terminate_interaction') is True:
            return False
        else:
            return True

class WaitPc(WaitPage):
    pass

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
        self.player.check_consistency()

        return {
            "condition" : self.player.condition(),
            "role"      : self.player.role()
        }

    def is_displayed(self):
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

    def is_displayed(self):
        return self.round_number == 1



class Trials_FP (SoMiPu_MainTrial):
    template_name = "SoMiPu/Trials_FirstPlayer.html"
    form_model = models.Player

    def is_displayed(self):
        return self.player.is_first()


class Wait_Trials_FP(SoMiPu_Wait):
    pass


class Trials_SP (SoMiPu_MainTrial):
    template_name = "SoMiPu/Trials_SecondPlayer.html"
    form_model = models.Player

    def is_displayed(self):
        return self.player.is_second()


class Wait_Trials_SP(SoMiPu_Wait):
    pass


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
        ret["feedback"] = True

        return ret

    def is_displayed(self):
        return self.player.is_first() and self.player.is_experimental()



class E2_Resolution(Page):
    pass







class T12_EFPCI (Page):
    template_name = "SoMiPu/Experimental_Trials_FirstPlayer.html"

    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(5, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(5, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '12',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "block"
        }

    def is_displayed(self):
        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class T12_EFP(Page):
    template_name = "SoMiPu/Experimental_Trials_FirstPlayer.html"

    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(5, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(5, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '12',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "block",
        }

    def is_displayed(self):
        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T13_EFP(Page):
    template_name = "SoMiPu/Experimental_Trials_FirstPlayer.html"

    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(6, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(6, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '13',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "none"
        }


    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T14_EFP(Page):
    template_name = "SoMiPu/Experimental_Trials_FirstPlayer.html"

    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(6, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(6, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '14',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "none"
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
        and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T15_EFP(Page):
    template_name = "SoMiPu/Experimental_Trials_FirstPlayer.html"

    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(7, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(7, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '15',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "none"
        }


    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T16_EFP(Page):
    template_name = "SoMiPu/Experimental_Trials_FirstPlayer.html"

    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(7, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(7, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '16',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "none"
        }


    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class T17_EFP(Page):
    template_name = "SoMiPu/Experimental_Trials_FirstPlayer.html"

    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(8, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(8, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '17',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "none"
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T18_EFP(Page):
    template_name = "SoMiPu/Experimental_Trials_FirstPlayer.html"

    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(8, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(8, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '18',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "none"
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T19_EFP(Page):
    template_name = "SoMiPu/Experimental_Trials_FirstPlayer.html"

    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(9, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(9, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '19',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "none"
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T20_EFP(Page):
    template_name = "SoMiPu/Experimental_Trials_FirstPlayer.html"

    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(9, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(9, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '20',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "none"
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T21_EFP(Page):
    template_name = "SoMiPu/Experimental_Trials_FirstPlayer.html"

    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(10, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(10, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '21',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "none"
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T22_EFP(Page):
    template_name = "SoMiPu/Experimental_Trials_FirstPlayer.html"

    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(10, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(10, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '22',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "none"
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class T23_EFP(Page):

    template_name = "SoMiPu/Experimental_Trials_FirstPlayer.html"

    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(11, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(11, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '23',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "none"
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T24_EFP(Page):
    template_name = "SoMiPu/Experimental_Trials_FirstPlayer.html"

    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(11, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(11, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '24',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "none"
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False



class T12_ExTh(Page):
    template_name = "SoMiPu/Trial12_ExclusionaryThreat_SecondPlayer.html"
    form_model = models.Player

    def get_form_fields(self):

        fields = ['terminate_interaction']

        return fields

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

    def before_next_page(self):
        terminate = self.player.__getattribute__('terminate_interaction')
        firstChooser = self.group.get_player_by_role('FirstChooser')
        firstChooser.__setattr__('terminate_interaction', terminate)

        if terminate is True:
            self.player.__setattr__('payoff', c(2))
            firstChooser.__setattr__('payoff', c(2))
        else:
            self.player.__setattr__('payoff', c(4))
            firstChooser.__setattr__('payoff', c(4))

class T13_ESP(Page):
        template_name = "SoMiPu/Experimental_Trial1_SecondPlayer.html"
        form_model = models.Player

        firstChoice = ""
        choiceList = [
            {"width": 100, "columnWidth": 210},
            {"width": 100, "columnWidth": 210},
            {"width": 100, "columnWidth": 210}
        ]

        def get_form_fields(self):

            if self.player.role() == "SecondChooser":
                firstChooser = self.group.get_player_by_role('FirstChooser')
                trials = firstChooser.participant.vars['trials']
            else:
                trials = self.participant.vars['trials']

            trialObjects = trials.getTrial(6, 0)
            fields = ['secondChoice', trialObjects[0].name + '_fb_s', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
            fields.append(trialObjects[0].name)
            return fields

        def vars_for_template(self):

            print("vars_for_template")

            if self.player.role() == "SecondChooser":
                firstChooser = self.group.get_player_by_role('FirstChooser')
                trials = firstChooser.participant.vars['trials']
                self.firstChoice = firstChooser.__getattribute__('firstChoice')
            else:
                trials = self.participant.vars['trials']
                self.firstChoice = self.player.__getattribute__('firstChoice')

            trialObjects = trials.getTrial(6, 0)

            self.choiceList[0]['id'] = trialObjects[0].id
            self.choiceList[0]['name'] = trialObjects[0].name
            self.choiceList[0]['value'] = trialObjects[0].value
            self.choiceList[0]['url'] = trialObjects[0].url
            self.choiceList[1]['id'] = trialObjects[1].id
            self.choiceList[1]['name'] = trialObjects[1].name
            self.choiceList[1]['value'] = trialObjects[1].value
            self.choiceList[1]['url'] = trialObjects[1].url
            self.choiceList[2]['id'] = trialObjects[2].id
            self.choiceList[2]['name'] = trialObjects[2].name
            self.choiceList[2]['value'] = trialObjects[2].value
            self.choiceList[2]['url'] = trialObjects[2].url

            # print(self.player.__dict__trial_1a)
            # print("form_fields:" + self.form_fields[0])

            self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

            return {
                'choiceList': self.choiceList,
                'firstChoice': self.firstChoice,
                'smilyListWidth': self.smilyListWidth,
                'smilyImgUrl': self.smilyImgUrl,
                'smilyList': self.smilyList,
                'trial': trialObjects[0].name,
                'sequence': '13'
            }

        smilyListWidth = 500
        smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"

        smilyList = [
            {"id": "cbs1"},
            {"id": "cbs2"},
            {"id": "cbs3"},
            {"id": "cbs4"},
            {"id": "cbs5"}
        ]

        def is_displayed(self):
            if self.player.__getattribute__('terminate_interaction') is True:
                return False

            if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                    and self.player.role() == 'SecondChooser':
                return True
            else:
                return False


class T14_ESP(Page):
    template_name = "SoMiPu/Experimental_Trial2_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(6, 1)
        fields = ['secondChoice', trialObjects[0].name + '_fb_s', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_fb_fb', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(6, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'smilyListWidth': self.smilyListWidth,
            'smilyImgUrl': self.smilyImgUrl,
            'smilyList': self.smilyList,
            'ExclusionaryThreat': 'none',
            'trial': trialObjects[0].name,
            'sequence': '14'
        }

    smilyListWidth = 500
    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T15_ESP(Page):
        template_name = "SoMiPu/Experimental_Trial1_SecondPlayer.html"
        form_model = models.Player

        firstChoice = ""
        choiceList = [
            {"width": 100, "columnWidth": 210},
            {"width": 100, "columnWidth": 210},
            {"width": 100, "columnWidth": 210}
        ]

        def get_form_fields(self):

            if self.player.role() == "SecondChooser":
                firstChooser = self.group.get_player_by_role('FirstChooser')
                trials = firstChooser.participant.vars['trials']
            else:
                trials = self.participant.vars['trials']

            trialObjects = trials.getTrial(7, 0)
            fields = ['secondChoice', trialObjects[0].name + '_fb_s', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
            fields.append(trialObjects[0].name)
            return fields

        def vars_for_template(self):

            print("vars_for_template")

            if self.player.role() == "SecondChooser":
                firstChooser = self.group.get_player_by_role('FirstChooser')
                trials = firstChooser.participant.vars['trials']
                self.firstChoice = firstChooser.__getattribute__('firstChoice')
            else:
                trials = self.participant.vars['trials']
                self.firstChoice = self.player.__getattribute__('firstChoice')

            trialObjects = trials.getTrial(7, 0)

            self.choiceList[0]['id'] = trialObjects[0].id
            self.choiceList[0]['name'] = trialObjects[0].name
            self.choiceList[0]['value'] = trialObjects[0].value
            self.choiceList[0]['url'] = trialObjects[0].url
            self.choiceList[1]['id'] = trialObjects[1].id
            self.choiceList[1]['name'] = trialObjects[1].name
            self.choiceList[1]['value'] = trialObjects[1].value
            self.choiceList[1]['url'] = trialObjects[1].url
            self.choiceList[2]['id'] = trialObjects[2].id
            self.choiceList[2]['name'] = trialObjects[2].name
            self.choiceList[2]['value'] = trialObjects[2].value
            self.choiceList[2]['url'] = trialObjects[2].url

            # print(self.player.__dict__trial_1a)
            # print("form_fields:" + self.form_fields[0])

            self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

            return {
                'choiceList': self.choiceList,
                'firstChoice': self.firstChoice,
                'smilyListWidth': self.smilyListWidth,
                'smilyImgUrl': self.smilyImgUrl,
                'smilyList': self.smilyList,
                'trial': trialObjects[0].name,
                'sequence': '15'
            }

        smilyListWidth = 500
        smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"

        smilyList = [
            {"id": "cbs1"},
            {"id": "cbs2"},
            {"id": "cbs3"},
            {"id": "cbs4"},
            {"id": "cbs5"}
        ]

        def is_displayed(self):
            if self.player.__getattribute__('terminate_interaction') is True:
                return False

            if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                    and self.player.role() == 'SecondChooser':
                return True
            else:
                return False


class T16_ESP(Page):
    template_name = "SoMiPu/Experimental_Trial2_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(7, 1)
        fields = ['secondChoice', trialObjects[0].name + '_fb_s', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_fb_fb', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(7, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'smilyListWidth': self.smilyListWidth,
            'smilyImgUrl': self.smilyImgUrl,
            'smilyList': self.smilyList,
            'ExclusionaryThreat': 'none',
            'trial': trialObjects[0].name,
            'sequence': '16'
        }

    smilyListWidth = 500
    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T17_ESP(Page):
        template_name = "SoMiPu/Experimental_Trial1_SecondPlayer.html"
        form_model = models.Player

        firstChoice = ""
        choiceList = [
            {"width": 100, "columnWidth": 210},
            {"width": 100, "columnWidth": 210},
            {"width": 100, "columnWidth": 210}
        ]

        def get_form_fields(self):

            if self.player.role() == "SecondChooser":
                firstChooser = self.group.get_player_by_role('FirstChooser')
                trials = firstChooser.participant.vars['trials']
            else:
                trials = self.participant.vars['trials']

            trialObjects = trials.getTrial(8, 0)
            fields = ['secondChoice', trialObjects[0].name + '_fb_s', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
            fields.append(trialObjects[0].name)
            return fields

        def vars_for_template(self):

            print("vars_for_template")

            if self.player.role() == "SecondChooser":
                firstChooser = self.group.get_player_by_role('FirstChooser')
                trials = firstChooser.participant.vars['trials']
                self.firstChoice = firstChooser.__getattribute__('firstChoice')
            else:
                trials = self.participant.vars['trials']
                self.firstChoice = self.player.__getattribute__('firstChoice')

            trialObjects = trials.getTrial(8, 0)

            self.choiceList[0]['id'] = trialObjects[0].id
            self.choiceList[0]['name'] = trialObjects[0].name
            self.choiceList[0]['value'] = trialObjects[0].value
            self.choiceList[0]['url'] = trialObjects[0].url
            self.choiceList[1]['id'] = trialObjects[1].id
            self.choiceList[1]['name'] = trialObjects[1].name
            self.choiceList[1]['value'] = trialObjects[1].value
            self.choiceList[1]['url'] = trialObjects[1].url
            self.choiceList[2]['id'] = trialObjects[2].id
            self.choiceList[2]['name'] = trialObjects[2].name
            self.choiceList[2]['value'] = trialObjects[2].value
            self.choiceList[2]['url'] = trialObjects[2].url

            # print(self.player.__dict__trial_1a)
            # print("form_fields:" + self.form_fields[0])

            self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

            return {
                'choiceList': self.choiceList,
                'firstChoice': self.firstChoice,
                'smilyListWidth': self.smilyListWidth,
                'smilyImgUrl': self.smilyImgUrl,
                'smilyList': self.smilyList,
                'trial': trialObjects[0].name,
                'sequence': '17'
            }

        smilyListWidth = 500
        smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"

        smilyList = [
            {"id": "cbs1"},
            {"id": "cbs2"},
            {"id": "cbs3"},
            {"id": "cbs4"},
            {"id": "cbs5"}
        ]

        def is_displayed(self):
            if self.player.__getattribute__('terminate_interaction') is True:
                return False

            if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                    and self.player.role() == 'SecondChooser':
                return True
            else:
                return False


class T18_ESP(Page):
    template_name = "SoMiPu/Experimental_Trial2_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(8, 1)
        fields = ['secondChoice', trialObjects[0].name + '_fb_s', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_fb_fb', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(8, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'smilyListWidth': self.smilyListWidth,
            'smilyImgUrl': self.smilyImgUrl,
            'smilyList': self.smilyList,
            'ExclusionaryThreat': 'none',
            'trial': trialObjects[0].name,
            'sequence': '18'
        }

    smilyListWidth = 500
    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T19_ESP(Page):
        template_name = "SoMiPu/Experimental_Trial1_SecondPlayer.html"
        form_model = models.Player

        firstChoice = ""
        choiceList = [
            {"width": 100, "columnWidth": 210},
            {"width": 100, "columnWidth": 210},
            {"width": 100, "columnWidth": 210}
        ]

        def get_form_fields(self):

            if self.player.role() == "SecondChooser":
                firstChooser = self.group.get_player_by_role('FirstChooser')
                trials = firstChooser.participant.vars['trials']
            else:
                trials = self.participant.vars['trials']

            trialObjects = trials.getTrial(9, 0)
            fields = ['secondChoice', trialObjects[0].name + '_fb_s',trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
            fields.append(trialObjects[0].name)
            return fields

        def vars_for_template(self):

            print("vars_for_template")

            if self.player.role() == "SecondChooser":
                firstChooser = self.group.get_player_by_role('FirstChooser')
                trials = firstChooser.participant.vars['trials']
                self.firstChoice = firstChooser.__getattribute__('firstChoice')
            else:
                trials = self.participant.vars['trials']
                self.firstChoice = self.player.__getattribute__('firstChoice')

            trialObjects = trials.getTrial(9, 0)

            self.choiceList[0]['id'] = trialObjects[0].id
            self.choiceList[0]['name'] = trialObjects[0].name
            self.choiceList[0]['value'] = trialObjects[0].value
            self.choiceList[0]['url'] = trialObjects[0].url
            self.choiceList[1]['id'] = trialObjects[1].id
            self.choiceList[1]['name'] = trialObjects[1].name
            self.choiceList[1]['value'] = trialObjects[1].value
            self.choiceList[1]['url'] = trialObjects[1].url
            self.choiceList[2]['id'] = trialObjects[2].id
            self.choiceList[2]['name'] = trialObjects[2].name
            self.choiceList[2]['value'] = trialObjects[2].value
            self.choiceList[2]['url'] = trialObjects[2].url

            # print(self.player.__dict__trial_1a)
            # print("form_fields:" + self.form_fields[0])

            self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

            return {
                'choiceList': self.choiceList,
                'firstChoice': self.firstChoice,
                'smilyListWidth': self.smilyListWidth,
                'smilyImgUrl': self.smilyImgUrl,
                'smilyList': self.smilyList,
                'trial': trialObjects[0].name,
                'sequence': '19'
            }

        smilyListWidth = 500
        smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"

        smilyList = [
            {"id": "cbs1"},
            {"id": "cbs2"},
            {"id": "cbs3"},
            {"id": "cbs4"},
            {"id": "cbs5"}
        ]

        def is_displayed(self):
            if self.player.__getattribute__('terminate_interaction') is True:
                return False

            if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                    and self.player.role() == 'SecondChooser':
                return True
            else:
                return False


class T20_ESP(Page):
    template_name = "SoMiPu/Experimental_Trial2_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(9, 1)
        fields = ['secondChoice', trialObjects[0].name + '_fb_s',trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_fb_fb', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(9, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'smilyListWidth': self.smilyListWidth,
            'smilyImgUrl': self.smilyImgUrl,
            'smilyList': self.smilyList,
            'ExclusionaryThreat': 'none',
            'trial': trialObjects[0].name,
            'sequence': '20'
        }

    smilyListWidth = 500
    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T21_ESP(Page):
        template_name = "SoMiPu/Experimental_Trial1_SecondPlayer.html"
        form_model = models.Player

        firstChoice = ""
        choiceList = [
            {"width": 100, "columnWidth": 210},
            {"width": 100, "columnWidth": 210},
            {"width": 100, "columnWidth": 210}
        ]

        def get_form_fields(self):

            if self.player.role() == "SecondChooser":
                firstChooser = self.group.get_player_by_role('FirstChooser')
                trials = firstChooser.participant.vars['trials']
            else:
                trials = self.participant.vars['trials']

            trialObjects = trials.getTrial(10, 0)
            fields = ['secondChoice', trialObjects[0].name + '_fb_s',trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
            fields.append(trialObjects[0].name)
            return fields

        def vars_for_template(self):

            print("vars_for_template")

            if self.player.role() == "SecondChooser":
                firstChooser = self.group.get_player_by_role('FirstChooser')
                trials = firstChooser.participant.vars['trials']
                self.firstChoice = firstChooser.__getattribute__('firstChoice')
            else:
                trials = self.participant.vars['trials']
                self.firstChoice = self.player.__getattribute__('firstChoice')

            trialObjects = trials.getTrial(10, 0)

            self.choiceList[0]['id'] = trialObjects[0].id
            self.choiceList[0]['name'] = trialObjects[0].name
            self.choiceList[0]['value'] = trialObjects[0].value
            self.choiceList[0]['url'] = trialObjects[0].url
            self.choiceList[1]['id'] = trialObjects[1].id
            self.choiceList[1]['name'] = trialObjects[1].name
            self.choiceList[1]['value'] = trialObjects[1].value
            self.choiceList[1]['url'] = trialObjects[1].url
            self.choiceList[2]['id'] = trialObjects[2].id
            self.choiceList[2]['name'] = trialObjects[2].name
            self.choiceList[2]['value'] = trialObjects[2].value
            self.choiceList[2]['url'] = trialObjects[2].url

            # print(self.player.__dict__trial_1a)
            # print("form_fields:" + self.form_fields[0])

            self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

            return {
                'choiceList': self.choiceList,
                'firstChoice': self.firstChoice,
                'smilyListWidth': self.smilyListWidth,
                'smilyImgUrl': self.smilyImgUrl,
                'smilyList': self.smilyList,
                'trial': trialObjects[0].name,
                'sequence': '21'
            }

        smilyListWidth = 500
        smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"

        smilyList = [
            {"id": "cbs1"},
            {"id": "cbs2"},
            {"id": "cbs3"},
            {"id": "cbs4"},
            {"id": "cbs5"}
        ]

        def is_displayed(self):
            if self.player.__getattribute__('terminate_interaction') is True:
                return False

            if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                    and self.player.role() == 'SecondChooser':
                return True
            else:
                return False


class T22_ESP(Page):
    template_name = "SoMiPu/Experimental_Trial2_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(10, 1)
        fields = ['secondChoice', trialObjects[0].name + '_fb_s', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_fb_fb', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(10, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'smilyListWidth': self.smilyListWidth,
            'smilyImgUrl': self.smilyImgUrl,
            'smilyList': self.smilyList,
            'ExclusionaryThreat': 'none',
            'trial': trialObjects[0].name,
            'sequence': '22'
        }

    smilyListWidth = 500
    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T23_ESP(Page):
        template_name = "SoMiPu/Experimental_Trial1_SecondPlayer.html"
        form_model = models.Player

        firstChoice = ""
        choiceList = [
            {"width": 100, "columnWidth": 210},
            {"width": 100, "columnWidth": 210},
            {"width": 100, "columnWidth": 210}
        ]

        def get_form_fields(self):

            if self.player.role() == "SecondChooser":
                firstChooser = self.group.get_player_by_role('FirstChooser')
                trials = firstChooser.participant.vars['trials']
            else:
                trials = self.participant.vars['trials']

            trialObjects = trials.getTrial(11, 0)
            fields = ['secondChoice', trialObjects[0].name + '_fb_s',trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
            fields.append(trialObjects[0].name)
            return fields

        def vars_for_template(self):

            print("vars_for_template")

            if self.player.role() == "SecondChooser":
                firstChooser = self.group.get_player_by_role('FirstChooser')
                trials = firstChooser.participant.vars['trials']
                self.firstChoice = firstChooser.__getattribute__('firstChoice')
            else:
                trials = self.participant.vars['trials']
                self.firstChoice = self.player.__getattribute__('firstChoice')

            trialObjects = trials.getTrial(11, 0)

            self.choiceList[0]['id'] = trialObjects[0].id
            self.choiceList[0]['name'] = trialObjects[0].name
            self.choiceList[0]['value'] = trialObjects[0].value
            self.choiceList[0]['url'] = trialObjects[0].url
            self.choiceList[1]['id'] = trialObjects[1].id
            self.choiceList[1]['name'] = trialObjects[1].name
            self.choiceList[1]['value'] = trialObjects[1].value
            self.choiceList[1]['url'] = trialObjects[1].url
            self.choiceList[2]['id'] = trialObjects[2].id
            self.choiceList[2]['name'] = trialObjects[2].name
            self.choiceList[2]['value'] = trialObjects[2].value
            self.choiceList[2]['url'] = trialObjects[2].url

            # print(self.player.__dict__trial_1a)
            # print("form_fields:" + self.form_fields[0])

            self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
            self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

            return {
                'choiceList': self.choiceList,
                'firstChoice': self.firstChoice,
                'smilyListWidth': self.smilyListWidth,
                'smilyImgUrl': self.smilyImgUrl,
                'smilyList': self.smilyList,
                'trial': trialObjects[0].name,
                'sequence': '23'
            }

        smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"
        smilyListWidth = "500"

        smilyList = [
            {"id": "cbs1"},
            {"id": "cbs2"},
            {"id": "cbs3"},
            {"id": "cbs4"},
            {"id": "cbs5"}
        ]
        def is_displayed(self):
            if self.player.__getattribute__('terminate_interaction') is True:
                return False

            if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                    and self.player.role() == 'SecondChooser':
                return True
            else:
                return False


class T24_ESP(Page):
    template_name = "SoMiPu/Experimental_Trial2_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(11, 1)
        fields = ['secondChoice', trialObjects[0].name + '_fb_s',trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_fb_fb', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(11, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'smilyListWidth': self.smilyListWidth,
            'smilyImgUrl': self.smilyImgUrl,
            'smilyList': self.smilyList,
            'ExclusionaryThreat': 'none',
            'trial': trialObjects[0].name,
            'sequence': '24'
        }

    smilyListWidth = 500
    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"

    smilyList = [
        {
            "id": "s0",
            "name": "s0",
        },
        {
            "id": "s1",
            "name": "s1",
        },
        {
            "id": "s2",
            "name": "s2",
        },
        {
            "id": "s3",
            "name": "s3",
        },
        {
            "id": "s4",
            "name": "s4",
        }
    ]

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False


class T13_CFP(Page):
    template_name = "SoMiPu/Control_Trials_FirstPlayer.html"
    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(6, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(6, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '13',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T13_CSP(Page):
    template_name = "SoMiPu/Control_Trial1_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(6, 0)
        fields = ['secondChoice', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(6, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])
        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'trial': trialObjects[0].name,
            'sequence': '13'
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T14_CFP(Page):
    template_name = "SoMiPu/Control_Trials_FirstPlayer.html"
    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(6, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(6, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '14',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T14_CSP(Page):
    template_name = "SoMiPu/Control_Trial2_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(6, 1)
        fields = ['secondChoice', trialObjects[0].name + '_fb_fb', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(6, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])
        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'trial': trialObjects[0].name,
            'sequence': '14'
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T15_CFP(Page):
    template_name = "SoMiPu/Control_Trials_FirstPlayer.html"
    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(7, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(7, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '15',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T15_CSP(Page):
    template_name = "SoMiPu/Control_Trial1_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(7, 0)
        fields = ['secondChoice', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(7, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])
        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'trial': trialObjects[0].name,
            'sequence': '15'
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T16_CFP(Page):
    template_name = "SoMiPu/Control_Trials_FirstPlayer.html"
    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(7, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(7, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '16',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T16_CSP(Page):
    template_name = "SoMiPu/Control_Trial2_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(7, 1)
        fields = ['secondChoice', trialObjects[0].name + '_fb_fb', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(7, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])
        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'trial': trialObjects[0].name,
            'sequence': '16'
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T17_CFP(Page):
    template_name = "SoMiPu/Control_Trials_FirstPlayer.html"
    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(8, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(8, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '17',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T17_CSP(Page):
    template_name = "SoMiPu/Control_Trial1_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(8, 0)
        fields = ['secondChoice', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(8, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])
        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'trial': trialObjects[0].name,
            'sequence': '17'
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T18_CFP(Page):
    template_name = "SoMiPu/Control_Trials_FirstPlayer.html"
    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(8, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(8, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '18',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T18_CSP(Page):
    template_name = "SoMiPu/Control_Trial2_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(8, 1)
        fields = ['secondChoice', trialObjects[0].name + '_fb_fb', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(8, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])
        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'trial': trialObjects[0].name,
            'sequence': '18'
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T19_CFP(Page):
    template_name = "SoMiPu/Control_Trials_FirstPlayer.html"
    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(9, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(9, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '19',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T19_CSP(Page):
    template_name = "SoMiPu/Control_Trial1_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(9, 0)
        fields = ['secondChoice', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(9, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])
        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'trial': trialObjects[0].name,
            'sequence': '19'
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T20_CFP(Page):
    template_name = "SoMiPu/Control_Trials_FirstPlayer.html"
    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(9, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(9, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '20',
            'trial': trialObjects[0].name
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T20_CSP(Page):
    template_name = "SoMiPu/Control_Trial2_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(9, 1)
        fields = ['secondChoice', trialObjects[0].name + '_fb_fb', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(9, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])
        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'trial': trialObjects[0].name,
            'sequence': '20'
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T21_CFP(Page):
    template_name = "SoMiPu/Control_Trials_FirstPlayer.html"
    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(10, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']
        trialObjects = trials.getTrial(10, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '21',
            'trial': trialObjects[0].name
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T21_CSP(Page):
    template_name = "SoMiPu/Control_Trial1_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(10, 0)
        fields = ['secondChoice', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(10, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])
        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'trial': trialObjects[0].name,
            'sequence': '21'
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T22_CFP(Page):
    template_name = "SoMiPu/Control_Trials_FirstPlayer.html"
    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(10, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']
        trialObjects = trials.getTrial(10, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '22',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T22_CSP(Page):
    template_name = "SoMiPu/Control_Trial2_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(10, 1)
        fields = ['secondChoice', trialObjects[0].name + '_fb_fb', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(10, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])
        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'trial': trialObjects[0].name,
            'sequence': '22',
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T23_CFP(Page):
    template_name = "SoMiPu/Control_Trials_FirstPlayer.html"
    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(11, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(11, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '23',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T23_CSP(Page):
    template_name = "SoMiPu/Control_Trial1_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(11, 0)
        fields = ['secondChoice', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(11, 0)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])
        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'trial': trialObjects[0].name,
            'sequence': '23'
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T24_CFP(Page):
    template_name = "SoMiPu/Control_Trials_FirstPlayer.html"
    form_model = models.Player
    # form_fields = ['trial_1a']

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(11, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(11, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'sequence': '24',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

    def before_next_page(self):
        self.player.__setattr__('payoff', c(4))


class T24_CSP(Page):
    template_name = "SoMiPu/Control_Trial2_SecondPlayer.html"
    form_model = models.Player

    firstChoice = ""
    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    def get_form_fields(self):

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(11, 1)
        fields = ['secondChoice', trialObjects[0].name + '_fb_fb', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        print("vars_for_template")

        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
        else:
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')

        trialObjects = trials.getTrial(11, 1)

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])
        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'trial': trialObjects[0].name,
            'sequence': '24'
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

    def before_next_page(self):
        self.player.__setattr__('payoff', c(4))

class E2_A(Page):
    template_name = "SoMiPu/E2_Assess.html"

    smilyListWidth = 500
    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    def vars_for_template(self):
        return {
            'smilyListWidth': self.smilyListWidth,
            'smilyImgUrl': self.smilyImgUrl,
            'smilyList': self.smilyList,
            }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False


class A_PersonalData(Page):
    form_model = models.Player
    def get_form_fields(self):
        return ['participant_sex', 'participant_age', 'participant_lang_skills']



class CB1_AP (Page):
    template_name = "SoMiPu/Checkbox1_AllPlayers.html"
    form_model = models.Player
    def get_form_fields(self):
        return ['overall_fb_cb1', 'overall_fb_cb2','overall_fb_cb3', 'overall_fb_cb4','overall_fb_cb5', 'overall_fb_cb6']
    pass


class CB2_FP(Page):
    template_name = "SoMiPu/Checkbox2_FirstPlayers.html"
    form_model = models.Player

    def get_form_fields(self):
        return ['overall_fb_tx1', 'overall_fb_tx2', 'overall_fb_tx3']

    def is_displayed(self):

        if self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class CB2_SP(Page):
    template_name = "SoMiPu/Checkbox2_SecondPlayers.html"
    form_model = models.Player
    def get_form_fields(self):
        return ['overall_fb_tx1', 'overall_fb_tx2']
    
    def is_displayed(self):

        if self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class E_OFB_SP_HT(Page):
    template_name = "SoMiPu/Overall_Feedback_SecondPlayer_Half_Time.html"
    form_model = models.Player
    smilyListWidth = 500
    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    def get_form_fields(self):

        return ['overall_fb_s_ht', 'overall_fb_ff_ht']

    def vars_for_template(self):

        self.smilyList[0]['name'] = "overall_fb_s_ht"
        self.smilyList[1]['name'] = "overall_fb_s_ht"
        self.smilyList[2]['name'] = "overall_fb_s_ht"
        self.smilyList[3]['name'] = "overall_fb_s_ht"
        self.smilyList[4]['name'] = "overall_fb_s_ht"

        return {
            'smilyListWidth': self.smilyListWidth,
            'smilyImgUrl': self.smilyImgUrl,
            'smilyList': self.smilyList
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False


class C_OFB_SP_HT(Page):
    template_name = "SoMiPu/Overall_Feedback_SecondPlayer_Half_Time.html"
    form_model = models.Player
    smilyListWidth = 500
    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    def get_form_fields(self):

        return ['overall_fb_s_ht', 'overall_fb_ff_ht']

    def vars_for_template(self):

        self.smilyList[0]['name'] = "overall_fb_s_ht"
        self.smilyList[1]['name'] = "overall_fb_s_ht"
        self.smilyList[2]['name'] = "overall_fb_s_ht"
        self.smilyList[3]['name'] = "overall_fb_s_ht"
        self.smilyList[4]['name'] = "overall_fb_s_ht"

        return {
            'smilyListWidth': self.smilyListWidth,
            'smilyImgUrl': self.smilyImgUrl,
            'smilyList': self.smilyList
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False


class OFB_SP(Page):
    template_name = "SoMiPu/Overall_Feedback_SecondPlayer.html"
    form_model = models.Player
    smilyListWidth = 500
    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    def get_form_fields(self):

        return ['overall_fb_s', 'overall_fb_ff']

    def vars_for_template(self):

        self.smilyList[0]['name'] = "overall_fb_s"
        self.smilyList[1]['name'] = "overall_fb_s"
        self.smilyList[2]['name'] = "overall_fb_s"
        self.smilyList[3]['name'] = "overall_fb_s"
        self.smilyList[4]['name'] = "overall_fb_s"

        return {
            'smilyListWidth': self.smilyListWidth,
            'smilyImgUrl': self.smilyImgUrl,
            'smilyList': self.smilyList
        }

    def is_displayed(self):

        if self.player.role() == 'FirstChooser' or self.player.__getattribute__('terminate_interaction') is True:
            return False
        else:
            return True


class FB_RTF(Page):
    template_name = "SoMiPu/Reason_To_Finish_SecondPlayer.html"
    form_model = models.Player

    def get_form_fields(self):

        return ['reason_to_finish']

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser' and self.player.__getattribute__('terminate_interaction') is True:
            return True
        else:
            return False





class E1_T12CI(Page):
    form_model = models.Player
    template_name = "SoMiPu/Feedback12_ContinueInteraction_FirstPlayer.html"

    firstChoice = ""
    secondChoice = ""

    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"
    smilyListWidth = "500"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    smilyFeedback = ""

    def get_form_fields(self):
        return []

    def vars_for_template(self):
        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
            self.secondChoice = self.player.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(5, 1)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(5, 1)
            self.smilyFeedback = secondChooser.__getattribute__(trialObjects[0].name + "_fb_s")

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            "choiceList": self.choiceList,
            "smilyList": self.smilyList,
            "smilyImgUrl": self.smilyImgUrl,
            "smilyListWidth": self.smilyListWidth,
            "firstChoice": self.firstChoice,
            "secondChoice": self.secondChoice,
            "smilyFeedback": self.smilyFeedback
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class E1_T12FI1(Page):
    form_model = models.Player
    template_name = "SoMiPu/Feedback12_FinishInteraction_FirstPlayer1.html"

    firstChoice = ""
    secondChoice = ""

    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"
    smilyListWidth = "500"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    smilyFeedback = ""

    def get_form_fields(self):
        return []

    def vars_for_template(self):
        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
            self.secondChoice = self.player.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(5, 1)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(5, 1)
            self.smilyFeedback = secondChooser.__getattribute__(trialObjects[0].name + "_fb_s")

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            "choiceList": self.choiceList,
            "smilyList": self.smilyList,
            "smilyImgUrl": self.smilyImgUrl,
            "smilyListWidth": self.smilyListWidth,
            "firstChoice": self.firstChoice,
            "secondChoice": self.secondChoice,
            "smilyFeedback": self.smilyFeedback
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is False:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class E1_T12FI2(Page):
    template_name = "SoMiPu/Feedback12_FinishInteraction_FirstPlayer2.html"

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is False:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class FB13(Page):
    form_model = models.Player
    template_name = "SoMiPu/Experimental_Feedback_FirstPlayer.html"
    firstChoice = ""
    secondChoice = ""

    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"
    smilyListWidth = "500"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    smilyFeedback = ""

    def get_form_fields(self):
        return []

    def vars_for_template(self):
        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
            self.secondChoice = self.player.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(6, 0)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(6, 0)
            self.smilyFeedback = secondChooser.__getattribute__(trialObjects[0].name + "_fb_s")

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            "choiceList": self.choiceList,
            "smilyList": self.smilyList,
            "smilyImgUrl": self.smilyImgUrl,
            "smilyListWidth": self.smilyListWidth,
            "firstChoice": self.firstChoice,
            "secondChoice": self.secondChoice,
            "smilyFeedback": self.smilyFeedback,
            "ExclusionaryThreat": 'none'
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class FB14(Page):
    form_model = models.Player
    template_name = "SoMiPu/Experimental_Feedback_FirstPlayer.html"

    firstChoice = ""
    secondChoice = ""

    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"
    smilyListWidth = "500"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    smilyFeedback = ""

    def get_form_fields(self):
        return []

    def vars_for_template(self):
        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
            self.secondChoice = self.player.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(6, 1)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(6, 1)
            self.smilyFeedback = secondChooser.__getattribute__(trialObjects[0].name + "_fb_s")

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            "choiceList": self.choiceList,
            "smilyList": self.smilyList,
            "smilyImgUrl": self.smilyImgUrl,
            "smilyListWidth": self.smilyListWidth,
            "firstChoice": self.firstChoice,
            "secondChoice": self.secondChoice,
            "smilyFeedback": self.smilyFeedback,
            "ExclusionaryThreat": 'none'
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class FB15(Page):
    form_model = models.Player
    template_name = "SoMiPu/Experimental_Feedback_FirstPlayer.html"

    firstChoice = ""
    secondChoice = ""

    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"
    smilyListWidth = "500"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    smilyFeedback = ""

    def get_form_fields(self):
        return []

    def vars_for_template(self):
        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
            self.secondChoice = self.player.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(7, 0)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(7, 0)
            self.smilyFeedback = secondChooser.__getattribute__(trialObjects[0].name + "_fb_s")

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            "choiceList": self.choiceList,
            "smilyList": self.smilyList,
            "smilyImgUrl": self.smilyImgUrl,
            "smilyListWidth": self.smilyListWidth,
            "firstChoice": self.firstChoice,
            "secondChoice": self.secondChoice,
            "smilyFeedback": self.smilyFeedback,
            "ExclusionaryThreat": 'none'
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class FB16(Page):
    form_model = models.Player
    template_name = "SoMiPu/Experimental_Feedback_FirstPlayer.html"

    firstChoice = ""
    secondChoice = ""

    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"
    smilyListWidth = "500"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    smilyFeedback = ""

    def get_form_fields(self):
        return []

    def vars_for_template(self):
        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
            self.secondChoice = self.player.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(7, 1)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(7, 1)
            self.smilyFeedback = secondChooser.__getattribute__(trialObjects[0].name + "_fb_s")

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            "choiceList": self.choiceList,
            "smilyList": self.smilyList,
            "smilyImgUrl": self.smilyImgUrl,
            "smilyListWidth": self.smilyListWidth,
            "firstChoice": self.firstChoice,
            "secondChoice": self.secondChoice,
            "smilyFeedback": self.smilyFeedback,
            "ExclusionaryThreat": 'none'
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class FB17(Page):
    form_model = models.Player
    template_name = "SoMiPu/Experimental_Feedback_FirstPlayer.html"

    firstChoice = ""
    secondChoice = ""

    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"
    smilyListWidth = "500"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    smilyFeedback = ""

    def get_form_fields(self):
        return []

    def vars_for_template(self):
        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
            self.secondChoice = self.player.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(8, 0)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(8, 0)
            self.smilyFeedback = secondChooser.__getattribute__(trialObjects[0].name + "_fb_s")

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            "choiceList": self.choiceList,
            "smilyList": self.smilyList,
            "smilyImgUrl": self.smilyImgUrl,
            "smilyListWidth": self.smilyListWidth,
            "firstChoice": self.firstChoice,
            "secondChoice": self.secondChoice,
            "smilyFeedback": self.smilyFeedback,
            "ExclusionaryThreat": 'none'
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class FB18(Page):
    form_model = models.Player
    template_name = "SoMiPu/Experimental_Feedback_FirstPlayer.html"

    firstChoice = ""
    secondChoice = ""

    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"
    smilyListWidth = "500"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    smilyFeedback = ""

    def get_form_fields(self):
        return []

    def vars_for_template(self):
        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
            self.secondChoice = self.player.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(8, 1)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(8, 1)
            self.smilyFeedback = secondChooser.__getattribute__(trialObjects[0].name + "_fb_s")

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            "choiceList": self.choiceList,
            "smilyList": self.smilyList,
            "smilyImgUrl": self.smilyImgUrl,
            "smilyListWidth": self.smilyListWidth,
            "firstChoice": self.firstChoice,
            "secondChoice": self.secondChoice,
            "smilyFeedback": self.smilyFeedback,
            "ExclusionaryThreat": 'none'
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class FB19(Page):
    form_model = models.Player
    template_name = "SoMiPu/Experimental_Feedback_FirstPlayer.html"

    firstChoice = ""
    secondChoice = ""

    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"
    smilyListWidth = "500"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    smilyFeedback = ""

    def get_form_fields(self):
        return []

    def vars_for_template(self):
        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
            self.secondChoice = self.player.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(9, 0)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(9, 0)
            self.smilyFeedback = secondChooser.__getattribute__(trialObjects[0].name + "_fb_s")

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            "choiceList": self.choiceList,
            "smilyList": self.smilyList,
            "smilyImgUrl": self.smilyImgUrl,
            "smilyListWidth": self.smilyListWidth,
            "firstChoice": self.firstChoice,
            "secondChoice": self.secondChoice,
            "smilyFeedback": self.smilyFeedback,
            "ExclusionaryThreat": 'none'
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class FB20(Page):
    form_model = models.Player
    template_name = "SoMiPu/Experimental_Feedback_FirstPlayer.html"

    firstChoice = ""
    secondChoice = ""

    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"
    smilyListWidth = "500"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    smilyFeedback = ""

    def get_form_fields(self):
        return []

    def vars_for_template(self):
        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
            self.secondChoice = self.player.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(9, 1)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(9, 1)
            self.smilyFeedback = secondChooser.__getattribute__(trialObjects[0].name + "_fb_s")

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            "choiceList": self.choiceList,
            "smilyList": self.smilyList,
            "smilyImgUrl": self.smilyImgUrl,
            "smilyListWidth": self.smilyListWidth,
            "firstChoice": self.firstChoice,
            "secondChoice": self.secondChoice,
            "smilyFeedback": self.smilyFeedback,
            "ExclusionaryThreat": 'none'
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class FB21(Page):
    form_model = models.Player
    template_name = "SoMiPu/Experimental_Feedback_FirstPlayer.html"

    firstChoice = ""
    secondChoice = ""

    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"
    smilyListWidth = "500"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    smilyFeedback = ""

    def get_form_fields(self):
        return []

    def vars_for_template(self):
        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
            self.secondChoice = self.player.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(10, 0)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(10, 0)
            self.smilyFeedback = secondChooser.__getattribute__(trialObjects[0].name + "_fb_s")

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            "choiceList": self.choiceList,
            "smilyList": self.smilyList,
            "smilyImgUrl": self.smilyImgUrl,
            "smilyListWidth": self.smilyListWidth,
            "firstChoice": self.firstChoice,
            "secondChoice": self.secondChoice,
            "smilyFeedback": self.smilyFeedback,
            "ExclusionaryThreat": 'none'
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class FB22(Page):
    form_model = models.Player
    template_name = "SoMiPu/Experimental_Feedback_FirstPlayer.html"

    firstChoice = ""
    secondChoice = ""

    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"
    smilyListWidth = "500"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    smilyFeedback = ""

    def get_form_fields(self):
        return []

    def vars_for_template(self):
        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
            self.secondChoice = self.player.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(10, 1)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(10, 1)
            self.smilyFeedback = secondChooser.__getattribute__(trialObjects[0].name + "_fb_s")

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            "choiceList": self.choiceList,
            "smilyList": self.smilyList,
            "smilyImgUrl": self.smilyImgUrl,
            "smilyListWidth": self.smilyListWidth,
            "firstChoice": self.firstChoice,
            "secondChoice": self.secondChoice,
            "smilyFeedback": self.smilyFeedback,
            "ExclusionaryThreat": 'none'
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class FB23(Page):
    form_model = models.Player
    template_name = "SoMiPu/Experimental_Feedback_FirstPlayer.html"

    firstChoice = ""
    secondChoice = ""

    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"
    smilyListWidth = "500"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    smilyFeedback = ""

    def get_form_fields(self):
        return []

    def vars_for_template(self):
        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
            self.secondChoice = self.player.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(11, 0)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(11, 0)
            self.smilyFeedback = secondChooser.__getattribute__(trialObjects[0].name + "_fb_s")

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            "choiceList": self.choiceList,
            "smilyList": self.smilyList,
            "smilyImgUrl": self.smilyImgUrl,
            "smilyListWidth": self.smilyListWidth,
            "firstChoice": self.firstChoice,
            "secondChoice": self.secondChoice,
            "smilyFeedback": self.smilyFeedback,
            "ExclusionaryThreat": 'none'
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class FB24(Page):
    form_model = models.Player
    template_name = "SoMiPu/Experimental_Feedback_FirstPlayer.html"

    firstChoice = ""
    secondChoice = ""

    choiceList = [
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210},
        {"width": 100, "columnWidth": 210}
    ]

    smilyImgUrl = "img/SoMiPu/Smiley-Skala.png"
    smilyListWidth = "500"

    smilyList = [
        {"id": "cbs1"},
        {"id": "cbs2"},
        {"id": "cbs3"},
        {"id": "cbs4"},
        {"id": "cbs5"}
    ]

    smilyFeedback = ""

    def get_form_fields(self):
        return []

    def vars_for_template(self):
        if self.player.role() == "SecondChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
            self.firstChoice = firstChooser.__getattribute__('firstChoice')
            self.secondChoice = self.player.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(11, 1)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(11, 1)
            self.smilyFeedback = secondChooser.__getattribute__(trialObjects[0].name + "_fb_s")

        self.choiceList[0]['id'] = trialObjects[0].id
        self.choiceList[0]['name'] = trialObjects[0].name
        self.choiceList[0]['value'] = trialObjects[0].value
        self.choiceList[0]['url'] = trialObjects[0].url
        self.choiceList[1]['id'] = trialObjects[1].id
        self.choiceList[1]['name'] = trialObjects[1].name
        self.choiceList[1]['value'] = trialObjects[1].value
        self.choiceList[1]['url'] = trialObjects[1].url
        self.choiceList[2]['id'] = trialObjects[2].id
        self.choiceList[2]['name'] = trialObjects[2].name
        self.choiceList[2]['value'] = trialObjects[2].value
        self.choiceList[2]['url'] = trialObjects[2].url

        self.smilyList[0]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[1]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[2]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[3]['name'] = trialObjects[0].name + "_fb_s"
        self.smilyList[4]['name'] = trialObjects[0].name + "_fb_s"

        return {
            "choiceList": self.choiceList,
            "smilyList": self.smilyList,
            "smilyImgUrl": self.smilyImgUrl,
            "smilyListWidth": self.smilyListWidth,
            "firstChoice": self.firstChoice,
            "secondChoice": self.secondChoice,
            "smilyFeedback": self.smilyFeedback,
            "ExclusionaryThreat": 'none'
        }

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is True:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class C_LastPage (Page):
    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") :
           return True
        else:
            return False

class E1_LastPageFI(Page):
    template_name = "SoMiPu/E1_LastPage_FI.html"
    def is_displayed(self):

         if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser' and self.player.__getattribute__('terminate_interaction') is True:
            return True
         else:
            return False

class E1_LastPageCI(Page):
    template_name = "SoMiPu/E1_LastPage_CI.html"
    def is_displayed(self):

         if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser' and self.player.__getattribute__('terminate_interaction') is False:
            return True
         else:
            return False

class E2_LastPageFI (Page):
    template_name = "SoMiPu/E2_LastPage_FI.html"
    def is_displayed(self):
        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'SecondChooser' and self.player.__getattribute__('terminate_interaction') is True:
            return True
        else:
            return False

class E2_LastPageCI (Page):
    template_name = "SoMiPu/E2_LastPage_CI.html"
    def is_displayed(self):
        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'SecondChooser' and self.player.__getattribute__('terminate_interaction') is False:
            return True
        else:
            return False


page_sequence = [
    # This block only run for round_number == 1
    GroupingWaitPage,
    Decision,
    Example,

    # First player does not depend on P2 (no wait!)
    Trials_FP,
    Wait_Trials_FP,
    Trials_SP,
    Wait_Trials_SP,
    Exp_FB]



obsolete = [
    E_OFB_SP_HT,
    T12_ExTh,
    FB_RTF,
    WaitPe,
    E1_T12CI,
    E1_T12FI1,
    E1_T12FI2,
    WaitPe,
    T13_EFP,
    WaitPe,
    T13_ESP,
    WaitPe,
    FB13,
    WaitPe,
    T14_EFP,
    WaitPe,
    T14_ESP,
    WaitPe,
    FB14,
    WaitPe,
    T15_EFP,
    WaitPe,
    T15_ESP,
    WaitPe,
    FB15,
    WaitPe,
    T16_EFP,
    WaitPe,
    T16_ESP,
    WaitPe,
    FB16,
    WaitPe,
    T17_EFP,
    WaitPe,
    T17_ESP,
    WaitPe,
    FB17,
    WaitPe,
    T18_EFP,
    WaitPe,
    T18_ESP,
    WaitPe,
    FB18,
    WaitPe,
    T19_EFP,
    WaitPe,
    T19_ESP,
    WaitPe,
    FB19,
    WaitPe,
    T20_EFP,
    WaitPe,
    T20_ESP,
    WaitPe,
    FB20,
    WaitPe,
    T21_EFP,
    WaitPe,
    T21_ESP,
    WaitPe,
    FB21,
    WaitPe,
    T22_EFP,
    WaitPe,
    T22_ESP,
    WaitPe,
    FB22,
    WaitPe,
    T23_EFP,
    WaitPe,
    T23_ESP,
    WaitPe,
    FB23,
    WaitPe,
    T24_EFP,
    WaitPe,
    T24_ESP,
    WaitPe,
    FB24,


    
    
    C_OFB_SP_HT,
    WaitPc,
    T13_CFP,
    WaitPc,
    T13_CSP,
    WaitPc,
    T14_CFP,
    WaitPc,
    T14_CSP,
    WaitPc,
    T15_CFP,
    WaitPc,
    T15_CSP,
    WaitPc,
    T16_CFP,
    WaitPc,
    T16_CSP,
    WaitPc,
    T17_CFP,
    WaitPc,
    T17_CSP,
    WaitPc,
    T18_CFP,
    WaitPc,
    T18_CSP,
    WaitPc,
    T19_CFP,
    WaitPc,
    T19_CSP,
    WaitPc,
    T20_CFP,
    WaitPc,
    T20_CSP,
    WaitPc,
    T21_CFP,
    WaitPc,
    T21_CSP,
    WaitPc,
    T22_CFP,
    WaitPc,
    T22_CSP,
    WaitPc,
    T23_CFP,
    WaitPc,
    T23_CSP,
    WaitPc,
    T24_CFP,
    WaitPc,
    T24_CSP,
    OFB_SP,
    CB1_AP,
    CB2_FP,
    CB2_SP,
    A_PersonalData,
    C_LastPage,
    E1_LastPageFI,
    E1_LastPageCI,
    E2_LastPageFI,
    E2_LastPageCI,
    E2_A,
    E2_Resolution
]
