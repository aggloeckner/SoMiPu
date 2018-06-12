from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from .trialList import TrialList

from string import digits


class A_Login(Page):
    form_model = models.Player
    form_fields = ['decision_lab_id']

    def vars_for_template(self):
        display = 'none'

        if self.player.participant.vars['loginError'] != 'OK':
            display = 'block'

        return {'loginError': self.player.participant.vars['loginError'],
                'displayError': display }

    def DecisionLabId_error_message(self, value):

        # Exactly 7 digits
        if len(value) < 7:
            return "Die Eingabe ist zu kurz! Die Decision Lab Id sollte genau sieben Stellen haben!"

        # Only digits
        if any([c not in digits for c in value]):
            return "Bitte nur Ziffern eingeben!"

        # Last two digits are the sum of all other digits
        sm = sum([int(c) for c in value[0:5]])
        if not sm == int(value[5:]):
            return "Fehlerhafte Decision Lab ID!"

        if value == "0000000":
            return "Fehlerhafe Decision Lab ID!"

        for p in self.subsession.get_players():
            if ("decision_lab_id" in p.participant.vars) and (p.participant.vars["decision_lab_id"] == value):
                return "Diese Decision Lab ID wird bereits verwendet!"

        return "OK"


    def before_next_page(self):
        error_message = self.DecisionLabId_error_message(self.player.decision_lab_id)
        if error_message != 'OK':
            self.player.participant.vars['loginError'] = error_message
            self.player.participant.vars['loginCount'] += 1
            self.player.__setattr__('decision_lab_id', '')
        else:
            self.player.participant.vars["decision_lab_id"] = self.player.decision_lab_id
            self.player.participant.vars['loginError'] = error_message
            self.player.participant.vars['loginCount'] = 0


    def is_displayed(self):

        if self.player.participant.vars['loginError'] != 'OK' and self.player.participant.vars['loginCount'] < 3:
            return True
        else:
            return False

class A_InvalidLabid(Page):

    def vars_for_template(self):
        return {'decision_lab_id': ""}

    def is_displayed(self):
        showMe = False

        if self.player.participant.vars['loginCount'] == 3:
            showMe = True

        print("Error:" + self.player.participant.vars['loginError'])
        print("ErrorCount:" + str(self.player.participant.vars['loginCount']))

        return showMe

    def before_next_page(self):

        self.player.participant.vars['loginError'] = ''
        self.player.participant.vars['loginCount'] = 0


class A_Welcome(Page):

    def vars_for_template(self):
        self.player.participant.vars['loginError'] = ""
        self.player.participant.vars['loginCount'] = 0
        return []


class A_Informed_consent(Page):

    def prepareTrials(self):
        if self.player.role() == "FirstChooser":
            try:
                ok = self.participant.vars['init_done']
            except:
                trials = TrialList()
                self.participant.vars['trials'] = trials
                self.participant.vars['init_done'] = 'ok'

    def vars_for_template(self):
        self.prepareTrials()
        return []  
    
class GroupingWaitPage(WaitPage):
    group_by_arrival_time = True

    def get_players_for_group(self, waiting_players):
        if len(waiting_players) >= 2:

            treatment = self.session.config['treatment']
            if treatment != 'experimental' and treatment != 'control':
                treatment = self.session.vars['treatment']
                if treatment == 'experimental':
                    treatment = 'control'
                else:
                    treatment = 'experimental'

            self.session.vars['treatment'] = treatment
            waiting_players[0].treatment = treatment
            waiting_players[1].treatment = treatment

            return [waiting_players[0], waiting_players[1]]

    # template_name = 'GroupingWaitPage.html'
    def vars_for_template(self):
        return {'body_text': "Sobald die nächste Person eintrifft, geht es los.",
                'title_text': "Bitte warten Sie."}


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
    template_name = "SoMiPu/WaitPage.html"

    def vars_for_template(self):
        return {'body_text': "Sobald die andere Person ihre Wahl getroffen hat, geht es weiter.",
                'title_text': "Bitte warten Sie ..."}

    def is_displayed(self):
        if self.session.vars['treatment'] == 'control':
            return True
        else:
            return False


