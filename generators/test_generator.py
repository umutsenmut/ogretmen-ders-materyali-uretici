import json

from generators.ai_client import call_ai, has_ai_key, extract_json_block


class TestGenerator:
    def generate(self, subject, topic, learning_outcomes, api_key, gemini_key=""):
        if not has_ai_key(api_key, gemini_key):
            return self._fallback(subject, topic)
        try:
            prompt = (
                f"Sen bir Türk öğretmensin. Aşağıdaki konu için test hazırla.\n"
                f"Ders: {subject}\n"
                f"Konu: {topic}\n"
                f"Kazanımlar: {learning_outcomes}\n\n"
                "20 adet 4 seçenekli çoktan seçmeli soru (A, B, C, D) ve 5 adet açık uçlu soru yaz.\n"
                "Yanıtını SADECE aşağıdaki JSON formatında ver:\n"
                '{"multiple_choice": [{"question": "...", "options": {"A": "...", "B": "...", "C": "...", "D": "..."}, "correct_answer": "A"}, ...], '
                '"open_ended": [{"question": "..."}, ...]}'
            )
            raw = call_ai(prompt, openai_key=api_key, gemini_key=gemini_key, max_tokens=4000)
            raw = extract_json_block(raw)
            data = json.loads(raw)
            return {
                "multiple_choice": data.get("multiple_choice", []),
                "open_ended": data.get("open_ended", []),
            }
        except Exception:
            return self._fallback(subject, topic)

    def _fallback(self, subject, topic):
        multiple_choice = []
        for i in range(1, 21):
            multiple_choice.append(
                {
                    "question": f"{topic} ile ilgili {i}. soru: Bu konuda hangi ifade doğrudur?",
                    "options": {
                        "A": f"{topic} hakkında doğru ifade A",
                        "B": f"{topic} hakkında yanlış ifade B",
                        "C": f"{topic} hakkında yanlış ifade C",
                        "D": f"{topic} hakkında yanlış ifade D",
                    },
                    "correct_answer": "A",
                }
            )
        open_ended = [
            {"question": f"{topic} konusunu kendi cümlenizle tanımlayınız."},
            {"question": f"{topic} ile ilgili bir günlük hayat örneği veriniz ve açıklayınız."},
            {"question": f"{topic} konusunun {subject} dersindeki önemini tartışınız."},
            {"question": f"{topic} konusunda karşılaşılan temel zorluklar nelerdir? Açıklayınız."},
            {"question": f"{topic} ile ilgili öğrendiklerinizi özetleyiniz."},
        ]
        return {"multiple_choice": multiple_choice, "open_ended": open_ended}
