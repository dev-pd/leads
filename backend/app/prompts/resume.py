"""Prompt for resume assessment.

Versioned so results stay traceable and the contract can evolve without
silently changing behavior. Bump RESUME_PROMPT_VERSION when the prompt or the
expected JSON output changes.
"""

RESUME_PROMPT_VERSION = "v1"

# Explicit, weighted rubric so scores are principled, consistent, and
# explainable — not a vibe. The model applies these weights to produce `score`.
RESUME_ASSESSMENT_PROMPT = """\
You are assisting an attorney triaging prospective clients from their submitted \
resume/CV. Score the prospect on this weighted rubric (0-100):
  - Relevant experience & seniority (depth, years): 35 points
  - Education, credentials & certifications: 20 points
  - Demonstrated skills relevant to the engagement: 20 points
  - Track record & achievements (impact, progression): 15 points
  - Resume clarity & completeness: 10 points
A thin, empty, or unreadable resume scores low. Map the total to a rating: \
strong (>=70), moderate (40-69), weak (<40).

Also extract the key resume details so the attorney can review the prospect at \
a glance.

Return ONLY a JSON object (no markdown, no text outside the JSON) with exactly \
these keys:
  "summary": a 2-3 sentence plain-text profile of the person.
  "score": the integer 0-100 rubric total.
  "rating": one of "strong", "moderate", "weak" (consistent with score).
  "rationale": one sentence explaining the score against the rubric.
  "strengths": array of up to 4 short strings.
  "concerns": array of up to 3 short strings (use [] if none).
  "most_recent_role": the latest job title and organization, or "Not specified".
  "years_experience": approximate total years as an integer, or null if unclear.
  "education": array of short "Degree, Institution" strings (use [] if none).
  "skills": array of up to 8 key skills (use [] if none).
Use only information present in the document. Do not invent details.\
"""
