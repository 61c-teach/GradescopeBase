import datetime
import time
from typing import List

from . import Autograder
from .Utils import is_local

class RateLimit:
    def __init__(
        self,
        tokens: int=None,
        seconds: int=0,
        minutes: int=0,
        hours: int=0,
        days: int=0,
        reset_time: str=None,
        pull_prev_run: bool=False,
        submission_id_exclude: List[str]=[],
        verbose: bool=False
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

        self.verbose = verbose

        self.oldest_token_time = None
        self.current_submission_time = None

        self.main_string = ""
        self.tokens_used = ""

    def is_enabled(self):
        return not (self.tokens is None or self.tokens <= 0)

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
        if not self.is_enabled():
            return ""
        datetime_regen_rate = datetime.timedelta(seconds=self.total_seconds())
        sub_to_count = None
        if self.oldest_token_time:
            sub_to_count = self.oldest_token_time
        else:
            if self.rate_limit_does_submission_count(ag):
                sub_to_count = self.current_submission_time
        

        tu = self.tokens_used
        if not self.rate_limit_does_submission_count(ag):
            tu -= 1

        if sub_to_count is not None:
            next_token_regen = sub_to_count + datetime_regen_rate
            next_token_regen_str = f"[Rate Limit]: As of this submission time, your next token will regenerate at {next_token_regen.ctime()} (PT).\n\n"
        else:
            next_token_regen_str = "[Rate Limit]: As of this submission time, you have not used any tokens!\n\n"

        return self.main_string.format(tu) + next_token_regen_str

    def total_seconds(self):
        return self.seconds + 60 * (self.minutes + 60 * (self.hours + (24 * self.days)))

    def rate_limit_main(self, ag: Autograder, verbose=None):
        if verbose is None:
            verbose = self.verbose
        if not self.is_enabled():
            return
        if is_local() and not ag.use_ratelimit_when_local:
            print("[WARNING]: Rate limit is enabled but will not be checked because this has been detected to be a local run!")
            return
        tokens = self.tokens
        restart_subm_string = self.reset_time
        s = self.seconds
        m = self.minutes
        h = self.hours
        d = self.days
        regen_time_seconds = self.total_seconds()
        def get_submission_time(s):
            return s[:-13]
        def pretty_time_str(s, m, h, d):
            sstr = "" if s == 0 else str(s) + " second"
            sstr += "" if sstr == "" or s == 1 else "s"
            mstr = "" if m == 0 else str(m) + " minute"
            mstr += "" if mstr == "" or m == 1 else "s"
            hstr = "" if h == 0 else str(h) + " hour"
            hstr += "" if hstr == "" or h == 1 else "s"
            dstr = "" if d == 0 else str(d) + " day"
            dstr += "" if dstr == "" or d == 1 else "s"
            st = dstr
            for tmpstr in [hstr, mstr, sstr]:
                if st != "" and tmpstr != "":
                    st += " "
                st += tmpstr
            if st == "":
                st = "none"
            return st
        current_subm_string = get_submission_time(ag.metadata["created_at"])
        current_time = time.strptime(current_subm_string,"%Y-%m-%dT%H:%M:%S")
        restart_time = time.strptime(restart_subm_string, "%Y-%m-%dT%H:%M:%S") if restart_subm_string is not None else None
        tokens_used = 0
        if verbose:
            print("=" * 30)
        oldest_counted_submission = None
        for i, v in enumerate(ag.metadata["previous_submissions"]):
            subm_string = get_submission_time(v["submission_time"])
            subm_time = time.strptime(subm_string,"%Y-%m-%dT%H:%M:%S")
            if restart_time is not None and time.mktime(subm_time) - time.mktime(restart_time) < 0:
                if verbose:
                    print("Ignoring a submission, too early!")
                continue
            if verbose:
                print("Current time: " + str(time.mktime(current_time)))
                print("Subm time: " + str(time.mktime(subm_time)))
            if (time.mktime(current_time) - time.mktime(subm_time) < regen_time_seconds): 
                try:
                    if verbose:
                        print(ag.metadata["previous_submissions"][i])
                        print("Tokens used: " + str(tokens_used))
                        print(str(ag.metadata["previous_submissions"][i].keys()))
                        print("Current submission data: " + str(ag.metadata["previous_submissions"][i]["results"]["extra_data"]))
                    ed = ag.metadata["previous_submissions"][i]["results"]["extra_data"]
                    if ed is not None:
                        subID = ed.get("id")
                        if (ed["sub_counts"] == 1) and (subID and (subID not in self.submission_id_exclude)): 
                            if oldest_counted_submission is None:
                                oldest_counted_submission = subm_time
                            tokens_used = tokens_used + 1
                    else:
                        if verbose:
                            print(f"Extra data not available in previous submission {i}!")
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(e)
                    tokens_used = tokens_used + 1
                    pass
            if verbose:
                print("-" * 30)
        if verbose:
            print("=" * 30)
        datetime_regen_rate = datetime.timedelta(seconds=regen_time_seconds)
        if oldest_counted_submission:
            oldest_counted_submission = datetime.datetime.fromtimestamp(time.mktime(oldest_counted_submission))
        if current_time:
            datetime_current_time = datetime.datetime.fromtimestamp(time.mktime(current_time))
        if tokens_used < tokens:
            ag.extra_data["sub_counts"] = 1
            tokens_used += 1 # This is to include the current submission.
            self.rate_limit_set_main_string(f"[Rate Limit]: Students can get up to {tokens} graded submissions within any given period of {pretty_time_str(s, m, h, d)}. In the last period, you have had {{}} graded submissions.\n", tokens_used)
            self.set_next_token_regen(oldest_counted_submission, datetime_current_time)
        else:
            ag.extra_data["sub_counts"] = 0
            if self.pull_prev_run:
                msg = ", so the results of your last graded submission are being displayed."
            else:
                msg = "."
            ag.print(f"[Rate Limit]: Students can get up to {tokens} graded submissions within any given period of {pretty_time_str(s, m, h, d)}. You have already had {tokens_used} graded submissions within the last {pretty_time_str(s, m, h, d)}{msg} Because you do not have any more tokens, this submission will not count as a graded submission.")

            if oldest_counted_submission:
                next_token_regen = oldest_counted_submission + datetime_regen_rate
                ag.print(f"[Rate Limit]: As of this submission time, your next token will regenerate at {next_token_regen.ctime()} (PT).\n")
            else:
                ag.print(f"[Rate Limit]: As of this submisison, you have not used any tokens.\n")
            
            if self.pull_prev_run:
                prev_subs = ag.metadata["previous_submissions"]
                prev_sub = prev_subs[len(prev_subs) - 1]
                if prev_sub and "results" not in prev_sub or prev_sub["results"] and "tests" not in prev_sub["results"]:
                    ag.print("[ERROR]: Could not pull the data from your previous submission! This is probably due to it not have finished running!")
                    tests = []
                    ag.set_score(0)
                    leaderboard = None
                else:
                    res = prev_sub["results"]
                    tests = res["tests"]
                    leaderboard = res["leaderboard"]
                    ag.set_score(prev_sub.get("score"))
            else:
                    tests = []
                    ag.set_score(0)
                    leaderboard = None
                
            ag.generate_results(test_results=tests, leaderboard=leaderboard)
            
            import sys
            sys.exit()
            # raise AutograderHalt("Rate limited!")

    @staticmethod
    def rate_limit_unset_submission(ag: Autograder):
        ag.extra_data["sub_counts"] = 0

    @staticmethod
    def rate_limit_does_submission_count(ag: Autograder):
        return ag.extra_data["sub_counts"]