"""
Génération de documents PDF (ordonnances, factures, résultats) à partir
de gabarits HTML/Jinja2, en utilisant WeasyPrint.
"""
from io import BytesIO

from flask import render_template
from weasyprint import HTML


def render_pdf_from_template(template_name, **context):
    """
    Rend un template Jinja2 en HTML puis le convertit en document PDF.
    Retourne un objet BytesIO prêt à être envoyé au client.
    """
    html_content = render_template(template_name, **context)
    pdf_buffer = BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer
