from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from string import digits

class A_Login(Page):
    form_model = models.Player
    form_fields = ['decision_lab_id']

    def testVars(self):
        try:
            test = self.player.participant.vars['loginError']
            testcount = self.player.participant.vars['loginCount']
        except Exception:
            self.player.participant.vars['loginError'] = ""
            self.player.participant.vars['loginCount'] = 0

    def vars_for_template(self):
        display = 'none'

        self.testVars()

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
        self.testVars()
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
        self.testVars()
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



page_sequence = [
    A_Login,
    A_Login,
    A_Login,
    A_InvalidLabid
]