class E2_Resolution(Page):
    pass


class T1_EFP (Page):
        template_name = "SoMiPu/Experimental_Trials_FirstPlayer.html"
        form_model = models.Player

        firstChoice = ""
        choiceList = [
            {"width": 100, "columnWidth": 210},
            {"width": 100, "columnWidth": 210},
            {"width": 100, "columnWidth": 210}
        ]

        def get_form_fields(self):

            trials = self.participant.vars['trials']

            trialObjects = trials.getTrial(0, 0)
            fields = ['firstChoice', trialObjects[0].name + '_seq']
            fields.append(trialObjects[0].name)
            return fields

        def vars_for_template(self):

            trials = self.participant.vars['trials']

            trialObjects = trials.getTrial(0, 0)

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
                'sequence': '1',
                'trial': trialObjects[0].name,
                'ExclusionaryThreat': "none"
            }

        def is_displayed(self):

            if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
                return True
            else:
                return False


class T2_EFP(Page):
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

        trialObjects = trials.getTrial(0, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(0, 1)

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
            'sequence': '2',
            'trial': trialObjects [0]. name,
            'ExclusionaryThreat': "block"
        }


    def is_displayed(self):
        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T3_EFP(Page):
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

        trialObjects = trials.getTrial(1, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(1, 0)

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
            'sequence': '3',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "none"
        }



    def is_displayed(self):
        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T4_EFP(Page):
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

        trialObjects = trials.getTrial(1, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(1, 1)

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
            'sequence': '4',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "block"
        }

    def is_displayed(self):
        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T5_EFP(Page):
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

        trialObjects = trials.getTrial(2, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(2, 0)

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
            'sequence': '5',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "none"
        }


    def is_displayed(self):
        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class T6_EFP(Page):
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

        trialObjects = trials.getTrial(2, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(2, 1)

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
            'sequence': '6',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "block"
        }

    def is_displayed(self):
        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T7_EFP(Page):
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

        trialObjects = trials.getTrial(3, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(3, 0)

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
            'sequence': '7',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "none"
        }


    def is_displayed(self):
        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T8_EFP(Page):
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

        trialObjects = trials.getTrial(3, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(3, 1)

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
            'sequence': '8',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "block"
        }


    def is_displayed(self):
        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T9_EFP(Page):
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

        trialObjects = trials.getTrial(4, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(4, 0)

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
            'sequence': '9',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "none"
        }


    def is_displayed(self):
        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T10_EFP(Page):
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

        trialObjects = trials.getTrial(4, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(4, 1)

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
            'sequence': '10',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "block"
        }


    def is_displayed(self):
        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T11_EFP(Page):
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

        trialObjects = trials.getTrial(5, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(5, 0)

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
            'sequence': '11',
            'trial': trialObjects[0].name,
            'ExclusionaryThreat': "none"
        }


    def is_displayed(self):
        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
            and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

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

class T1_ESP(Page):
        template_name = "SoMiPu/Experimental_Trial1_SecondPlayer.html"
        form_model = models.Player

        firstChoice = ""
        secondChoice = ""

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

            trialObjects = trials.getTrial(0, 0)
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

            trialObjects = trials.getTrial(0, 0)
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
                'sequence': '1'
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

            if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                    and self.player.role() == 'SecondChooser':
                return True
            else:
                return False


class T2_ESP (Page):
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

        trialObjects = trials.getTrial(0, 1)
        fields = ['secondChoice', trialObjects[0].name + '_fb_s', trialObjects[0].name + '_fb_ff', trialObjects[0].name + '_fb_fb',trialObjects[0].name + '_seq']
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

        trialObjects = trials.getTrial(0, 1)

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
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'smilyListWidth': self.smilyListWidth,
            'smilyImgUrl': self.smilyImgUrl,
            'smilyList': self.smilyList,
            'ExclusionaryThreat': 'block',
            'trial': trialObjects[0].name,
            'sequence': '2'
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

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T3_ESP(Page):
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

            trialObjects = trials.getTrial(1, 0)
            fields = ['secondChoice', trialObjects[0].name + '_fb_s', trialObjects[0].name + '_fb_ff',trialObjects[0].name + '_seq']
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

            trialObjects = trials.getTrial(1, 0)

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
                'sequence': '3'
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

            if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                    and self.player.role() == 'SecondChooser':
                return True
            else:
                return False


