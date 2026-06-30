"""Prompt for resume assessment.

Versioned so results stay traceable and the contract can evolve without
silently changing behavior. Bump RESUME_PROMPT_VERSION when the prompt or the
expected JSON output changes.

v2 — reframed for the firm's actual matter: assessing a prospect's strength as
an O-1 (extraordinary-ability) visa candidate, scored against O-1 / EB-1A
evidentiary criteria rather than generic employability.
"""

RESUME_PROMPT_VERSION = "v2"

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

Return ONLY a JSON object (no markdown, no text outside the JSON) with exactly \
these keys:
  "summary": 2-3 plain-text sentences on the prospect and their O-1 case strength.
  "score": the integer 0-100 rubric total.
  "rating": one of "strong", "moderate", "weak" (consistent with score).
  "rationale": one sentence explaining the score against the O-1 criteria.
  "strengths": array of up to 4 short strings — evidence that supports an O-1 case.
  "concerns": array of up to 3 short strings — gaps or missing O-1 evidence (use [] if none).
  "most_recent_role": the latest job title and organization, or "Not specified".
  "years_experience": approximate total years as an integer, or null if unclear.
  "education": array of short "Degree, Institution" strings (use [] if none).
  "skills": array of up to 8 key skills or areas of expertise (use [] if none).
Use only information present in the document. Do not invent details.\
"""
