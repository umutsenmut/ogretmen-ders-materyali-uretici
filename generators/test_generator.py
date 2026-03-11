import json
import openai


class TestGenerator:
    def generate(self, subject, topic, learning_outcomes, api_key):
        if not api_key or api_key.startswith("sk-your"):
            return self._fallback(subject, topic)
        try:
            client = openai.OpenAI(api_key=api_key)
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
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=4000,
            )
            raw = response.choices[0].message.content.strip()
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
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