class T4_ESP(Page):
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

        trialObjects = trials.getTrial(1, 1)
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

        trialObjects = trials.getTrial(1, 1)

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
            'ExclusionaryThreat': 'block',
            'trial': trialObjects[0].name,
            'sequence': '4'
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

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T5_ESP(Page):
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

            trialObjects = trials.getTrial(2, 0)
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

            trialObjects = trials.getTrial(2, 0)

            fields = ['secondChoice', trialObjects[0].name + '_fb_s', trialObjects[0].name + '_fb_ff',trialObjects[0].name + '_seq']
            fields.append(trialObjects[0].name)

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
                'sequence': '5'
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

            if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                    and self.player.role() == 'SecondChooser':
                return True
            else:
                return False


class T6_ESP(Page):
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

        trialObjects = trials.getTrial(2, 1)
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

        trialObjects = trials.getTrial(2, 1)

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
            'ExclusionaryThreat': 'block',
            'trial': trialObjects[0].name,
            'sequence': '6'
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

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T7_ESP(Page):
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

            trialObjects = trials.getTrial(3, 0)
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

            trialObjects = trials.getTrial(3, 0)

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
                'sequence': '7'
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

            if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                    and self.player.role() == 'SecondChooser':
                return True
            else:
                return False


class T8_ESP(Page):
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

        trialObjects = trials.getTrial(3, 1)
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

        trialObjects = trials.getTrial(3, 1)

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
            'ExclusionaryThreat': 'block',
            'trial': trialObjects[0].name,
            'sequence': '8'
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

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T9_ESP(Page):
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

            trialObjects = trials.getTrial(4, 0)
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

            trialObjects = trials.getTrial(4, 0)

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
                'sequence': '9'
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

            if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                    and self.player.role() == 'SecondChooser':
                return True
            else:
                return False


class T10_ESP(Page):
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

        trialObjects = trials.getTrial(4, 1)
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

        trialObjects = trials.getTrial(4, 1)

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
            'ExclusionaryThreat': 'block',
            'trial': trialObjects[0].name,
            'sequence': '10'
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

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T11_ESP(Page):
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

            trialObjects = trials.getTrial(5, 0)
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

            trialObjects = trials.getTrial(5, 0)

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
                'sequence': '11'
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

            if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                    and self.player.role() == 'SecondChooser':
                return True
            else:
                return False

class T12_ESP (Page):
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

        trialObjects = trials.getTrial(5, 1)
        fields = ['secondChoice', trialObjects[0].name + '_fb_s', trialObjects[0].name + '_fb_ff',
                  trialObjects[0].name + '_fb_fb', trialObjects[0].name + '_seq']
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
            'sequence': '12'
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

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
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

class T1_CFP (Page):
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

        if self.player.role() == "FirstChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(0, 0)
        fields = ['firstChoice', trialObjects [0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(0, 0)

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
            'sequence': '1',
            'trial': trialObjects[0].name
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T1_CSP (Page):
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

        trialObjects = trials.getTrial(0, 0)
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

        trialObjects = trials.getTrial(0, 0)

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
            'sequence': '1',
            }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T2_CFP (Page):
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

        if self.player.role() == "FirstChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(0, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(0, 1)

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
            'sequence': '2',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class T2_CSP (Page):
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

        trialObjects = trials.getTrial(0, 1)
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

        trialObjects = trials.getTrial(0, 1)

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
            'sequence': '2',
            }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False


class T3_CFP (Page):
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

        if self.player.role() == "FirstChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(1, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(1, 0)

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
            'sequence': '3',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class T3_CSP (Page):
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

        trialObjects = trials.getTrial(1, 0)
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

        trialObjects = trials.getTrial(1, 0)

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
            'sequence': '3',
            }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False


class T4_CFP(Page):
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

        if self.player.role() == "FirstChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(1, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(1, 1)

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
            'sequence': '4',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class T4_CSP(Page):
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

        trialObjects = trials.getTrial(1, 1)
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

        trialObjects = trials.getTrial(1, 1)

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
            'sequence': '4',
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False


