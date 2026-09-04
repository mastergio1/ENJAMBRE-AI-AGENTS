"""Puntuador NLP de titulares con FinBERT (HERRAMIENTA DE LABORATORIO — offline).

⚠️ AISLADO A PROPÓSITO: este módulo NO está enchufado al motor en producción.
FinBERT arrastra `torch` + `transformers` (varios GB en RAM), y el motor corre en
Render con memoria muy ajustada: cargarlo ahí lo reventaría (OOM). Además, en El
Enjambre la interpretación de la noticia la hacen los LÍDERES LLM por arquetipo
(engine/brains/) — ese es el diferenciador del producto. Este scorer es solo una
pieza de experimento para la rama de calibración, para comparar enfoques offline.

Convierte un titular en un vector de 3 dimensiones:
  - sentiment  (-1 a 1): positivo/negativo
  - uncertainty (0 a 1): qué tan neutral/dudosa es la noticia
  - impact     (0 a 1): magnitud de la sacudida emocional
"""

import numpy as np


class FinBERTScorer:
    def __init__(self):
        # Import perezoso: solo se paga torch/transformers si de verdad se usa.
        import torch
        from transformers import (AutoModelForSequenceClassification,
                                  AutoTokenizer)

        self._torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "yiyanghkust/finbert-tone")
        self.model.to(self.device)
        self.model.eval()

    def get_impact_vector(self, text: str) -> dict:
        if not text or len(text.strip()) == 0:
            return {"sentiment": 0.0, "uncertainty": 0.5, "impact": 0.0}

        torch = self._torch
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True,
                                padding=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            # Orden del modelo finbert-tone: [neutral, positivo, negativo]
            # (se mantiene el desempaquetado del bundle original; ver README).
            pos, neg, neutral = probs[0].tolist()

        sentiment = pos - neg                 # rango -1 a 1
        uncertainty = 1 - max(pos, neg)       # si es neutral, sube la incertidumbre
        magnitude = abs(sentiment) * (1 + uncertainty)  # impacto real

        return {
            "sentiment": round(float(sentiment), 4),
            "uncertainty": round(float(uncertainty), 4),
            "impact": round(float(magnitude), 4),
        }


# Singleton perezoso (para experimentos; NO se importa desde el servidor real).
_scorer_instance = None


def get_scorer():
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = FinBERTScorer()
    return _scorer_instance
