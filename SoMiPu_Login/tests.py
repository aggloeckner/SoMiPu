from otree.api import Currency as c, currency_range
from . import views
from ._builtin import Bot
from .models import Constants


RBase = {
	1000 : "M",
	 900 : "CM",
	 500 : "D",
	 400 : "CD",
	 100 : "C",
	  90 : "XC",
	  50 : "L",
	  40 : "XL",
	  10 : "X",
	   9 : "IX",
	   5 : "V",
	   4 : "IV",
	   1 : "I" }

def toRoman(n):
	res = ""
	for b in sorted( RBase.keys(), reverse=True ):
		while n >= b:
			n = n - b
			res = res + RBase[b]
	return res



class PlayerBot(Bot):

    def play_round(self):
        yield (views.A_Login, {"decision_lab_id" : "Botty McBotface " + toRoman(self.player.id)} )
        yield (views.A_Informed_consent)
        