class T5_CFP(Page):
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

        if self.player.role() == "FirstChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(2, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(2, 0)

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
            'sequence': '5',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class T5_CSP(Page):
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

        trialObjects = trials.getTrial(2, 0)
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

        trialObjects = trials.getTrial(2, 0)

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
            'sequence': '5',
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False


class T6_CFP(Page):
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

        if self.player.role() == "FirstChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(2, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(2, 1)

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
            'sequence': '6',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T6_CSP(Page):
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

        trialObjects = trials.getTrial(2, 1)
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

        trialObjects = trials.getTrial(2, 1)

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
            'sequence': '6',
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T7_CFP(Page):
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

        if self.player.role() == "FirstChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(3, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(3, 0)

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
            'sequence': '7',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T7_CSP(Page):
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

        trialObjects = trials.getTrial(3, 0)
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

        trialObjects = trials.getTrial(3, 0)

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
            'sequence': '7',
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T8_CFP(Page):
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

        if self.player.role() == "FirstChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(3, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(3, 1)

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
            'sequence': '8',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T8_CSP(Page):
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

        trialObjects = trials.getTrial(3, 1)
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

        trialObjects = trials.getTrial(3, 1)

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
            'sequence': '8'

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T9_CFP(Page):
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

        if self.player.role() == "FirstChooser":
            firstChooser = self.group.get_player_by_role('FirstChooser')
            trials = firstChooser.participant.vars['trials']
        else:
            trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(4, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(4, 0)

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
            'sequence': '9',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T9_CSP(Page):
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

        trialObjects = trials.getTrial(4, 0)
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

        trialObjects = trials.getTrial(4, 0)

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
            'sequence': '9'
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T10_CFP(Page):
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

        trialObjects = trials.getTrial(4, 1)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(4, 1)

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
            'sequence': '10',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T10_CSP(Page):
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

        trialObjects = trials.getTrial(4, 1)
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

        trialObjects = trials.getTrial(4, 1)

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
            'sequence': '10'
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False


class T11_CFP(Page):
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

        trialObjects = trials.getTrial(5, 0)
        fields = ['firstChoice', trialObjects[0].name + '_seq']
        fields.append(trialObjects[0].name)
        return fields

    def vars_for_template(self):

        trials = self.participant.vars['trials']

        trialObjects = trials.getTrial(5, 0)

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
            'sequence': '11',
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T11_CSP(Page):
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

        trialObjects = trials.getTrial(5, 0)
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

        trialObjects = trials.getTrial(5, 0)

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
            'sequence': '11'
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class T12_CFP(Page):
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
            'trial': trialObjects[0].name

        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class T12_CSP(Page):
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

        trialObjects = trials.getTrial(5, 1)
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

        # print(self.player.__dict__trial_1a)
        # print("form_fields:" + self.form_fields[0])
        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
            'trial': trialObjects[0].name,
            'sequence': '12'
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
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

class C1_Decision(Page):
    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class C2_Decision (Page):
    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False


class E1_Decision(Page):
    def is_displayed(self):

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class E2_Decision(Page):
    def is_displayed(self):

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False


class C1_Example (Page):
    firstChoice = "idx"

    choiceList = [
        {
            "id": "id0",
            "name": "doubledElement",
            "url": "img/SoMiPu/MM_green.png",
            "width": 100,
            "columnWidth": 210,
        },
        {
            "id": "id1",
            "name": "singleElement",
            "url": "img/SoMiPu/MM_blue.png",
            "width": 100,
            "columnWidth": 210,
        },
        {
            "id": "id2",
            "name": "doubledElement",
            "url": "img/SoMiPu/MM_green.png",
            "width": 100,
            "columnWidth": 210,
        }
    ]


    def vars_for_template(self):
        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class C2_Example (Page):
    firstChoice = "idx"

    choiceList = [
        {
            "id": "id0",
            "name": "doubledElement",
            "url": "img/SoMiPu/MM_green.png",
            "width": 100,
            "columnWidth": 210,
        },
        {
            "id": "id1",
            "name": "singleElement",
            "url": "img/SoMiPu/MM_blue.png",
            "width": 100,
            "columnWidth": 210,
        },
        {
            "id": "id2",
            "name": "doubledElement",
            "url": "img/SoMiPu/MM_green.png",
            "width": 100,
            "columnWidth": 210,
        }
    ]

    def vars_for_template(self):
        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "control" or self.player.treatment == "control") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

