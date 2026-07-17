ATS_ANALYSIS_PROMPT = """
You are an expert ATS (Applicant Tracking System) recruiter and resume analyzer.
Your task is to analyze the following resume text and provide a highly professional, detailed evaluation.

Provide your evaluation EXACTLY in the following JSON format. Do not add any markdown wrapper or explanation outside the JSON:
{{
  "ats_score": <int between 0 and 100>,
  "extracted_skills": [<list of strings of detected technical and soft skills>],
  "missing_skills": [<list of strings of skills that are typically expected for this profile but missing or weak>],
  "weak_sections": [<list of strings highlighting sections of the resume that need work>],
  "strengths": [<list of strings of the resume's strong points>],
  "weaknesses": [<list of strings of the resume's weak points or areas of improvement>],
  "summary": "<a concise 3-4 sentence professional summary of the candidate's profile>"
}}

Resume Text:
{resume_text}
"""
