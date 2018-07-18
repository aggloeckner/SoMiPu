from otree.api import Currency as c, currency_range
from . import views
from ._builtin import Bot
from otree.bots import Submission, SubmissionMustFail
from .models import Constants

from bs4 import BeautifulSoup
import random
import lorem


class PlayerBot(Bot):

    cases = [   { "terminate" : "yes",      "alwaysChoose" : "random"},
                { "terminate" : "no",       "alwaysChoose" : "random"},
                { "terminate" : "random",   "alwaysChoose" : "single"},
                { "terminate" : "random",   "alwaysChoose" : "double"},
                { "terminate" : "random",   "alwaysChoose" : "random"} ]

    def maybe_lorem(self):
        if random.getrandbits(1) == 1:
            return lorem.sentence()
        else:
            return ""

    def get_field_value(self, phtml, div, name, type):
        return type( phtml.find(id = div).find("input", attrs={'name':name})["value"])

    def get_options(self, phtml):
        return dict( [(ip["id"],ip["value"]) for ip in phtml.find(id="choice").find_all("input", attrs={"name":"choice"})] )

    def make_submission(self, phtml):
        ret = dict()

        ret["firstChoice"]  = self.get_field_value(phtml, "ChoiceDataForm", "firstChoice", str)

        ret["stimulus"]             = self.get_field_value(phtml, "TrialData", "stimulus", int)
        ret["stimulus_name"]        = self.get_field_value(phtml, "TrialData", "stimulus_name", str)
        ret["single"]               = self.get_field_value(phtml, "TrialData", "single", str)
        ret["double"]               = self.get_field_value(phtml, "TrialData", "double", str)
        ret["subtrial"]             = self.get_field_value(phtml, "TrialData", "subtrial", str)
        ret["trial"]                = self.get_field_value(phtml, "TrialData", "trial", int)
        ret["repeat"]               = self.get_field_value(phtml, "TrialData", "repeat", str)
        ret["item1"]                = self.get_field_value(phtml, "TrialData", "item1", str)
        ret["item2"]                = self.get_field_value(phtml, "TrialData", "item2", str)
        ret["item3"]                = self.get_field_value(phtml, "TrialData", "item3", str)
        ret["ExclusionaryThreat"]   = self.get_field_value(phtml, "TrialData", "ExclusionaryThreat", str)

        return ret


    def play_round(self):

        ##### First round

        if self.subsession.round_number == 1:
            #### Description of experiment 
            phtml = BeautifulSoup(self.html, "lxml")
            if self.player.is_experimental():
                assert phtml.find(id = "ExclusionaryThreat") is not None
            else:
                assert phtml.find(id = "ExclusionaryThreat") is None
            yield(views.Decision)

            #### Example choice
            yield(views.Example, {"example_choice": "single"})

        ##### Trials only when not terminated

        # We cant ever terminate before halftime
        if self.player.before_halftime():
            assert self.player.has_not_terminated()

        if self.player.has_not_terminated():
            phtml = BeautifulSoup(self.html, "lxml")
            try:
                s = self.make_submission(phtml)
            except:
                f = open("/tmp/form.html", "w")
                f.write(phtml.prettify())
                f.close()
                raise

            ## Some general tests

            # Exclusionary threat never after HT
            if self.player.after_halftime():
                assert s["ExclusionaryThreat"] == "False"
            else:
                # Exclusionary threat never on "a" pages
                if s["repeat"] == "a":
                    assert s["ExclusionaryThreat"] == "False"
                else:
                    assert s["ExclusionaryThreat"] == "True"

            # Exclusionary threat displayed if True (only experimental group)
            if self.player.is_experimental() and s["ExclusionaryThreat"] == "True":
                assert phtml.find(id = "ExclusionaryThreat") is not None
            else:
                assert phtml.find(id = "ExclusionaryThreat") is None


            opts = self.get_options(phtml)


            ##### For first player

            if self.player.is_first():
                
                #### Choice Trial

                # FirstChoice should never be set on the webpage for first player
                assert s["firstChoice"] == ""

                if self.case["alwaysChoose"] == "random":
                    choice = random.choice(list(opts.keys()))
                else:
                    choice = random.choice([o[0] for o in opts.items() if o[1] == self.case["alwaysChoose"]])              

                ## Test validation for first Choice (must be in list of choices)

                # Item not available
                s["firstChoice"] = "invalid_item"
                s["choice"] = "single"

                yield SubmissionMustFail( views.Trials_FP, s)

                # Item not single / double
                s["firstChoice"] = choice

                s["choice"] = "invalid_item_type"

                yield SubmissionMustFail( views.Trials_FP, s)                

                s["choice"] = opts[choice]
                yield(views.Trials_FP, s)

                #### Feedback from Player 2 (only experimental group)

                if self.player.is_experimental():
                    phtml = BeautifulSoup(self.html, "lxml")
                    if self.player.has_terminated():
                        # Feedback after termination should show terminate message
                        assert phtml.find(id="hasTerminated") is not None
                        assert phtml.find(id="halftime-ci") is None
                        assert phtml.find(id="ExclusionaryThreat") is None
                    else:
                        assert phtml.find(id="hasTerminated") is None
                        if self.player.repeat_name() == "a":
                            assert phtml.find(id="ExclusionaryThreat") is None
                            assert phtml.find(id="hasTerminated") is None
                            assert phtml.find(id="halftime-ci") is None
                        else:
                            if self.player.after_halftime():
                                # Never show exclusionary threat after halftime
                                assert phtml.find(id="ExclusionaryThreat") is None
                                assert phtml.find(id="hasTerminated") is None
                                assert phtml.find(id="halftime-ci") is None
                            elif self.player.is_halftime():
                                # "b" repeat 
                                # at half time
                                # not terminated
                                assert phtml.find(id="ExclusionaryThreat") is None
                                assert phtml.find(id="hasTerminated") is None
                                assert phtml.find(id="halftime-ci") is not None
                            else:
                                # "b" repeat 
                                # strictly before half time
                                # not terminated
                                assert phtml.find(id="ExclusionaryThreat") is not None
                                assert phtml.find(id="hasTerminated") is None
                                assert phtml.find(id="halftime-ci") is None
                    yield (views.Exp_FB)



            ##### For second player

            else:

                #### Choice Trial

                # FirstChoice must match the one stored for Player 1
                assert s["firstChoice"] == self.player.get_fp().firstChoice

                choice = random.choice([k for k in opts.keys() if k != s["firstChoice"]])
                s["fb_ff"] = random.randrange(500)
                if self.player.is_experimental():
                    # Check smilies are available
                    assert phtml.find(id = "smilies") is not None
                    s["fb_s"] = random.randrange(1,6)
                else:
                    assert phtml.find(id = "smilies") is None

                # On b trials also give fb feedback
                if s["repeat"] == "b":
                    ## Check slider is available
                    assert phtml.find(id="vas_fb") is not None
                    s["fb_fb"] = random.randrange(500)
                else:
                    assert phtml.find(id="vas_fb") is None
                                      
                ## Tests for second player submission

                # Item not available
                s["secondChoice"] = "invalid_item"
                s["choice"] = "single"

                yield SubmissionMustFail( views.Trials_SP, s, check_html=False)

                # Same item as first player
                s["secondChoice"] = s["firstChoice"]
                yield SubmissionMustFail( views.Trials_SP, s, check_html=False)

                s["secondChoice"] = choice
                
                # Same item type (single) as first player
                # Should work for item type double
                if self.case["alwaysChoose"] == "single":                  
                    s["choice"] = "single"
                    yield SubmissionMustFail( views.Trials_SP, s, check_html=False)

                # Item not single / double
                s["choice"] = "invalid_item_type"

                yield SubmissionMustFail( views.Trials_SP, s, check_html=False)      

                s["secondChoice"] = choice
                s["choice"] = opts[choice]


                # fb_ff and fb_fb fields generated by javascript
                # => disable html checks
                yield Submission(views.Trials_SP, s, check_html=False)

                ##### Feedback and ExTh at halftime

                if self.player.is_halftime():

                    #### Overall Feedback Half Time

                    s["overall_fb_s_ht"] = random.randrange(1,6)
                    s["overall_fb_ff_ht"] = random.randrange(500)
                    yield Submission(views.OFB_SP_HT, s, check_html=False)
                    
                    #### Terminate for second player

                    if self.player.is_experimental():
                        if self.case["terminate"] == "yes":
                            doTerminate = True
                        elif self.case["terminate"] == "no":
                            doTerminate = False
                        else:
                            doTerminate = random.choice([True,False])
                        yield (views.HT_ExTh, {"terminate_interaction" : doTerminate})

                        assert self.player.has_terminated() == doTerminate
                        assert self.player.get_fp().has_terminated() == doTerminate
                        assert self.player.get_sp().has_terminated() == doTerminate

                        #### Reason to finish after terminate

                        if doTerminate:
                            s = { "reason_to_finish" : self.maybe_lorem() }
                            yield (views.FB_RTF, s)

                #### Overall Feedback Full Time

                if self.player.is_fulltime() and self.player.has_not_terminated():
                    s["overall_fb_s"] = random.randrange(1,6)
                    s["overall_fb_ff"] = random.randrange(500)
                    yield Submission(views.OFB_SP, s, check_html=False)

        if self.player.is_fulltime():
            s = { 
                'overall_fb_cb1' : random.choice([True, False]),
                'overall_fb_cb2' : random.choice([True, False]),
                'overall_fb_cb3' : random.choice([True, False]), 
                'overall_fb_cb4' : random.choice([True, False]),
                'overall_fb_cb5' : random.choice([True, False]), 
                'overall_fb_cb6' : random.choice([True, False])}

            yield (views.CB1_AP, s)

            s = { 
                'overall_fb_tx2' : self.maybe_lorem(), 
                'overall_fb_tx3' : self.maybe_lorem()}
            if self.player.is_first():
                s['overall_fb_tx1'] = self.maybe_lorem()

            yield (views.CB2_AP, s)

            s = {
                'participant_sex' : random.choice([1,2,3]), 
                'participant_age' : random.randrange(18,100), 
                'participant_lang_skills' : random.choice([1,2,3,4,5,6])
            }
            yield (views.A_PersonalData, s)

            # Final checks

            if self.player.is_experimental():
                if self.case["terminate"] == "yes":
                    assert self.player.has_terminated()
                elif self.case["terminate"] == "no":
                    assert self.player.has_not_terminated()
            else:
                # Control group must NEVER terminate
                assert self.player.has_not_terminated()

            if self.player.has_terminated():
                assert self.participant.payoff == c(2)
            else:
                assert self.participant.payoff == c(4)
            # LastPage must not be yielded, since there is no button on that page
            

