from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)


def generate_pdf(
    title: str,
    content: str,
    output_path: str
):

    doc = SimpleDocTemplate(output_path)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(title, styles["Title"])
    )

    elements.append(
        Spacer(1, 12)
    )

    for line in content.split("\n"):

        elements.append(
            Paragraph(
                line,
                styles["BodyText"]
            )
        )

    doc.build(elements)

    return output_path