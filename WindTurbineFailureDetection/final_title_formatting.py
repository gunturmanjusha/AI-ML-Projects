"""Formatting-only final title adjustment for the existing deck."""
from pptx import Presentation
from pptx.util import Inches, Pt

PATH = "outputs/AIML_Project_1_Low_Code_Final_Presentation.pptx"


def slide_with_title(deck, prefix):
    for slide in deck.slides:
        for shape in slide.shapes:
            if getattr(shape, "has_text_frame", False) and shape.top < Inches(0.7) and shape.text.startswith(prefix):
                return slide, shape
    raise RuntimeError(f"Slide title not found: {prefix}")


def set_title(shape, text):
    shape.text_frame.paragraphs[0].text = text
    shape.text_frame.paragraphs[0].font.size = Pt(15)
    shape.width = Inches(7.3)


def main():
    deck = Presentation(PATH)
    # The hyperparameter slide already uses two separate, bounded cards.
    tuning, _ = slide_with_title(deck, "Model Improvement — Hyperparameter Tuning")
    xgb = [s for s in tuning.shapes if getattr(s, "has_text_frame", False) and s.text == "XGBoost Tuning"]
    ann = [s for s in tuning.shapes if getattr(s, "has_text_frame", False) and s.text == "ANN Tuning"]
    if len(xgb) != 1 or len(ann) != 1:
        raise RuntimeError("Expected separate XGBoost and ANN tuning sections.")

    _, multivariate_title = slide_with_title(deck, "EDA Results — Multivariate Relationships")
    set_title(multivariate_title, "Multivariate Sensor Analysis")

    _, comparison_title = slide_with_title(deck, "ANN and XGBoost Tuning Comparison")
    set_title(comparison_title, "ANN vs. XGBoost — Tuning Results")

    deck.save(PATH)
    print(f"Saved {PATH}; {len(deck.slides)} slides")


if __name__ == "__main__":
    main()
