from halluguard.config import SecurityWeights
from halluguard.http import HttpResponse
from halluguard.mitigation import MitigationModule, ReasonCode
from halluguard.registry_client import RegistryClient
from halluguard.relevance_judge import RelevanceJudge
from halluguard.security_score import SecurityScorer
from halluguard.verifier import HalluGuardVerifier, Outcome


class ScriptedCompleter:
    def __init__(self, answers):
        self.answers = list(answers)

    def complete(self, system, user, temperature, max_tokens):
        return self.answers.pop(0)


def build(fake_http, judge_answers, regenerated=("import requests\n",)):
    http = fake_http({
        "pypi.org/pypi/requests/": HttpResponse(200, {}),
        "pypi.org/pypi/requests_plus/": HttpResponse(404, None),
        "osv": HttpResponse(200, {"vulns": []}),
        "lib.example": HttpResponse(200, {"age_days": 3000, "downloads": 1e6}),
    })
    registry = RegistryClient(http, "https://pypi.org/pypi/{package}/json")
    scorer = SecurityScorer(http, SecurityWeights(0.6, 0.2, 0.2), 0.7, "https://osv/q",
                            "https://lib.example/{package}", ["requests"])
    judge = RelevanceJudge(ScriptedCompleter(judge_answers), 0.2)
    mitigation = MitigationModule(ScriptedCompleter(regenerated), 0.2, 512)
    return HalluGuardVerifier(lambda p: "import requests_plus\n", registry, scorer, judge,
                              mitigation, {}, max_attempts=3)


def test_nonexistent_package_is_repaired(fake_http):
    outcome = build(fake_http, ["Yes"]).verify_and_mitigate("fetch a URL")
    assert outcome.outcome is Outcome.VERIFIED
    assert outcome.attempts == 2
    assert outcome.rejections[0].reason is ReasonCode.NOT_EXIST
    assert outcome.final_code == "import requests\n"


def test_irrelevant_package_exhausts_attempts(fake_http):
    v = build(fake_http, ["No", "No", "No"], regenerated=["import requests\n"] * 3)
    outcome = v.verify_and_mitigate("sort a list")
    assert outcome.outcome is Outcome.FAILED and outcome.final_code is None


def test_unparseable_code_short_circuits(fake_http):
    v = build(fake_http, [])
    v._generate = lambda p: "def ("
    assert v.verify_and_mitigate("x").outcome is Outcome.UNPARSEABLE
