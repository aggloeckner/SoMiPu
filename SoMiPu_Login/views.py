from . import models
from ._builtin import Page


class A_Login(Page):
    form_model = models.Player
    form_fields = ['decision_lab_id']

    def before_next_page(self):
        self.player.decision_lab_id = self.player.decision_lab_id.upper()
        self.player.participant.vars["decision_lab_id"] = self.player.decision_lab_id
        self.player.participant.label = self.player.decision_lab_id

class A_Informed_consent(Page):
    pass

page_sequence = [
    A_Login,
    A_Informed_consent
]
