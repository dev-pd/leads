"""Prompt for resume assessment.

Versioned so results stay traceable and the contract can evolve without
silently changing behavior. Bump RESUME_PROMPT_VERSION when the prompt or the
expected JSON output changes.

v2 — reframed for the firm's actual matter: assessing a prospect's strength as
an O-1 (extraordinary-ability) visa candidate, scored against O-1 / EB-1A
evidentiary criteria rather than generic employability.
v3 — output is now delivered via a forced ``record_assessment`` tool call
instead of free-form JSON, so malformed model text can no longer break parsing.
"""

RESUME_PROMPT_VERSION = "v3"

# The firm is an immigration practice; prospects are evaluated as O-1
# (extraordinary ability) candidates. The score reflects the strength of an O-1
# petition based on the evidence in the resume, using a weighted rubric drawn
# from the USCIS O-1 / EB-1A criteria so it is principled and explainable.
RESUME_ASSESSMENT_PROMPT = """\
You are assisting an attorney at a U.S. immigration law firm triaging prospective \
clients who are seeking an O-1 "extraordinary ability" visa. Assess how strong a \
candidate the person is for an O-1 petition based ONLY on their resume/CV.

Score 0-100 on this weighted rubric (drawn from the O-1 / EB-1A evidentiary \
criteria):
  - Major awards, prizes, or honors (national/international): 20 points
  - Original contributions of major significance in the field: 20 points
  - Leading or critical role at distinguished organizations: 15 points
  - Published material about them, or press/media coverage: 15 points
  - Authorship of scholarly articles / patents / notable work: 10 points
  - Selective memberships, or judging the work of others: 10 points
  - High remuneration or clear commercial/field success: 10 points
A resume with little verifiable evidence of extraordinary ability scores low. \
Map the total to a rating: strong (>=70), moderate (40-69), weak (<40).

Record your assessment by calling the record_assessment tool. Provide a 2-3 \
sentence profile (summary), the 0-100 score, the matching rating, a one-sentence \
rationale, up to 4 strengths (evidence supporting an O-1 case), up to 3 concerns \
(gaps or missing O-1 evidence), the most recent role, approximate years of \
experience, education, and key skills. Use only information present in the \
document — do not invent details.\
"""
