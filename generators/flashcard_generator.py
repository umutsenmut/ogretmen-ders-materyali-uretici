import json

from generators.ai_client import call_ai, has_ai_key, extract_json_block


class FlashcardGenerator:
    def generate(self, subject, topic, learning_outcomes, api_key, gemini_key=""):
        if not has_ai_key(api_key, gemini_key):
            return self._fallback(subject, topic)
        try:
            prompt = (
                f"Sen bir Türk öğretmensin. Aşağıdaki konu için 8 adet bilgi kartı (flashcard) hazırla.\n"
                f"Ders: {subject}\n"
                f"Konu: {topic}\n"
                f"Kazanımlar: {learning_outcomes}\n\n"
                "Her kart için ön yüzde soru veya kavram, arka yüzde açıklama veya cevap yaz.\n"
                "Yanıtını SADECE aşağıdaki JSON formatında ver, başka hiçbir şey ekleme:\n"
                '{"cards": [{"id": 1, "front": "...", "back": "..."}, ...]}'
            )
            raw = call_ai(prompt, openai_key=api_key, gemini_key=gemini_key, max_tokens=2000)
            raw = extract_json_block(raw)
            data = json.loads(raw)
            cards = data.get("cards", [])
            for i, card in enumerate(cards, 1):
                card.setdefault("id", i)
            return {"cards": cards}
        except Exception:
            return self._fallback(subject, topic)

    def _fallback(self, subject, topic):
        cards = [
            {
                "id": 1,
                "front": f"{topic} nedir?",
                "back": f"{topic}, {subject} dersinin önemli bir konusudur.",
            },
            {
                "id": 2,
                "front": f"{topic} konusunun temel kavramları nelerdir?",
                "back": "Temel kavramlar: tanım, özellikler, uygulama alanları.",
            },
            {
                "id": 3,
                "front": f"{topic} neden önemlidir?",
                "back": f"{subject} alanında temel bir yapı taşı olduğundan önemlidir.",
            },
            {
                "id": 4,
                "front": f"{topic} ile ilgili bir örnek veriniz.",
                "back": "Günlük hayattan bir örnek: gerçek yaşamda bu konunun uygulaması.",
            },
            {
                "id": 5,
                "front": f"{topic} konusunda dikkat edilmesi gereken noktalar nelerdir?",
                "back": "Dikkat edilmesi gerekenler: doğru uygulama, kavram yanılgılarından kaçınma.",
            },
        ]
        return {"cards": cards}
