from . import models
from ._builtin import Page


class A_Login(Page):
    form_model = models.Player
    form_fields = ['decision_lab_id']

    def before_next_page(self):
        self.player.participant.vars["decision_lab_id"] = self.player.decision_lab_id


page_sequence = [
    A_Login
]
