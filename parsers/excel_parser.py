import pandas as pd


class ExcelParser:
    COLUMN_KEYS = [
        "week_number",
        "unit_topic",
        "learning_outcomes",
        "outcome_description",
        "teaching_techniques",
        "tools_equipment",
        "assessment",
        "special_days",
    ]

    def parse(self, filepath):
        entries = []
        try:
            engine = "openpyxl"
            if str(filepath).lower().endswith(".xls"):
                engine = "xlrd"
            df = pd.read_excel(filepath, engine=engine, header=None, dtype=str)
            df = df.fillna("")
            start_row = 0
            if not df.empty:
                first_row_text = " ".join(str(v).strip().lower() for v in df.iloc[0])
                if any(
                    kw in first_row_text
                    for kw in ["hafta", "week", "ünite", "konu"]
                ):
                    start_row = 1
            for _, row in df.iloc[start_row:].iterrows():
                cells = [str(v).strip() for v in row.values]
                if all(c == "" or c == "nan" for c in cells):
                    continue
                cells = ["" if c == "nan" else c for c in cells]
                entry = self._cells_to_entry(cells)
                if entry:
                    entries.append(entry)
        except Exception as e:
            entries.append(
                {
                    "week_number": "Hata",
                    "unit_topic": f"Dosya okunamadı: {str(e)}",
                    "learning_outcomes": "",
                    "outcome_description": "",
                    "teaching_techniques": "",
                    "tools_equipment": "",
                    "assessment": "",
                    "special_days": "",
                }
            )
        return entries

    def _cells_to_entry(self, cells):
        while len(cells) < 8:
            cells.append("")
        entry = {}
        for i, key in enumerate(self.COLUMN_KEYS):
            entry[key] = cells[i] if i < len(cells) else ""
        if all(v == "" for v in entry.values()):
            return None
        return entry
