import os
import json
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    send_file,
    flash,
)
from werkzeug.utils import secure_filename
import io

from config import Config
from database.db_manager import DatabaseManager
from parsers.pdf_parser import PdfParser
from parsers.word_parser import WordParser
from parsers.excel_parser import ExcelParser
from generators.flashcard_generator import FlashcardGenerator
from generators.presentation_generator import PresentationGenerator
from generators.test_generator import TestGenerator
from generators.notes_generator import NotesGenerator
from exporters.pdf_exporter import PdfExporter
from exporters.word_exporter import WordExporter

app = Flask(__name__)
app.config.from_object(Config)

db = DatabaseManager(app.config["DATABASE_PATH"])
db.init_db()

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


# ──────────────────────────────────────────────
# Main pages
# ──────────────────────────────────────────────

@app.route("/")
def index():
    plans = db.get_all_plans()
    materials = db.get_all_materials()
    schedule = db.get_weekly_schedule()
    total_lessons = sum(len(v) for v in schedule.values())
    return render_template(
        "index.html",
        plan_count=len(plans),
        material_count=len(materials),
        lesson_count=total_lessons,
    )


@app.route("/upload-plan", methods=["GET"])
def upload_plan_page():
    plans = db.get_all_plans()
    return render_template("upload_plan.html", plans=plans)


