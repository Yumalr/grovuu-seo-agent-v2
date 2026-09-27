"""DOCX strategy report renderer.

Uses python-docx DocxTemplate to render a strategy plan into the
existing template.docx.
"""

import io
import os
from docxtpl import DocxTemplate


DOCX_TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "template.docx"
)


def render_docx(plan: dict, template_path: str | None = None) -> bytes:
    """Render a strategy plan into a DOCX document.

    Args:
        plan: The structured plan dict from assembly_pass().
        template_path: Path to the .docx template. Defaults to template.docx.

    Returns:
        DOCX file content as bytes.

    Raises:
        FileNotFoundError: If the template file is missing.
    """
    path = template_path or DOCX_TEMPLATE_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Template '{path}' not found.")

    doc = DocxTemplate(path)
    doc.render(plan)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
