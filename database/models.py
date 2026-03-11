CREATE_ANNUAL_PLANS = """
CREATE TABLE IF NOT EXISTS annual_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    subject TEXT NOT NULL,
    year TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content TEXT NOT NULL
)
"""

CREATE_WEEKLY_SCHEDULE = """
CREATE TABLE IF NOT EXISTS weekly_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_of_week TEXT NOT NULL,
    time_slot TEXT NOT NULL,
    subject_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_GENERATED_MATERIALS = """
CREATE TABLE IF NOT EXISTS generated_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    material_type TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_PLAN_ENTRIES = """
CREATE TABLE IF NOT EXISTS plan_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    week_number TEXT,
    unit_topic TEXT,
    learning_outcomes TEXT,
    outcome_description TEXT,
    teaching_techniques TEXT,
    tools_equipment TEXT,
    assessment TEXT,
    special_days TEXT,
    FOREIGN KEY (plan_id) REFERENCES annual_plans(id)
)
"""

ALL_TABLES = [
    CREATE_ANNUAL_PLANS,
    CREATE_WEEKLY_SCHEDULE,
    CREATE_GENERATED_MATERIALS,
    CREATE_PLAN_ENTRIES,
]
