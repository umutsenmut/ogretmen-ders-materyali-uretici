import pdfplumber


class PdfParser:
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
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        if not table:
                            continue
                        # Detect header row
                        start_row = 0
                        if table[0]:
                            first_cell = str(table[0][0]).strip().lower()
                            if any(
                                kw in first_cell
                                for kw in ["hafta", "week", "ünite", "konu"]
                            ):
                                start_row = 1
                        for row in table[start_row:]:
                            if not row or all(
                                (cell is None or str(cell).strip() == "")
                                for cell in row
                            ):
                                continue
                            entry = self._row_to_entry(row)
                            if entry:
                                entries.append(entry)
                    # If no tables, fall back to text extraction
                    if not tables:
                        text = page.extract_text() or ""
                        for line in text.splitlines():
                            line = line.strip()
                            if line:
                                entries.append(
                                    {
                                        "week_number": "",
                                        "unit_topic": line,
                                        "learning_outcomes": "",
                                        "outcome_description": "",
                                        "teaching_techniques": "",
                                        "tools_equipment": "",
                                        "assessment": "",
                                        "special_days": "",
                                    }
                                )
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

    def _row_to_entry(self, row):
        cells = [str(c).strip() if c is not None else "" for c in row]
        # Pad or trim to 8 columns
        while len(cells) < 8:
            cells.append("")
        entry = {}
        for i, key in enumerate(self.COLUMN_KEYS):
            entry[key] = cells[i] if i < len(cells) else ""
        if all(v == "" for v in entry.values()):
            return None
        return entry
