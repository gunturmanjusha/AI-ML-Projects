"""Update only the ANN-tuning evidence in the existing 18-slide deck."""
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

PATH = "outputs/AIML_Project_1_Low_Code_Final_Presentation.pptx"
NAVY = RGBColor(12, 58, 82)
PALE = RGBColor(235, 246, 246)
WHITE = RGBColor(255, 255, 255)
INK = RGBColor(38, 54, 63)


def apply_text(shape, text, size):
    shape.text_frame.clear()
    shape.text_frame.word_wrap = True
    paragraph = shape.text_frame.paragraphs[0]
    paragraph.text = text
    paragraph.font.size = Pt(size)
    paragraph.font.color.rgb = INK


def style_cell(cell, text, header=False):
    cell.text = text
    cell.fill.solid()
    cell.fill.fore_color.rgb = NAVY if header else PALE
    for paragraph in cell.text_frame.paragraphs:
        paragraph.font.size = Pt(9 if header else 8.5)
        paragraph.font.bold = header
        paragraph.font.color.rgb = WHITE if header else INK
        paragraph.alignment = PP_ALIGN.CENTER


def text_shape(slide, prefix):
    return next(shape for shape in slide.shapes
                if getattr(shape, "has_text_frame", False) and shape.text.startswith(prefix))


