import sqlite3
import json
from datetime import datetime
from database.models import ALL_TABLES


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            for ddl in ALL_TABLES:
                cursor.execute(ddl)
            conn.commit()
        finally:
            conn.close()

    def save_annual_plan(self, filename, subject, year, content):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO annual_plans (filename, subject, year, content) VALUES (?, ?, ?, ?)",
                (filename, subject, year, json.dumps(content, ensure_ascii=False)),
            )
            plan_id = cursor.lastrowid
            for entry in content:
                cursor.execute(
                    """INSERT INTO plan_entries
                       (plan_id, week_number, unit_topic, learning_outcomes,
                        outcome_description, teaching_techniques, tools_equipment,
                        assessment, special_days)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        plan_id,
                        entry.get("week_number", ""),
                        entry.get("unit_topic", ""),
                        entry.get("learning_outcomes", ""),
                        entry.get("outcome_description", ""),
                        entry.get("teaching_techniques", ""),
                        entry.get("tools_equipment", ""),
                        entry.get("assessment", ""),
                        entry.get("special_days", ""),
                    ),
                )
            conn.commit()
            return plan_id
        finally:
            conn.close()

    def get_all_plans(self):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, filename, subject, year, created_at FROM annual_plans ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_plan_by_id(self, plan_id):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM annual_plans WHERE id = ?", (plan_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            plan = dict(row)
            plan["content"] = json.loads(plan["content"])
            cursor.execute(
                "SELECT * FROM plan_entries WHERE plan_id = ? ORDER BY id",
                (plan_id,),
            )
            plan["entries"] = [dict(e) for e in cursor.fetchall()]
            return plan
        finally:
            conn.close()

    def save_weekly_schedule(self, day, time_slot, subject):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO weekly_schedule (day_of_week, time_slot, subject_name) VALUES (?, ?, ?)",
                (day, time_slot, subject),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_weekly_schedule(self):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM weekly_schedule ORDER BY day_of_week, time_slot"
            )
            rows = cursor.fetchall()
            schedule = {}
            for row in rows:
                d = dict(row)
                day = d["day_of_week"]
                if day not in schedule:
                    schedule[day] = []
                schedule[day].append(d)
            return schedule
        finally:
            conn.close()

    def delete_schedule_entry(self, entry_id):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM weekly_schedule WHERE id = ?", (entry_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def save_generated_material(self, subject, topic, material_type, content):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO generated_materials (subject, topic, material_type, content) VALUES (?, ?, ?, ?)",
                (subject, topic, material_type, json.dumps(content, ensure_ascii=False)),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_materials_by_subject(self, subject):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM generated_materials WHERE subject = ? ORDER BY created_at DESC",
                (subject,),
            )
            rows = cursor.fetchall()
            result = []
            for row in rows:
                m = dict(row)
                m["content"] = json.loads(m["content"])
                result.append(m)
            return result
        finally:
            conn.close()

    def get_all_materials(self):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, subject, topic, material_type, created_at FROM generated_materials ORDER BY created_at DESC"
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_material_by_id(self, material_id):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM generated_materials WHERE id = ?", (material_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return None
            m = dict(row)
            m["content"] = json.loads(m["content"])
            return m
        finally:
            conn.close()
