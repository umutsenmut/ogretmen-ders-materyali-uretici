import json
import openai


class PresentationGenerator:
    def generate(self, subject, topic, learning_outcomes, api_key):
        if not api_key or api_key.startswith("sk-your"):
            return self._fallback(subject, topic)
        try:
            client = openai.OpenAI(api_key=api_key)
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
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=3000,
            )
            raw = response.choices[0].message.content.strip()
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
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