class E1_Example (Page):
    firstChoice = "idx"

    choiceList = [
        {
            "id": "id0",
            "name": "doubledElement",
            "url": "img/SoMiPu/MM_green.png",
            "width": 100,
            "columnWidth": 210,
        },
        {
            "id": "id1",
            "name": "singleElement",
            "url": "img/SoMiPu/MM_blue.png",
            "width": 100,
            "columnWidth": 210,
        },
        {
            "id": "id2",
            "name": "doubledElement",
            "url": "img/SoMiPu/MM_green.png",
            "width": 100,
            "columnWidth": 210,
        }
    ]

    def vars_for_template(self):
        return {
            'choiceList': self.choiceList,
            'firstChoice': self.firstChoice,
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class E2_Example(Page):

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
            'smilyList': self.smilyList
        }

    def is_displayed(self):

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
            return True
        else:
            return False

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

        if self.player.role() == 'SecondChooser' and self.player.__getattribute__('terminate_interaction') is False:
            return True
        else:
            return False

class OFB_ExSP(Page):
    template_name = "SoMiPu/Exclusion_Overall_Feedback_SecondPlayer.html"
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

        return ['overall_fb_s', 'overall_fb_ff', 'reason_to_finish']


    def vars_for_template(self):

        self.smilyList[0]['name'] =  "overall_fb_s"
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

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser' and self.player.__getattribute__('terminate_interaction') is True:
            return True
        else:
            return False


class FB1(Page):
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
            trialObjects = trials.getTrial(0, 0)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(0, 0)
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

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class FB2(Page):
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
            trialObjects = trials.getTrial(0, 1)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(0, 1)
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

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class FB3(Page):
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
            trialObjects = trials.getTrial(1, 0)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(1, 0)
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

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class FB4(Page):
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
            trialObjects = trials.getTrial(1, 1)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(1, 1)
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

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class FB5(Page):
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
            trialObjects = trials.getTrial(2, 0)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(2, 0)
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

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class FB6(Page):
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
            trialObjects = trials.getTrial(2, 1)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(2, 1)
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

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False


class FB7(Page):
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
            trialObjects = trials.getTrial(3, 0)
            self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
        else:
            secondChooser = self.group.get_player_by_role('SecondChooser')
            trials = self.participant.vars['trials']
            self.firstChoice = self.player.__getattribute__('firstChoice')
            self.secondChoice = secondChooser.__getattribute__('secondChoice')
            trialObjects = trials.getTrial(3, 0)
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

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
            return True
        else:
            return False

