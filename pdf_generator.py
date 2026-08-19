"""
Takes a render context (from build_report.build_context) and produces a PDF.
Uses Jinja2 for templating and WeasyPrint for HTML->PDF rendering.
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"

_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
_template = _env.get_template("report_template.html")


def render_pdf(context: dict, output_path: str):
    html_string = _template.render(**context)
    HTML(string=html_string, base_url=str(TEMPLATE_DIR)).write_pdf(output_path)
