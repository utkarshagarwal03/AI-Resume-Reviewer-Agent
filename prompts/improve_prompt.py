RESUME_IMPROVEMENT_PROMPT = """
You are a professional resume writer and career coach.
Review the following resume and identify bullet points or descriptions that can be rewritten to be more impactful.
Also suggest formatting enhancements and additional projects that would strengthen the profile.

Provide your suggestions EXACTLY in the following JSON format. Do not add any markdown wrapper or explanation outside the JSON:
{{
  "improved_bullets": [
    {{
      "original": "<original weak bullet point from the resume>",
      "improved": "<improved bullet point using strong action verbs, STAR method, and quantitative results where possible>",
      "reason": "<reason for the change and why it is more impactful>"
    }}
  ],
  "formatting_suggestions": [<list of strings of specific layout, spacing, font, or section organization suggestions>],
  "project_suggestions": [<list of strings of 2-3 specific project ideas tailored to the candidate's skills that would boost their profile>]
}}

Resume Text:
{resume_text}
"""