def main():
    deck = Presentation(PATH)

    # Slide 12: accurate methodology, compact enough for the existing appendix layout.
    slide = deck.slides[11]
    apply_text(
        next(shape for shape in slide.shapes if getattr(shape, "has_text_frame", False)
             and (shape.text.startswith("ANN configuration selection:") or shape.text.startswith("ANN: Five fixed"))),
        "ANN: Five fixed-seed configurations were evaluated on the fixed timestamp-grouped chronological validation partition: baseline reproduction, prior 64/24 regularised ANN, wider L2, higher-dropout L2, and compact regularised. Median imputation and scaling were fit on training data only; training-label class weights and validation-loss early stopping were used. The recorded prior 64/24 configuration retained the highest validation recall (92.49%); best new run was higher-dropout L2 at 92.40%.",
        10.5,
    )

    # Slide 18: replace the three-row table with an evidence table that includes
    # the retained ANN, best new ANN run, and tuned XGBoost.
    slide = deck.slides[17]
    old_table = next(shape for shape in slide.shapes if getattr(shape, "has_table", False))
    old_table._element.getparent().remove(old_table._element)
    table = slide.shapes.add_table(4, 4, Inches(0.55), Inches(1.35), Inches(12.2), Inches(1.85)).table
    widths = [1.8, 2.55, 2.55, 5.3]
    for column, width in zip(table.columns, widths):
        column.width = Inches(width)
    values = [
        ["Model", "Validation P / R / F1", "Status", "Configuration / evidence"],
        ["ANN", "37.67 / 92.49 / 53.54", "Selected", "Recorded 64/24; BatchNorm; dropout 0.30/0.15; Adam; early stopping"],
        ["ANN", "45.13 / 92.40 / 60.64", "Best new run", "Higher-dropout L2; 5 actual fixed-seed ANN configurations evaluated"],
        ["XGBoost", "69.57 / 69.10 / 69.34", "Tuned comparator", "6 randomized configurations; 2 timestamp-grouped expanding folds"],
    ]
    for row_index, row in enumerate(values):
        for col_index, value in enumerate(row):
            style_cell(table.cell(row_index, col_index), value, header=row_index == 0)

    apply_text(
        text_shape(slide, "Selection rationale"),
        "Selection rationale\nValidation recall is primary. The historical 64/24 ANN remains selected at 92.49%, narrowly above the best fresh configuration (92.40%). Its lower precision/F1 reflects the alert trade-off. XGBoost has higher precision and F1 but lower recall (69.10%). Test data did not choose configurations or thresholds.",
        13,
    )

    # The Great Learning template is 10 × 5.625 inches. These four additions
    # were previously laid out for a wider canvas; fit them to the real slide.
    title = deck.slides[0]
    date = text_shape(title, "Submission date:")
    date.left, date.top, date.width, date.height = Inches(0.7), Inches(4.96), Inches(4.0), Inches(0.18)
    for paragraph in date.text_frame.paragraphs:
        paragraph.font.size = Pt(8.5)

    recommendations = deck.slides[8]
    evidence = text_shape(recommendations, "Evidence base:")
    evidence.left, evidence.top, evidence.width, evidence.height = Inches(0.65), Inches(4.62), Inches(8.7), Inches(0.40)
    apply_text(evidence, evidence.text, 8.5)

    # Reflow slide 17 within the template boundary.
    s17 = deck.slides[16]
    s17.shapes[1].left, s17.shapes[1].width = Inches(0.35), Inches(7.3)
    s17.shapes[2].left, s17.shapes[2].width = Inches(7.75), Inches(1.9)
    s17.shapes[2].text_frame.paragraphs[0].font.size = Pt(6.5)
    s17.shapes[3].left, s17.shapes[3].top, s17.shapes[3].width, s17.shapes[3].height = Inches(0.35), Inches(0.80), Inches(4.55), Inches(3.85)
    s17.shapes[4].left, s17.shapes[4].top, s17.shapes[4].width, s17.shapes[4].height = Inches(5.15), Inches(0.86), Inches(4.25), Inches(0.34)
    s17.shapes[5].left, s17.shapes[5].top, s17.shapes[5].width, s17.shapes[5].height = Inches(5.15), Inches(1.28), Inches(4.2), Inches(1.65)
    for paragraph in s17.shapes[5].text_frame.paragraphs:
        paragraph.font.size = Pt(9)
    s17.shapes[6].left, s17.shapes[6].top, s17.shapes[6].width, s17.shapes[6].height = Inches(5.15), Inches(3.25), Inches(4.2), Inches(1.25)
    s17.shapes[7].left, s17.shapes[7].top, s17.shapes[7].width, s17.shapes[7].height = Inches(5.32), Inches(3.43), Inches(3.85), Inches(0.85)
    for paragraph in s17.shapes[7].text_frame.paragraphs:
        paragraph.font.size = Pt(9)

    # Reflow slide 18 including its rebuilt comparison table.
    s18 = deck.slides[17]
    s18.shapes[1].left, s18.shapes[1].width = Inches(0.35), Inches(7.3)
    s18.shapes[2].left, s18.shapes[2].width = Inches(7.75), Inches(1.9)
    s18.shapes[2].text_frame.paragraphs[0].font.size = Pt(6.5)
    s18.shapes[3].left, s18.shapes[3].top, s18.shapes[3].width, s18.shapes[3].height = Inches(0.35), Inches(0.75), Inches(9.1), Inches(0.26)
    for paragraph in s18.shapes[3].text_frame.paragraphs:
        paragraph.font.size = Pt(8.5)
    s18.shapes[4].left, s18.shapes[4].top, s18.shapes[4].width, s18.shapes[4].height = Inches(0.45), Inches(3.18), Inches(9.1), Inches(1.32)
    s18.shapes[5].left, s18.shapes[5].top, s18.shapes[5].width, s18.shapes[5].height = Inches(0.65), Inches(3.40), Inches(8.7), Inches(0.88)
    for paragraph in s18.shapes[5].text_frame.paragraphs:
        paragraph.font.size = Pt(9.5)
    for shape in s18.shapes:
        if getattr(shape, "has_table", False):
            shape.left, shape.top, shape.width, shape.height = Inches(0.35), Inches(1.12), Inches(9.3), Inches(1.75)
            widths = [1.15, 1.85, 1.35, 4.95]
            for column, width in zip(shape.table.columns, widths):
                column.width = Inches(width)
            for row_index, row in enumerate(shape.table.rows):
                for cell in row.cells:
                    for paragraph in cell.text_frame.paragraphs:
                        paragraph.font.size = Pt(7.5 if row_index else 8)
    deck.save(PATH)
    print(f"Saved {PATH} with {len(deck.slides)} slides")


if __name__ == "__main__":
    main()
