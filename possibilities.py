"""
All 50 StrokeCare possibilities with their fields,
system prompts, models, and validation rules.
"""

POSSIBILITIES = {
    "P1": {
        "name": "Personalised check-in question",
        "section": "Section 1 — Patient interaction",
        "model": "claude-haiku-4-5",
        "max_tokens": 120,
        "safety": True,
        "fields": [
            {
                "key": "patient_name",
                "label": "Patient first name",
                "type": "text",
                "required": True,
                "placeholder": "e.g. Priyanka",
            },
            {
                "key": "session_type",
                "label": "Session type",
                "type": "select",
                "required": True,
                "options": [
                    "Physio",
                    "Speech",
                    "Social",
                    "Blood test",
                    "Meds review",
                    "Hospital",
                    "Occupational",
                ],
            },
            {
                "key": "therapist_name",
                "label": "Therapist / person name",
                "type": "text",
                "required": False,
                "placeholder": "e.g. Mike (optional)",
            },
            {
                "key": "date_label",
                "label": "Session date",
                "type": "date",
                "required": True,
            },
            {
                "key": "feedback_logged",
                "label": "Feedback already logged?",
                "type": "select",
                "required": True,
                "options": ["No", "Yes"],
            },
        ],
        "preflight": {
            # Block 1 — already submitted
            "block_if": [
                {
                    "field": "feedback_logged",
                    "equals": "Yes",
                    "message": "Feedback already submitted for this session. No new check-in needed.",
                },
                # Block 2 — required fields missing (never call the model with empty inputs)
                {
                    "fields_empty": [
                        "patient_name",
                        "session_type",
                        "date_label",
                        "feedback_logged",
                    ],
                    "message": "Please fill in patient name, session type, and session date before continuing.",
                },
            ],
        },
        "system_prompt": """You are StrokeCare, a stroke recovery app.

Write ONE warm check-in question for the patient. Return ONLY the message text.

HARD RULES:
- Include patient's name
- Reference the session type (no clinical jargon)
- Exactly ONE question
- End with a tap instruction (vary wording: "tap below", "tap a face", etc.)
- Max 200 characters

DATE — today is {today_date}. Calculate gap, then write:
  0 days → "today"  |  1 day → "yesterday"
  2–6 days → day name e.g. "on Thursday"
  7+ days → full date e.g. "on 29 May"
  Never write the raw date. Never write "recently".

THERAPIST — include if given, omit entirely if blank.

TONE:
  Physio → effort, grit | Speech → patience, small wins | Social → warmth
  Blood test → wry, brief | Meds review → clarity, confidence
  Hospital → heavy, acknowledge effort | Occupational → practical wins

Make the patient feel seen, not processed.""",
        "user_prompt_template": """Patient: {patient_name}
Session type: {session_type}
Therapist: {therapist_name}
Session date: {date_label}
Feedback already logged: {feedback_logged}""",
        "validation": {
            "max_chars": 220,
            "question_marks": 1,
            "must_contain": [
                "patient_name"
            ],  # name must appear — structure can be anything
            "must_contain_any": [
                "session_type",
                "session_type_alias",
            ],  # "OT" counts for Occupational etc.
            "must_contain_word": "tap",  # tap instruction must be there, wording free
            "therapist_rule": {
                "if_provided": "should_include",  # soft check — warn, don't block
                "if_blank": "must_exclude_with",
            },
        },
        "fallback": "Hi {patient_name} — how did your {session_type} session go today? Tap below whenever you are ready.",
    },
    "P2": {
        "name": "Gentle response — patient scores low",
        "section": "Section 1 — Patient interaction",
        "model": "claude-sonnet-4-6",
        "max_tokens": 200,
        "safety": True,
        "fields": [
            {
                "key": "patient_name",
                "label": "Patient first name",
                "type": "text",
                "required": True,
                "placeholder": "e.g. Priyanka",
            },
            {
                "key": "session_type",
                "label": "Session type",
                "type": "select",
                "required": True,
                "options": ["Physio", "Speech", "Social", "Blood test", "Meds review"],
            },
            {
                "key": "score",
                "label": "Score just logged (1-4)",
                "type": "select",
                "required": True,
                "options": ["1", "2"],
            },
            {
                "key": "personal_avg",
                "label": "Personal average for this type",
                "type": "text",
                "required": True,
                "placeholder": "e.g. 2.8",
            },
            {
                "key": "is_lowest_ever",
                "label": "Is this lowest ever score?",
                "type": "select",
                "required": True,
                "options": ["Yes", "No"],
            },
        ],
        "system_prompt": """You are StrokeCare, a compassionate recovery support platform.
    A patient has just logged a low mood score after their session.
    Write an empathetic 2-3 sentence response.
    Rules:
    (1) Acknowledge the difficulty directly — do not minimise
    (2) NEVER use: don't worry, you'll be fine, stay positive, cheer up
    (3) Confirm care team has been notified
    (4) If is_lowest_ever is Yes — acknowledge this gently
    (5) Warm human tone — not clinical
    (6) Under 250 characters
    Return ONLY the response text.""",
        "user_prompt_template": """Patient: {patient_name}
    Session: {session_type}
    Score just logged: {score} (scale 1-4, 1=very hard)
    Personal average for this type: {personal_avg}
    Is this their lowest ever score: {is_lowest_ever}""",
        "validation": {
            "max_chars": 250,
            "prohibited": [
                "don't worry",
                "you'll be fine",
                "stay positive",
                "cheer up",
            ],
        },
        "fallback": "That sounds like a really hard session, {patient_name}. Your care team has been notified and someone will be in touch soon.",
    },
    "P3": {
        "name": "Answer a patient question",
        "section": "Section 1 — Patient interaction",
        "model": "claude-sonnet-4-6",
        "max_tokens": 250,
        "safety": True,
        "fields": [
            {
                "key": "patient_name",
                "label": "Patient first name",
                "type": "text",
                "required": True,
                "placeholder": "e.g. Priyanka",
            },
            {
                "key": "question",
                "label": "Patient's question",
                "type": "textarea",
                "required": True,
                "placeholder": "e.g. Is it normal to feel exhausted after speech therapy?",
            },
            {
                "key": "recovery_week",
                "label": "Recovery week number",
                "type": "text",
                "required": True,
                "placeholder": "e.g. 14",
            },
            {
                "key": "recent_session",
                "label": "Most recent session",
                "type": "text",
                "required": False,
                "placeholder": "e.g. Speech therapy yesterday, score 2",
            },
        ],
        "system_prompt": """You are StrokeCare, a recovery support assistant for stroke patients.
    Answer the patient's question in plain English specific to stroke recovery.
    Rules:
    (1) Reassuring but honest — do not over-promise recovery
    (2) Under 120 words
    (3) Reference their recovery stage where relevant
    (4) Suggest speaking to therapist for clinical questions
    (5) No medical diagnosis language
    Return ONLY the answer text.""",
        "user_prompt_template": """Patient: {patient_name}
    Question: {question}
    Recovery week: {recovery_week}
    Most recent session: {recent_session}""",
        "validation": {"max_words": 120},
        "fallback": "That's a great question, {patient_name}. Please speak to your care team at your next session — they'll be able to give you the best advice for your specific recovery.",
    },
    "P4": {
        "name": "Motivational message — positive streak",
        "section": "Section 1 — Patient interaction",
        "model": "claude-haiku-4-5",
        "max_tokens": 150,
        "safety": False,
        "fields": [
            {
                "key": "patient_name",
                "label": "Patient first name",
                "type": "text",
                "required": True,
                "placeholder": "e.g. Priyanka",
            },
            {
                "key": "streak_days",
                "label": "Consecutive days logged",
                "type": "text",
                "required": True,
                "placeholder": "e.g. 10",
            },
            {
                "key": "this_week_avg",
                "label": "This week average score",
                "type": "text",
                "required": True,
                "placeholder": "e.g. 2.9",
            },
            {
                "key": "four_weeks_ago",
                "label": "Four weeks ago average",
                "type": "text",
                "required": True,
                "placeholder": "e.g. 1.8",
            },
        ],
        "system_prompt": """You are StrokeCare. Write a short genuine motivational message for a patient who has been consistent.
    Rules:
    (1) Reference the exact streak number
    (2) Reference the mood improvement using the actual numbers
    (3) Under 80 words
    (4) Warm and genuine — not generic
    Return ONLY the message text.""",
        "user_prompt_template": """Patient: {patient_name}
    Consecutive days logged: {streak_days}
    This week average: {this_week_avg}
    Four weeks ago average: {four_weeks_ago}""",
        "validation": {"max_words": 80},
        "fallback": "Great work {patient_name} — {streak_days} days in a row. Keep it up!",
    },
    "P5": {
        "name": "Response to distressed note",
        "section": "Section 1 — Patient interaction",
        "model": "claude-sonnet-4-6",
        "max_tokens": 200,
        "safety": True,
        "fields": [
            {
                "key": "patient_name",
                "label": "Patient first name",
                "type": "text",
                "required": True,
                "placeholder": "e.g. Priyanka",
            },
            {
                "key": "note_text",
                "label": "Patient note text",
                "type": "textarea",
                "required": True,
                "placeholder": "e.g. I just feel like I am never going to get better",
            },
            {
                "key": "score",
                "label": "Most recent score (1-4)",
                "type": "select",
                "required": True,
                "options": ["1", "2", "3", "4"],
            },
            {
                "key": "after_8pm",
                "label": "Is it after 8pm?",
                "type": "select",
                "required": True,
                "options": ["No", "Yes"],
            },
        ],
        "system_prompt": """You are StrokeCare, a compassionate care platform.
    A patient has written a distressed note. Write an empathetic 2-3 sentence response.
    PROHIBITED: 'don't worry', 'you'll be fine', 'stay positive', 'the platform flagged you'
    Rules:
    (1) Acknowledge their feeling directly — name what they said
    (2) Do NOT minimise or offer solutions
    (3) Confirm care team has been notified
    (4) If after_8pm is Yes — say someone will be in touch tomorrow morning
    (5) Warm human tone
    Return ONLY the response text.""",
        "user_prompt_template": """Patient: {patient_name}
    Note text: {note_text}
    Score: {score}
    After 8pm: {after_8pm}""",
        "validation": {
            "prohibited": [
                "don't worry",
                "you'll be fine",
                "stay positive",
                "the platform flagged you",
            ]
        },
        "fallback": "Thank you for writing that down, {patient_name}. Your care team has been notified and someone will be in touch soon. You are not going through this alone.",
    },
    "P6": {
        "name": "Appointment reminder with advice",
        "section": "Section 1 — Patient interaction",
        "model": "claude-haiku-4-5",
        "max_tokens": 150,
        "safety": False,
        "fields": [
            {
                "key": "patient_name",
                "label": "Patient first name",
                "type": "text",
                "required": True,
                "placeholder": "e.g. Priyanka",
            },
            {
                "key": "appt_type",
                "label": "Appointment type",
                "type": "select",
                "required": True,
                "options": [
                    "Physio",
                    "Speech",
                    "Social",
                    "Blood test",
                    "Meds review",
                    "Hospital",
                ],
            },
            {
                "key": "therapist_name",
                "label": "Therapist name",
                "type": "text",
                "required": False,
                "placeholder": "e.g. Mike",
            },
            {
                "key": "appt_time",
                "label": "Appointment date & time",
                "type": "datetime",
                "required": True,
            },
            {
                "key": "avg_score",
                "label": "Avg score for this type",
                "type": "text",
                "required": True,
                "placeholder": "e.g. 2.8",
            },
            {
                "key": "last_score",
                "label": "Last score for this type",
                "type": "text",
                "required": True,
                "placeholder": "e.g. 2",
            },
        ],
        "system_prompt": """You are StrokeCare. Write a personalised appointment reminder with one specific preparation tip.
    Rules:
    (1) Include appointment time and therapist name
    (2) One specific preparation tip based on their data
    (3) Brief encouraging close
    (4) Under 120 words
    Return ONLY the reminder text.""",
        "user_prompt_template": """Patient: {patient_name}
    Appointment: {appt_type} with {therapist_name} at {appt_time}
    Average score for this type: {avg_score}
    Last score: {last_score}""",
        "validation": {"max_words": 120},
        "fallback": "Just a reminder {patient_name} — {appt_type} is {appt_time}. Try to rest well beforehand. You can do this.",
    },
    "P7": {
        "name": "Weekly mood summary for carer",
        "section": "Section 2 — Mood pattern detection",
        "model": "claude-sonnet-4-6",
        "max_tokens": 200,
        "safety": False,
        "fields": [
            {
                "key": "patient_name",
                "label": "Patient first name",
                "type": "text",
                "required": True,
                "placeholder": "e.g. Priyanka",
            },
            {
                "key": "scores_summary",
                "label": "Scores this week",
                "type": "textarea",
                "required": True,
                "placeholder": "e.g. Physio 2, Social 4, Meds review 1, Physio 2, Speech 2",
            },
            {
                "key": "weekly_avg",
                "label": "Weekly average",
                "type": "text",
                "required": True,
                "placeholder": "e.g. 2.2",
            },
            {
                "key": "baseline",
                "label": "Personal baseline",
                "type": "text",
                "required": True,
                "placeholder": "e.g. 2.8",
            },
            {
                "key": "completed",
                "label": "Check-ins completed / total",
                "type": "text",
                "required": True,
                "placeholder": "e.g. 5 of 5",
            },
        ],
        "system_prompt": """You are StrokeCare. Write a concise weekly mood summary for a patient's carer.
    Rules:
    (1) One paragraph, maximum 80 words
    (2) These values MUST appear: weekly average, best session, worst session, completion rate
    (3) Factual and observational — no clinical diagnosis
    (4) If possible based on data give observation also
    Return ONLY the paragraph text.""",
        "user_prompt_template": """Patient: {patient_name}
    Scores this week: {scores_summary}
    Weekly average: {weekly_avg}
    Personal baseline: {baseline}
    Check-ins completed: {completed}""",
        "validation": {"max_words": 80},
        "fallback": "This week {patient_name} completed {completed} check-ins with a weekly average of {weekly_avg}, compared to their baseline of {baseline}.",
    },  
    
    #  "P10": {
    #         "name": "Long-term downward trend detection",
    #         "section": "Section 2 — Mood pattern detection",
    #         "model": "claude-sonnet-4-6",
    #         "max_tokens": 150,
    #         "safety": False,
    #         "fields": [
    #             {
    #                 "key": "patient_name",
    #                 "label": "Patient first name",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. Priyanka",
    #             },
    #             {
    #                 "key": "weekly_avgs",
    #                 "label": "Weekly averages (oldest first)",
    #                 "type": "textarea",
    #                 "required": True,
    #                 "placeholder": "e.g. 3.1, 2.9, 2.7, 2.4, 2.2, 2.0, 1.9, 1.7",
    #             },
    #             {
    #                 "key": "consecutive",
    #                 "label": "Consecutive declining weeks",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 8",
    #             },
    #             {
    #                 "key": "current_avg",
    #                 "label": "Current average",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 1.7",
    #             },
    #             {
    #                 "key": "baseline",
    #                 "label": "Patient baseline",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 3.0",
    #             },
    #             {
    #                 "key": "severity",
    #                 "label": "Severity level",
    #                 "type": "select",
    #                 "required": True,
    #                 "options": ["concern", "urgent", "critical"],
    #             },
    #         ],
    #         "system_prompt": """You are StrokeCare. Write a clear trend statement for a patient's care team.
    # Rules:
    # (1) State the consecutive declining weeks precisely
    # (2) State the delta from baseline precisely
    # (3) Give a recommended action appropriate to severity
    # (4) Do not diagnose — recommend clinical review
    # (5) Under 80 words
    # Return ONLY the statement text.""",
    #         "user_prompt_template": """Patient: {patient_name}
    # Weekly averages (oldest first): {weekly_avgs}
    # Consecutive declining weeks: {consecutive}
    # Current average: {current_avg}
    # Baseline: {baseline}
    # Severity: {severity}""",
    #         "validation": {"max_words": 80},
    #         "fallback": "{patient_name}'s mood has declined for {consecutive} consecutive weeks. Current average is {current_avg}, below their baseline of {baseline}. Clinical review recommended.",
    #     },
    #     "P21": {
    #         "name": "High priority carer alert",
    #         "section": "Section 4 — Clinical alerts",
    #         "model": "claude-sonnet-4-6",
    #         "max_tokens": 200,
    #         "safety": True,
    #         "fields": [
    #             {
    #                 "key": "patient_name",
    #                 "label": "Patient first name",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. Priyanka",
    #             },
    #             {
    #                 "key": "pattern",
    #                 "label": "Pattern detected",
    #                 "type": "textarea",
    #                 "required": True,
    #                 "placeholder": "e.g. Physio score drops after meds review",
    #             },
    #             {
    #                 "key": "occurrences",
    #                 "label": "Occurrences out of total",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 4 of 4",
    #             },
    #             {
    #                 "key": "action_type",
    #                 "label": "Recommended action type",
    #                 "type": "select",
    #                 "required": True,
    #                 "options": [
    #                     "GP contact",
    #                     "Carer check-in",
    #                     "Diary change",
    #                     "Speech therapist",
    #                     "Neurologist",
    #                 ],
    #             },
    #         ],
    #         "system_prompt": """You are StrokeCare. Write a HIGH PRIORITY alert for a patient's carer.
    # Output MUST start with: HIGH PRIORITY —
    # Rules:
    # (1) Name the specific pattern detected
    # (2) State exactly how many times it has occurred
    # (3) Give ONE specific recommended action for this week
    # (4) Direct tone — this requires action
    # (5) Under 80 words
    # Return ONLY the alert text starting with HIGH PRIORITY —""",
    #         "user_prompt_template": """Patient: {patient_name}
    # Pattern: {pattern}
    # Occurrences: {occurrences}
    # Recommended action type: {action_type}""",
    #         "validation": {"starts_with": "HIGH PRIORITY", "max_words": 80},
    #         "fallback": "HIGH PRIORITY — {patient_name} has shown a consistent pattern: {pattern} on {occurrences} occasions. Action required this week: {action_type}.",
    #     },
    #     "P22": {
    #         "name": "Post-stroke depression clinical alert",
    #         "section": "Section 4 — Clinical alerts",
    #         "model": "claude-sonnet-4-6",
    #         "max_tokens": 200,
    #         "safety": True,
    #         "fields": [
    #             {
    #                 "key": "patient_name",
    #                 "label": "Patient first name",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. Priyanka",
    #             },
    #             {
    #                 "key": "five_week_avg",
    #                 "label": "5-week mood average",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 1.5",
    #             },
    #             {
    #                 "key": "baseline",
    #                 "label": "Patient baseline",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 2.9",
    #             },
    #             {
    #                 "key": "engagement_drop",
    #                 "label": "Engagement drop %",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 65",
    #             },
    #             {
    #                 "key": "distress_words",
    #                 "label": "Distress words in notes",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. tired, struggling, pointless",
    #             },
    #             {
    #                 "key": "still_declining",
    #                 "label": "Still declining?",
    #                 "type": "select",
    #                 "required": True,
    #                 "options": ["Yes", "No"],
    #             },
    #         ],
    #         "system_prompt": """You are StrokeCare. Write a clinical alert for a patient's GP or clinician.
    # Output MUST start with: CLINICAL ALERT —
    # Rules:
    # (1) Report evidence across all four signals
    # (2) Recommend formal depression screening — do NOT diagnose
    # (3) Specify: next available appointment, not the next scheduled one
    # (4) Professional clinical language
    # (5) Under 100 words
    # (6) Never use 'depression' as a diagnosis — only as a screening recommendation
    # Return ONLY the alert text starting with CLINICAL ALERT —""",
    #         "user_prompt_template": """Patient: {patient_name}
    # 5-week mood average: {five_week_avg} (baseline: {baseline})
    # Engagement drop: {engagement_drop}%
    # Distress language detected: {distress_words}
    # Direction: {still_declining}""",
    #         "validation": {
    #             "starts_with": "CLINICAL ALERT",
    #             "prohibited_in_output": ["you are depressed", "the patient is depressed"],
    #         },
    #         "fallback": "CLINICAL ALERT — {patient_name}'s mood has averaged {five_week_avg} over 5 weeks against a baseline of {baseline}. Formal depression screening conversation with the GP is recommended this week.",
    #     },
    #     "P26": {
    #         "name": "First ever lowest score alert",
    #         "section": "Section 4 — Clinical alerts",
    #         "model": "claude-sonnet-4-6",
    #         "max_tokens": 150,
    #         "safety": True,
    #         "fields": [
    #             {
    #                 "key": "patient_name",
    #                 "label": "Patient first name",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. Priyanka",
    #             },
    #             {
    #                 "key": "score",
    #                 "label": "Score just logged",
    #                 "type": "select",
    #                 "required": True,
    #                 "options": ["1", "2"],
    #             },
    #             {
    #                 "key": "previous_min",
    #                 "label": "Previous all-time lowest",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 2",
    #             },
    #             {
    #                 "key": "session_date",
    #                 "label": "Date score was logged",
    #                 "type": "date",
    #                 "required": True,
    #             },
    #             {
    #                 "key": "note_text",
    #                 "label": "Patient note (if any)",
    #                 "type": "textarea",
    #                 "required": False,
    #                 "placeholder": "e.g. Terrible day. Nothing feels worth it.",
    #             },
    #             {
    #                 "key": "after_8pm",
    #                 "label": "Is it after 8pm?",
    #                 "type": "select",
    #                 "required": True,
    #                 "options": ["No", "Yes"],
    #             },
    #         ],
    #         "system_prompt": """You are StrokeCare. Write an immediate alert for a patient's carer.
    # Output MUST start with: ALERT —
    # Rules:
    # (1) State this is outside their established range
    # (2) If note present — reference the key phrase (3-5 words max)
    # (3) Specify: this evening if after 8pm, today if daytime
    # (4) Urgent but not panicked
    # (5) Under 70 words
    # Return ONLY the alert text starting with ALERT —""",
    #         "user_prompt_template": """Patient: {patient_name}
    # Score just logged: {score}
    # Previous all-time lowest: {previous_min}
    # Note: {note_text}
    # After 8pm: {after_8pm}""",
    #         "validation": {"starts_with": "ALERT", "max_words": 70},
    #         "fallback": "ALERT — {patient_name} has just logged a score of {score} for the first time in their history. Their carer should be contacted today. This is not a routine low score.",
    #     },
    #     "P33": {
    #         "name": "Monthly progress report — care team",
    #         "section": "Section 6 — Progress reporting",
    #         "model": "claude-sonnet-4-6",
    #         "max_tokens": 300,
    #         "safety": False,
    #         "fields": [
    #             {
    #                 "key": "patient_name",
    #                 "label": "Patient first name",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. Priyanka",
    #             },
    #             {
    #                 "key": "month_name",
    #                 "label": "Month",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. April",
    #             },
    #             {
    #                 "key": "completed",
    #                 "label": "Sessions completed/total",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 14 of 16",
    #             },
    #             {
    #                 "key": "monthly_avg",
    #                 "label": "Monthly average",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 2.4",
    #             },
    #             {
    #                 "key": "prev_avg",
    #                 "label": "Previous month average",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 2.9",
    #             },
    #             {
    #                 "key": "best_type",
    #                 "label": "Best session type",
    #                 "type": "select",
    #                 "required": True,
    #                 "options": ["Social", "Physio", "Speech", "Blood test", "Meds review"],
    #             },
    #             {
    #                 "key": "best_avg",
    #                 "label": "Best session avg",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 3.9",
    #             },
    #             {
    #                 "key": "worst_type",
    #                 "label": "Worst session type",
    #                 "type": "select",
    #                 "required": True,
    #                 "options": ["Meds review", "Blood test", "Speech", "Physio", "Social"],
    #             },
    #             {
    #                 "key": "worst_avg",
    #                 "label": "Worst session avg",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 1.5",
    #             },
    #             {
    #                 "key": "alerts_summary",
    #                 "label": "Key alerts this month",
    #                 "type": "textarea",
    #                 "required": False,
    #                 "placeholder": "e.g. Medication-physio correlation confirmed",
    #             },
    #         ],
    #         "system_prompt": """You are StrokeCare. Write a monthly progress report for a patient's care team.
    # Rules:
    # (1) All key numbers MUST appear verbatim in the output
    # (2) Cover: sessions, overall average vs previous, best/worst session types
    # (3) Summarise any key alerts or patterns
    # (4) End with ONE recommended focus for next month
    # (5) Under 150 words
    # Return ONLY the report text.""",
    #         "user_prompt_template": """Patient: {patient_name}
    # Month: {month_name}
    # Sessions: {completed}
    # Monthly average: {monthly_avg}
    # Previous month: {prev_avg}
    # Best session: {best_type} at {best_avg}
    # Worst session: {worst_type} at {worst_avg}
    # Alerts this month: {alerts_summary}""",
    #         "validation": {"max_words": 150},
    #         "fallback": "{patient_name} — {month_name} summary. Sessions: {completed}. Average: {monthly_avg} vs {prev_avg} last month. Best: {best_type}. Worst: {worst_type}.",
    #     },
    #     "P44": {
    #         "name": "Personal medication impact profile",
    #         "section": "Section 9 — Medication & clinical intelligence",
    #         "model": "claude-sonnet-4-6",
    #         "max_tokens": 250,
    #         "safety": False,
    #         "fields": [
    #             {
    #                 "key": "patient_name",
    #                 "label": "Patient first name",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. Priyanka",
    #             },
    #             {
    #                 "key": "event_count",
    #                 "label": "Medication events analysed",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 8",
    #             },
    #             {
    #                 "key": "months",
    #                 "label": "Months of data",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 6",
    #             },
    #             {
    #                 "key": "avg_drop",
    #                 "label": "Average score drop per event",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 1.2",
    #             },
    #             {
    #                 "key": "avg_duration",
    #                 "label": "Duration of impact (days)",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 2 to 3",
    #             },
    #             {
    #                 "key": "affected_types",
    #                 "label": "Most affected session types",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. Physio, Speech",
    #             },
    #             {
    #                 "key": "consistency",
    #                 "label": "Consistency %",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 100",
    #             },
    #             {
    #                 "key": "return_days",
    #                 "label": "Days to return to baseline",
    #                 "type": "text",
    #                 "required": True,
    #                 "placeholder": "e.g. 4 to 5",
    #             },
    #         ],
    #         "system_prompt": """You are StrokeCare. Write a personalised medication impact profile for a patient's prescribing doctor.
    # Rules:
    # (1) All values must be specific to this patient
    # (2) End with: This profile should be shared with the prescribing doctor as real-world evidence of medication impact on daily function.
    # (3) Do NOT recommend stopping or adjusting medication
    # (4) Professional clinical framing
    # (5) Under 150 words
    # Return ONLY the profile text.""",
    #         "user_prompt_template": """Patient: {patient_name}
    # Events analysed: {event_count} medication events over {months} months
    # Average score drop: {avg_drop} points
    # Duration of impact: {avg_duration} days
    # Most affected session types: {affected_types}
    # Consistency: {consistency}% of events show this pattern
    # Days to return to baseline: {return_days}""",
    #         "validation": {
    #             "max_words": 150,
    #             "prohibited": [
    #                 "stop the medication",
    #                 "reduce the dose",
    #                 "increase the dose",
    #             ],
    #         },
    #         "fallback": "Medication impact profile for {patient_name}: following each medication event, mood drops an average of {avg_drop} points for {avg_duration} days. This has been consistent across {consistency}% of {event_count} events.",
    #     },
        "P50": {
            "name": "Full patient handover document",
            "section": "Section 10 — Future possibilities",
            "model": "claude-opus-4-6",
            "max_tokens": 600,
            "safety": False,
            "fields": [
                {
                    "key": "patient_name",
                    "label": "Patient first name",
                    "type": "text",
                    "required": True,
                    "placeholder": "e.g. Priyanka",
                },
                {
                    "key": "months_on",
                    "label": "Months on platform",
                    "type": "text",
                    "required": True,
                    "placeholder": "e.g. 14",
                },
                {
                    "key": "top_predictor",
                    "label": "Strongest mood predictor",
                    "type": "text",
                    "required": True,
                    "placeholder": "e.g. Social visits with Sarah",
                },
                {
                    "key": "med_profile",
                    "label": "Medication impact summary",
                    "type": "textarea",
                    "required": True,
                    "placeholder": "e.g. Reviews cause 48-72hr mood drop, recovery in 4-5 days",
                },
                {
                    "key": "best_schedule",
                    "label": "Best therapy schedule",
                    "type": "textarea",
                    "required": True,
                    "placeholder": "e.g. Physio best Wed/Thu mornings, avoid Monday",
                },
                {
                    "key": "speech_trend",
                    "label": "Speech therapy trend",
                    "type": "text",
                    "required": True,
                    "placeholder": "e.g. Strongest improvement, 1.6 to 2.9",
                },
                {
                    "key": "comms_style",
                    "label": "Communication style notes",
                    "type": "textarea",
                    "required": True,
                    "placeholder": "e.g. Responds best to warm informal first-name contact",
                },
            ],
            "system_prompt": """You are StrokeCare. Write a comprehensive patient handover document for a new care team.
    Sections required: Essential Knowledge, Scheduling Preferences, Medication Profile, Social Support, Communication Style
    Rules:
    (1) Each section: 2-4 sentences, specific and evidence-based
    (2) Essential Knowledge must come first
    (3) Plain English — readable by any clinician
    (4) Under 400 words
    Return ONLY the handover document.""",
            "user_prompt_template": """Patient: {patient_name}
    Months on platform: {months_on}
    Strongest mood predictor: {top_predictor}
    Medication impact: {med_profile}
    Scheduling preferences: {best_schedule}
    Speech therapy trend: {speech_trend}
    Communication style: {comms_style}""",
            "validation": {"max_words": 400},
            "fallback": "Patient handover — {patient_name}. {months_on} months on StrokeCare. Key predictor: {top_predictor}. See detailed records for full profile.",
        },
}

# Sections for sidebar grouping
SECTIONS = [
    "Section 1 — Patient interaction",
    "Section 2 — Mood pattern detection",
    "Section 4 — Clinical alerts",
    "Section 6 — Progress reporting",
    "Section 9 — Medication & clinical intelligence",
    "Section 10 — Future possibilities",
]
