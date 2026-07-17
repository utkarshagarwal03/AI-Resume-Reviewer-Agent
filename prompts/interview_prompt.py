INTERVIEW_QUESTIONS_PROMPT = """
You are an expert technical interviewer.
Analyze the following resume and generate tailored interview questions to help the candidate prepare.
You must generate:
1. HR Questions (Behavioral/General)
2. Java Questions (Core Java, OOP, concurrency, collection framework)
3. DSA Questions (Data Structures and Algorithms)
4. SQL Questions (Database queries, Joins, Indexing, Transactions)
5. Project-based Questions (specific to the projects mentioned in the resume)

For each question, provide a short tip on the best approach to answer it.

Provide your output EXACTLY in the following JSON format:
{{
  "hr_questions": [
    {{
      "question": "<question string>",
      "best_approach": "<tip/strategy to answer>"
    }}
  ],
  "java_questions": [
    {{
      "question": "<question string>",
      "best_approach": "<tip/strategy to answer>"
    }}
  ],
  "dsa_questions": [
    {{
      "question": "<question string>",
      "best_approach": "<tip/strategy to answer>"
    }}
  ],
  "sql_questions": [
    {{
      "question": "<question string>",
      "best_approach": "<tip/strategy to answer>"
    }}
  ],
  "project_questions": [
    {{
      "question": "<question string>",
      "best_approach": "<tip/strategy to answer>"
    }}
  ]
}}

Resume Text:
{resume_text}
"""
