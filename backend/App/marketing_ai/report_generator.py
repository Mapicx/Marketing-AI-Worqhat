# report_generator.py
from __future__ import annotations
import logging
from typing import Any, Dict, Optional, Tuple, Union
from pathlib import Path
import numbers
from jinja2 import Environment, FileSystemLoader, Undefined

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

Numeric = Union[int, float]

def _safe_round(value: Any, precision: Optional[int] = 0, default: Numeric = 0) -> Union[Numeric, Any]:
    # Treat Jinja Undefined as missing
    try:
        if isinstance(value, Undefined):
            return default
    except Exception:
        pass

    if value is None:
        return default

    # Normalize precision
    if precision is None:
        precision_int = None
    else:
        try:
            precision_int = int(precision)
        except Exception:
            precision_int = 0

    # numeric types
    if isinstance(value, numbers.Number):
        if precision_int is None:
            return round(value)  # type: ignore[arg-type]
        return round(value, precision_int)  # type: ignore[arg-type]

    # numeric strings
    if isinstance(value, str):
        try:
            v = float(value)
        except ValueError:
            return default
        if precision_int is None:
            return round(v)  # type: ignore[arg-type]
        return round(v, precision_int)  # type: ignore[arg-type]

    return default


_DEFAULT_TEMPLATE = """<!doctype html>
<html>
<head><meta charset="utf-8"><title>Report</title></head>
<body>
  <h1>Business Creativity Report</h1>
  <h2>Summary</h2>
  <p>Privacy Compliance: {{ privacy_compliance.handled }}</p>
  <p>Conversion rate: {{ (conversion_rate | default(0)) | safe_round(2) }}</p>
  <p>Average order value: {{ (avg_order_value | default(0)) | safe_round(2) }}</p>
  
  <h2>Predicted Campaign</h2>
  {% if analysis_results.predicted_campaign is defined %}
  <table border="1">
    <tr>
      <th>Feature</th>
      <th>Value</th>
    </tr>
    <tr><td>Type</td><td>{{ analysis_results.predicted_campaign.campaign_type }}</td></tr>
    <tr><td>Offer</td><td>{{ analysis_results.predicted_campaign.offer_type }}</td></tr>
    <tr><td>Target Segment</td><td>{{ analysis_results.predicted_campaign.target_segment }}</td></tr>
    <tr><td>Discount</td><td>{{ analysis_results.predicted_campaign.discount_pct }}%</td></tr>
    <tr><td>Budget</td><td>${{ analysis_results.predicted_campaign.budget | safe_round(2) }}</td></tr>
    <tr><td>Target Size</td><td>{{ analysis_results.predicted_campaign.target_size }}</td></tr>
  </table>
  {% else %}
  <p>No campaign prediction data available.</p>
  {% endif %}

  {% if analysis_results is defined %}
    <h2>Analysis Results</h2>
    <pre>{{ analysis_results }}</pre>
  {% endif %}

  <h2>Full Context Keys</h2>
  <ul>
  {% for k in context_keys | default([]) %}
    <li>{{ k }}</li>
  {% endfor %}
  </ul>
</body>
</html>
"""


def _find_or_create_templates_dir(provided: Optional[str]) -> Path:
    """
    If `provided` exists, return it.
    Otherwise look in likely places:
      - same directory as this file /templates
      - current working directory /templates
      - parent of working dir /templates
    If none exist, create templates next to this file and write a minimal `report.html`.
    """
    module_dir = Path(__file__).resolve().parent
    cwd = Path.cwd()

    candidates = []
    if provided:
        candidates.append(Path(provided))
    candidates.extend([
        module_dir / "templates",
        cwd / "templates",
        cwd.parent / "templates",
    ])

    for c in candidates:
        try:
            if c.exists() and c.is_dir():
                logger.info("Using templates directory: %s", c)
                return c
        except Exception:
            continue

    # none found -> create templates next to module
    target = module_dir / "templates"
    logger.warning("No templates dir found in candidates. Creating templates at: %s", target)
    target.mkdir(parents=True, exist_ok=True)

    # write a default report.html if it doesn't already exist
    default_file = target / "report.html"
    if not default_file.exists():
        logger.info("Writing default template to %s", default_file)
        default_file.write_text(_DEFAULT_TEMPLATE, encoding="utf-8")
    else:
        logger.info("Default template already exists at %s; not overwriting.", default_file)

    return target


def generate_report(
    report_data: Optional[Dict[str, Any]] = None,
    template_name: str = "report.html",
    templates_dir: Optional[str] = None,
    **extra_context: Any
) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Render the HTML report and return (report_data, html_report_str).

    - Will locate or create a templates directory if one isn't found.
    - Accepts extra keyword arguments (e.g. analysis_results=...) and merges them into template context.
    """
    tpl_dir_path = _find_or_create_templates_dir(templates_dir)
    env = Environment(loader=FileSystemLoader(str(tpl_dir_path)))
    env.filters['round'] = _safe_round
    env.filters['safe_round'] = _safe_round

    # Build context
    context: Dict[str, Any] = dict(report_data or {})
    context.update(extra_context)  # Merge in extra context first
    # Provide a list of keys to template for debugging/display
    context['context_keys'] = sorted(list(context.keys()))

    template = env.get_template(template_name)
    try:
        html_report = template.render(**context)
    except Exception as e:
        logger.exception("Failed to render template: %s", e)
        logger.info("Template dir used: %s", tpl_dir_path)
        logger.info("Template context keys (%d): %s", len(context), sorted(context.keys()))
        raise

    return report_data, html_report