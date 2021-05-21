import datetime
from . import Autograder

class RateLimit:
    def __init__(
        self,
        tokens:int=None,
        seconds:int=0,
        minutes:int=0,
        hours:int=0,
        days:int=0,
        reset_time:str=None,
        pull_prev_run=False,
        submission_id_exclude=[]
    ):
        self.tokens = tokens
        self.seconds = seconds
        self.minutes = minutes
        self.hours = hours
        self.days = days
        self.reset_time = reset_time
        self.output = ""

        self.pull_prev_run = pull_prev_run

        self.submission_id_exclude = submission_id_exclude

        self.oldest_token_time = None
        self.current_submission_time = None

        self.main_string = ""
        self.tokens_used = ""

    def print(self, *args, sep=' ', end='\n', file=None, flush=True, also_stdout=False):
        msg = sep.join(map(str, args)) + end
        if also_stdout:
            print(msg)
        self.output += msg

    def set_next_token_regen(self, oldest_token_time, current_submission_time):
        self.oldest_token_time = oldest_token_time
        self.current_submission_time = current_submission_time

    def rate_limit_set_main_string(self, string, tokens_used):
        self.main_string = string
        self.tokens_used = tokens_used

    def get_rate_limit_str(self, ag: Autograder):
        datetime_regen_rate = datetime.timedelta(seconds=self.total_seconds())
        sub_to_count = None
        if self.oldest_token_time:
            sub_to_count = self.oldest_token_time
        else:
            if ag.rate_limit_does_submission_count():
                sub_to_count = self.current_submission_time
        

        tu = self.tokens_used
        if not ag.rate_limit_does_submission_count():
            tu -= 1

        if sub_to_count is not None:
            next_token_regen = sub_to_count + datetime_regen_rate
            next_token_regen_str = f"[Rate Limit]: As of this submission time, your next token will regenerate at {next_token_regen.ctime()} (PT).\n\n"
        else:
            next_token_regen_str = "[Rate Limit]: As of this submission time, you have not used any tokens!\n\n"

        return self.main_string.format(tu) + next_token_regen_str

    def total_seconds(self):
        return self.seconds + 60 * (self.minutes + 60 * (self.hours + (24 * self.days)))