@app.route("/upload-plan", methods=["POST"])
def upload_plan():
    if "file" not in request.files:
        return jsonify({"error": "Dosya seçilmedi"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Dosya adı boş"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Desteklenmeyen dosya türü. Lütfen PDF, DOCX veya XLSX yükleyin."}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    subject = request.form.get("subject", "Genel")
    year = request.form.get("year", "2024-2025")

    ext = filename.rsplit(".", 1)[1].lower()
    try:
        if ext == "pdf":
            parser = PdfParser()
        elif ext == "docx":
            parser = WordParser()
        else:
            parser = ExcelParser()

        content = parser.parse(filepath)
        plan_id = db.save_annual_plan(filename, subject, year, content)

        return jsonify(
            {
                "success": True,
                "plan_id": plan_id,
                "filename": filename,
                "entry_count": len(content),
                "message": f"Plan başarıyla yüklendi. {len(content)} kayıt eklendi.",
            }
        )
    except Exception as e:
        return jsonify({"error": f"Dosya işlenirken hata oluştu: {str(e)}"}), 500


# ──────────────────────────────────────────────
# Plans API
# ──────────────────────────────────────────────

@app.route("/api/plans")
def api_plans():
    plans = db.get_all_plans()
    return jsonify(plans)


@app.route("/api/plans/<int:plan_id>")
def api_plan_detail(plan_id):
    plan = db.get_plan_by_id(plan_id)
    if plan is None:
        return jsonify({"error": "Plan bulunamadı"}), 404
    return jsonify(plan)


# ──────────────────────────────────────────────
# Schedule
# ──────────────────────────────────────────────

@app.route("/schedule")
def schedule_page():
    schedule = db.get_weekly_schedule()
    return render_template("schedule.html", schedule=schedule)


@app.route("/api/schedule")
def api_schedule():
    schedule = db.get_weekly_schedule()
    return jsonify(schedule)


@app.route("/api/schedule", methods=["POST"])
def api_schedule_add():
    data = request.get_json(force=True)
    day = data.get("day_of_week", "").strip()
    time_slot = data.get("time_slot", "").strip()
    subject = data.get("subject_name", "").strip()

    if not day or not time_slot or not subject:
        return jsonify({"error": "Gün, saat ve ders adı gereklidir"}), 400

    entry_id = db.save_weekly_schedule(day, time_slot, subject)
    return jsonify({"success": True, "id": entry_id})


@app.route("/api/schedule/<int:entry_id>", methods=["DELETE"])
def api_schedule_delete(entry_id):
    deleted = db.delete_schedule_entry(entry_id)
    if not deleted:
        return jsonify({"error": "Kayıt bulunamadı"}), 404
    return jsonify({"success": True})


# ──────────────────────────────────────────────
# Generate
# ──────────────────────────────────────────────

@app.route("/generate")
def generate_page():
    plans = db.get_all_plans()
    return render_template("generate.html", plans=plans)


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json(force=True)
    subject = data.get("subject", "").strip()
    topic = data.get("topic", "").strip()
    learning_outcomes = data.get("learning_outcomes", "").strip()
    material_types = data.get("material_types", [])

    if not subject or not topic:
        return jsonify({"error": "Ders adı ve konu gereklidir"}), 400

    if not material_types:
        return jsonify({"error": "En az bir materyal türü seçin"}), 400

    api_key = app.config.get("OPENAI_API_KEY", "")
    results = {}

    type_map = {
        "flashcards": (FlashcardGenerator, "Bilgi Kartları"),
        "presentation": (PresentationGenerator, "Sunum"),
        "test": (TestGenerator, "Test"),
        "notes": (NotesGenerator, "Öğretmen Notları"),
    }

    generated_ids = {}

    for mtype in material_types:
        if mtype not in type_map:
            continue
        gen_class, display_name = type_map[mtype]
        generator = gen_class()
        content = generator.generate(subject, topic, learning_outcomes, api_key)
        material_id = db.save_generated_material(subject, topic, display_name, content)
        results[mtype] = {"id": material_id, "data": content}
        generated_ids[mtype] = material_id

    return jsonify({"success": True, "materials": results})


# ──────────────────────────────────────────────
# Materials API
# ──────────────────────────────────────────────

@app.route("/api/materials")
def api_materials():
    materials = db.get_all_materials()
    return jsonify(materials)


@app.route("/api/materials/<int:material_id>")
def api_material_detail(material_id):
    material = db.get_material_by_id(material_id)
    if material is None:
        return jsonify({"error": "Materyal bulunamadı"}), 404
    return jsonify(material)


@app.route("/preview/<int:material_id>")
def preview(material_id):
    material = db.get_material_by_id(material_id)
    if material is None:
        flash("Materyal bulunamadı", "danger")
        return redirect(url_for("index"))
    return render_template("preview.html", material=material)


# ──────────────────────────────────────────────
# Download
# ──────────────────────────────────────────────

@app.route("/download/<int:material_id>/<fmt>")
def download(material_id, fmt):
    material = db.get_material_by_id(material_id)
    if material is None:
        return jsonify({"error": "Materyal bulunamadı"}), 404

    subject = material.get("subject", "Ders")
    topic = material.get("topic", "Konu")
    material_type = material.get("material_type", "Materyal")
    content = material.get("content", {})

    safe_name = f"{subject}_{topic}".replace(" ", "_")[:50]

    if fmt == "pdf":
        exporter = PdfExporter()
        if material_type == "Bilgi Kartları":
            data = exporter.export_flashcards(content.get("cards", []), subject, topic)
        elif material_type == "Sunum":
            data = exporter.export_presentation(content.get("slides", []), subject, topic)
        elif material_type == "Test":
            data = exporter.export_test(content, subject, topic)
        else:
            data = exporter.export_notes(content, subject, topic)
        return send_file(
            io.BytesIO(data),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{safe_name}.pdf",
        )

    elif fmt == "docx":
        exporter = WordExporter()
        if material_type == "Test":
            data = exporter.export_test(content, subject, topic)
        else:
            data = exporter.export_notes(content, subject, topic)
        return send_file(
            io.BytesIO(data),
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name=f"{safe_name}.docx",
        )

    elif fmt == "txt":
        text = _content_to_text(material_type, content, subject, topic)
        return send_file(
            io.BytesIO(text.encode("utf-8")),
            mimetype="text/plain; charset=utf-8",
            as_attachment=True,
            download_name=f"{safe_name}.txt",
        )

    elif fmt == "html":
        html = _content_to_html(material_type, content, subject, topic)
        return send_file(
            io.BytesIO(html.encode("utf-8")),
            mimetype="text/html; charset=utf-8",
            as_attachment=True,
            download_name=f"{safe_name}.html",
        )

    return jsonify({"error": "Desteklenmeyen format"}), 400


def _content_to_text(material_type, content, subject, topic):
    lines = [f"{subject} - {topic}", f"Materyal Türü: {material_type}", "=" * 60, ""]
    if material_type == "Bilgi Kartları":
        for card in content.get("cards", []):
            lines.append(f"Kart {card.get('id', '')}")
            lines.append(f"  Ön: {card.get('front', '')}")
            lines.append(f"  Arka: {card.get('back', '')}")
            lines.append("")
    elif material_type == "Sunum":
        for slide in content.get("slides", []):
            lines.append(f"Slayt {slide.get('slide_number', '')}: {slide.get('title', '')}")
            for item in slide.get("content", []):
                lines.append(f"  • {item}")
            lines.append(f"  Görsel: {slide.get('visual_suggestion', '')}")
            lines.append("")
    elif material_type == "Test":
        for i, q in enumerate(content.get("multiple_choice", []), 1):
            lines.append(f"{i}. {q.get('question', '')}")
            for k, v in q.get("options", {}).items():
                lines.append(f"   {k}) {v}")
            lines.append(f"   Cevap: {q.get('correct_answer', '')}")
            lines.append("")
        for i, q in enumerate(content.get("open_ended", []), 1):
            lines.append(f"Açık Uçlu {i}: {q.get('question', '')}")
            lines.append("")
    else:
        lines.append(content.get("title", ""))
        lines.append("")
        for c in content.get("main_concepts", []):
            lines.append(f"• {c}")
        lines.append("")
        lines.append(content.get("detailed_explanation", ""))
    return "\n".join(lines)


def _content_to_html(material_type, content, subject, topic):
    parts = [
        "<!DOCTYPE html><html lang='tr'><head><meta charset='UTF-8'>",
        "<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css'>",
        f"<title>{subject} - {topic}</title></head><body class='container py-4'>",
        f"<h1>{subject} - {topic}</h1><h4 class='text-muted'>{material_type}</h4><hr>",
    ]
    if material_type == "Bilgi Kartları":
        parts.append("<div class='row'>")
        for card in content.get("cards", []):
            parts.append(
                f"<div class='col-md-6 mb-3'><div class='card'>"
                f"<div class='card-header bg-primary text-white'>Kart {card.get('id','')} - Ön Yüz</div>"
                f"<div class='card-body'><p>{card.get('front','')}</p></div>"
                f"<div class='card-header bg-success text-white'>Arka Yüz</div>"
                f"<div class='card-body'><p>{card.get('back','')}</p></div>"
                f"</div></div>"
            )
        parts.append("</div>")
    elif material_type == "Sunum":
        for slide in content.get("slides", []):
            parts.append(
                f"<div class='card mb-3'><div class='card-header'>"
                f"<strong>Slayt {slide.get('slide_number','')}: {slide.get('title','')}</strong></div>"
                f"<div class='card-body'><ul>"
            )
            for item in slide.get("content", []):
                parts.append(f"<li>{item}</li>")
            parts.append(
                f"</ul><em>Görsel: {slide.get('visual_suggestion','')}</em></div></div>"
            )
    elif material_type == "Test":
        parts.append("<h3>Çoktan Seçmeli</h3>")
        for i, q in enumerate(content.get("multiple_choice", []), 1):
            parts.append(f"<p><strong>{i}. {q.get('question','')}</strong></p><ul>")
            for k, v in q.get("options", {}).items():
                parts.append(f"<li>{k}) {v}</li>")
            parts.append(f"</ul><p class='text-success'>Cevap: {q.get('correct_answer','')}</p>")
        parts.append("<h3>Açık Uçlu</h3>")
        for i, q in enumerate(content.get("open_ended", []), 1):
            parts.append(f"<p><strong>{i}. {q.get('question','')}</strong></p><br><hr>")
    else:
        parts.append(f"<h2>{content.get('title','')}</h2>")
        parts.append("<h4>Ana Kavramlar</h4><ul>")
        for c in content.get("main_concepts", []):
            parts.append(f"<li>{c}</li>")
        parts.append(f"</ul><h4>Ayrıntılı Açıklama</h4><p>{content.get('detailed_explanation','')}</p>")
        parts.append("<h4>Örnekler</h4><ul>")
        for ex in content.get("examples", []):
            parts.append(f"<li>{ex}</li>")
        parts.append("</ul><h4>Dikkat Edilmesi Gerekenler</h4><ul>")
        for w in content.get("warnings", []):
            parts.append(f"<li>{w}</li>")
        parts.append("</ul><h4>İpuçları</h4><ul>")
        for tip in content.get("tips", []):
            parts.append(f"<li>{tip}</li>")
        parts.append("</ul>")

    parts.append("</body></html>")
    return "\n".join(parts)


# ──────────────────────────────────────────────
# Subjects API
# ──────────────────────────────────────────────

@app.route("/api/subjects")
def api_subjects():
    schedule = db.get_weekly_schedule()
    subjects = set()
    for entries in schedule.values():
        for entry in entries:
            subjects.add(entry["subject_name"])
    plans = db.get_all_plans()
    for plan in plans:
        subjects.add(plan["subject"])
    return jsonify(sorted(list(subjects)))


if __name__ == "__main__":
    app.run(debug=True)
