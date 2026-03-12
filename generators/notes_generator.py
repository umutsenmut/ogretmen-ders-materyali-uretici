import json

from generators.ai_client import call_ai, has_ai_key, extract_json_block


class NotesGenerator:
    def generate(self, subject, topic, learning_outcomes, api_key, gemini_key=""):
        if not has_ai_key(api_key, gemini_key):
            return self._fallback(subject, topic)
        try:
            prompt = (
                f"Sen deneyimli bir Türk öğretmensin. Aşağıdaki konu için detaylı öğretmen notları hazırla.\n"
                f"Ders: {subject}\n"
                f"Konu: {topic}\n"
                f"Kazanımlar: {learning_outcomes}\n\n"
                "Öğretmen notları şunları içermeli:\n"
                "- Başlık\n"
                "- Ana kavramlar listesi\n"
                "- Detaylı açıklama\n"
                "- Somut örnekler\n"
                "- Dikkat edilmesi gereken noktalar\n"
                "- Öğretim ipuçları\n"
                "Yanıtını SADECE aşağıdaki JSON formatında ver:\n"
                '{"title": "...", "main_concepts": ["...", "..."], "detailed_explanation": "...", '
                '"examples": ["...", "..."], "warnings": ["...", "..."], "tips": ["...", "..."]}'
            )
            raw = call_ai(prompt, openai_key=api_key, gemini_key=gemini_key, max_tokens=3000)
            raw = extract_json_block(raw)
            data = json.loads(raw)
            return {
                "title": data.get("title", topic),
                "main_concepts": data.get("main_concepts", []),
                "detailed_explanation": data.get("detailed_explanation", ""),
                "examples": data.get("examples", []),
                "warnings": data.get("warnings", []),
                "tips": data.get("tips", []),
            }
        except Exception:
            return self._fallback(subject, topic)

    def _fallback(self, subject, topic):
        return {
            "title": f"{subject} - {topic} Öğretmen Notları",
            "main_concepts": [
                f"{topic} tanımı ve kapsamı",
                "Temel kavramlar ve terminoloji",
                "Tarihsel gelişim ve önemi",
                "Uygulama alanları",
                "İlgili alt konular",
            ],
            "detailed_explanation": (
                f"{topic}, {subject} dersinin önemli konularından biridir. "
                "Bu konuyu öğrencilere aktarırken somut örneklerden yararlanılmalı, "
                "önce temel kavramlar açıklanmalı, ardından daha karmaşık yapılara geçilmelidir. "
                "Öğrencilerin ön bilgileri değerlendirilerek ders planlanmalıdır. "
                "Görsel materyaller ve etkinlikler konunun pekiştirilmesine yardımcı olur."
            ),
            "examples": [
                f"Örnek 1: {topic} konusunun günlük hayattaki uygulaması",
                f"Örnek 2: {topic} ile ilgili temel alıştırma sorusu ve çözümü",
                f"Örnek 3: {topic} konusunun farklı bir bağlamda kullanımı",
            ],
            "warnings": [
                "Öğrencilerin sıkça yaptığı kavram yanılgısına dikkat edin.",
                "Konuya geçmeden önce ön bilgileri yoklayın.",
                "Aşırı soyut anlatımdan kaçının, somut örnekler kullanın.",
                "Öğrencilerin sorularına açık ve sabırlı yanıtlar verin.",
            ],
            "tips": [
                "Konuyu görsel materyallerle destekleyin.",
                "Grup çalışmaları ve tartışmalar düzenleyin.",
                "Öğrencilerin aktif katılımını teşvik edin.",
                "Farklı öğrenme stillerine yönelik etkinlikler planlayın.",
                "Değerlendirmeyi süreç boyunca yapın, sadece sınav sonunda değil.",
            ],
        }