class FB8(Page):
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
                trialObjects = trials.getTrial(3, 1)
                self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
            else:
                secondChooser = self.group.get_player_by_role('SecondChooser')
                trials = self.participant.vars['trials']
                self.firstChoice = self.player.__getattribute__('firstChoice')
                self.secondChoice = secondChooser.__getattribute__('secondChoice')
                trialObjects = trials.getTrial(3, 1)
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

            if (self.player.session.config[
                'treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
                return True
            else:
                return False


class FB9(Page):
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
                trialObjects = trials.getTrial(4, 0)
                self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
            else:
                secondChooser = self.group.get_player_by_role('SecondChooser')
                trials = self.participant.vars['trials']
                self.firstChoice = self.player.__getattribute__('firstChoice')
                self.secondChoice = secondChooser.__getattribute__('secondChoice')
                trialObjects = trials.getTrial(4, 0)
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

            if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'FirstChooser':
                return True
            else:
                return False

class FB10(Page):

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
                trialObjects = trials.getTrial(4, 1)
                self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
            else:
                secondChooser = self.group.get_player_by_role('SecondChooser')
                trials = self.participant.vars['trials']
                self.firstChoice = self.player.__getattribute__('firstChoice')
                self.secondChoice = secondChooser.__getattribute__('secondChoice')
                trialObjects = trials.getTrial(4, 1)
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

            if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                    and self.player.role() == 'FirstChooser':
                return True
            else:
                return False


class FB11(Page):
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
                trialObjects = trials.getTrial(5, 0)
                self.smilyFeedback = self.player.__getattribute__(trialObjects[0].name + "_fb_s")
            else:
                secondChooser = self.group.get_player_by_role('SecondChooser')
                trials = self.participant.vars['trials']
                self.firstChoice = self.player.__getattribute__('firstChoice')
                self.secondChoice = secondChooser.__getattribute__('secondChoice')
                trialObjects = trials.getTrial(5, 0)
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

            if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                    and self.player.role() == 'FirstChooser':
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

class E2_T12FI (Page):
    template_name = "SoMiPu/Feedback12_FinishInteraction_SecondPlayer.html"

    def is_displayed(self):
        if self.player.__getattribute__('terminate_interaction') is False:
            return False

        if (self.player.session.config['treatment'] == "experimental" or self.player.treatment == "experimental") \
                and self.player.role() == 'SecondChooser':
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
    GroupingWaitPage,
    A_Welcome,
    A_Login,
    A_Login,
    A_Login,
    A_InvalidLabid,
    A_Informed_consent,
    E1_Decision,
    E1_Example,
    E2_Decision,
    E2_Example,
    T1_EFP,
    WaitPe,
    T1_ESP,
    WaitPe,
    FB1,
    WaitPe,
    T2_EFP,
    WaitPe,
    T2_ESP,
    WaitPe,
    FB2,
    WaitPe,
    T3_EFP,
    WaitPe,
    T3_ESP,
    WaitPe,
    FB3,
    WaitPe,
    T4_EFP,
    WaitPe,
    T4_ESP,
    WaitPe,
    FB4,
    WaitPe,
    T5_EFP,
    WaitPe,
    T5_ESP,
    WaitPe,
    FB5,
    WaitPe,
    T6_EFP,
    WaitPe,
    T6_ESP,
    WaitPe,
    FB6,
    WaitPe,
    T7_EFP,
    WaitPe,
    T7_ESP,
    WaitPe,
    FB7,
    WaitPe,
    T8_EFP,
    WaitPe,
    T8_ESP,
    WaitPe,
    FB8,
    WaitPe,
    T9_EFP,
    WaitPe,
    T9_ESP,
    WaitPe,
    FB9,
    WaitPe,
    T10_EFP,
    WaitPe,
    T10_ESP,
    WaitPe,
    FB10,
    WaitPe,
    T11_EFP,
    WaitPe,
    T11_ESP,
    WaitPe,
    FB11,
    WaitPe,
    T12_EFP,
    WaitPe,
    T12_ESP,
    T12_ExTh,
    WaitPe,
    E1_T12CI,
    E1_T12FI1,
    E1_T12FI2,
    E2_T12FI,
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
    C1_Decision,
    C2_Decision,
    C1_Example,
    C2_Example,
    WaitPc,
    T1_CFP,
    WaitPc,
    T1_CSP,
    WaitPc,
    T2_CFP,
    WaitPc,
    T2_CSP,
    WaitPc,
    T3_CFP,
    WaitPc,
    T3_CSP,
    WaitPc,
    T4_CFP,
    WaitPc,
    T4_CSP,
    WaitPc,
    T5_CFP,
    WaitPc,
    T5_CSP,
    WaitPc,
    T6_CFP,
    WaitPc,
    T6_CSP,
    WaitPc,
    T7_CFP,
    WaitPc,
    T7_CSP,
    WaitPc,
    T8_CFP,
    WaitPc,
    T8_CSP,
    WaitPc,
    T9_CFP,
    WaitPc,
    T9_CSP,
    WaitPc,
    T10_CFP,
    WaitPc,
    T10_CSP,
    WaitPc,
    T11_CFP,
    WaitPc,
    T11_CSP,
    WaitPc,
    T12_CFP,
    WaitPc,
    T12_CSP,
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
    OFB_ExSP,
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
