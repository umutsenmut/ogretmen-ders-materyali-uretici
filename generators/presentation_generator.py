import json

from generators.ai_client import call_ai, has_ai_key, extract_json_block


class PresentationGenerator:
    def generate(self, subject, topic, learning_outcomes, api_key, gemini_key=""):
        if not has_ai_key(api_key, gemini_key):
            return self._fallback(subject, topic)
        try:
            prompt = (
                f"Sen bir Türk öğretmensin. Aşağıdaki konu için 12 slaytlık sunum hazırla.\n"
                f"Ders: {subject}\n"
                f"Konu: {topic}\n"
                f"Kazanımlar: {learning_outcomes}\n\n"
                "Her slayt için başlık, içerik (madde madde) ve görsel öneri yaz.\n"
                "İçerik kısa ve öz olsun, 3-5 madde.\n"
                "Yanıtını SADECE aşağıdaki JSON formatında ver:\n"
                '{"slides": [{"slide_number": 1, "title": "...", "content": ["...", "..."], "visual_suggestion": "..."}, ...]}'
            )
            raw = call_ai(prompt, openai_key=api_key, gemini_key=gemini_key, max_tokens=3000)
            raw = extract_json_block(raw)
            data = json.loads(raw)
            return {"slides": data.get("slides", [])}
        except Exception:
            return self._fallback(subject, topic)

    def _fallback(self, subject, topic):
        slides = [
            {
                "slide_number": 1,
                "title": f"{topic} - Giriş",
                "content": [
                    f"Ders: {subject}",
                    f"Konu: {topic}",
                    "Bu sunumda konunun temel kavramları ele alınacaktır.",
                ],
                "visual_suggestion": "Konuya ilişkin motivasyon görseli",
            },
            {
                "slide_number": 2,
                "title": "Kazanımlar",
                "content": [
                    "Bu dersin sonunda öğrenciler:",
                    "• Temel kavramları tanımlayabilecek",
                    "• Örnekleri açıklayabilecek",
                    "• Uygulamalı sorular çözebilecek",
                ],
                "visual_suggestion": "Hedef veya ok görseli",
            },
            {
                "slide_number": 3,
                "title": "Temel Kavramlar",
                "content": [
                    f"{topic} tanımı",
                    "Temel özellikler",
                    "Tarihsel gelişim",
                ],
                "visual_suggestion": "Kavram haritası",
            },
            {
                "slide_number": 4,
                "title": "Detaylı Açıklama",
                "content": [
                    "Konunun derinlemesine incelenmesi",
                    "Alt başlıklar ve açıklamalar",
                    "Teorik temel",
                ],
                "visual_suggestion": "Açıklayıcı diyagram",
            },
            {
                "slide_number": 5,
                "title": "Örnekler",
                "content": [
                    "Örnek 1: Temel uygulama",
                    "Örnek 2: İleri düzey uygulama",
                    "Günlük hayattan örnekler",
                ],
                "visual_suggestion": "Fotoğraf veya gerçek hayat görseli",
            },
            {
                "slide_number": 6,
                "title": "Uygulama",
                "content": [
                    "Etkinlik: Grup çalışması",
                    "Problem çözme",
                    "Tartışma soruları",
                ],
                "visual_suggestion": "Öğrencilerin çalıştığı görsel",
            },
            {
                "slide_number": 7,
                "title": "Özet ve Değerlendirme",
                "content": [
                    "Öğrendiklerimizi pekiştirelim",
                    "Temel noktalar",
                    "Sonraki ders hazırlığı",
                ],
                "visual_suggestion": "Özet listesi görseli",
            },
        ]
        return {"slides": slides}
