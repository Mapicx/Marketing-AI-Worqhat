# report_generator.py
from __future__ import annotations
import logging
from typing import Any, Dict, Optional, Tuple, Union
from pathlib import Path
import numbers
from jinja2 import Environment, FileSystemLoader, Undefined, select_autoescape
import cloudinary
import cloudinary.uploader
import os
import time
import json
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Configure Cloudinary from environment variables
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

Numeric = Union[int, float]


def upload_image_to_cloudinary(image_path: str) -> Optional[str]:
    """
    Upload image to Cloudinary and return secure URL.
    Returns None on failure (and logs the failure).
    """
    try:
        response = cloudinary.uploader.upload(
            image_path,
            folder="marketing_reports/",
            resource_type="image",
        )
        # prefer secure_url
        url = response.get("secure_url") or response.get("url")
        if not url:
            logger.error(
                "Cloudinary upload returned no URL. Response: %r", response
            )
            return None
        logger.info("Cloudinary upload successful: %s -> %s", image_path, url)
        return url
    except Exception as exc:
        logger.exception("Failed to upload image to Cloudinary (%s): %s", image_path, exc)
        return None


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
<head>
  <meta charset="utf-8">
  <title>Business Creativity Report</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; }
    .visualization { margin: 20px 0; text-align: center; }
    img { max-width: 100%; border: 1px solid #eee; }
    .section { margin-bottom: 30px; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; }
    pre {
      background-color: #f5f5f5;
      padding: 15px;
      border-radius: 5px;
      overflow-x: auto;
      white-space: pre-wrap;
    }
  </style>
</head>
<body>
  <h1>Business Creativity Report</h1>

  <div class="section">
    <h2>Summary</h2>
    <p>Privacy Compliance: {{ privacy_compliance.handled if privacy_compliance is defined else 'N/A' }}</p>
    <p>Conversion rate: {{ (conversion_rate | default(0)) | safe_round(2) }}</p>
    <p>Average order value: {{ (avg_order_value | default(0)) | safe_round(2) }}</p>
  </div>

  <!-- VISUALIZATIONS SECTION -->
  <div class="section">
    <h2>Visualizations</h2>

    {% if segmentation_image_url %}
    <div class="visualization">
      <h3>Customer Segmentation</h3>
      <img src="{{ segmentation_image_url | safe }}" alt="Customer Segmentation">
    </div>
    {% endif %}

    {% if campaign_analysis_image_url %}
    <div class="visualization">
      <h3>Conversion Rate by Campaign Type and Offer</h3>
      <img src="{{ campaign_analysis_image_url | safe }}" alt="Campaign Analysis">
    </div>
    {% endif %}

    {% if roi_prediction_image_url %}
    <div class="visualization">
      <h3>ROI Prediction Accuracy</h3>
      <img src="{{ roi_prediction_image_url | safe }}" alt="ROI Prediction">
    </div>
    {% endif %}
  </div>

  <!-- PREDICTED CAMPAIGN SECTION -->
  <div class="section">
    <h2>Predicted Campaign</h2>
    {% if analysis_results and analysis_results.get('predicted_campaign') %}
    <table>
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
  </div>

  <!-- ANALYSIS RESULTS SECTION -->
  {% if analysis_results %}
  <div class="section">
    <h2>Analysis Results</h2>
    <pre>{{ analysis_results | tojson | safe }}</pre>
  </div>
  {% endif %}

  <!-- CONTEXT KEYS SECTION -->
  {% if context_keys %}
  <div class="section">
    <h2>Full Context Keys</h2>
    <ul>
    {% for k in context_keys %}
      <li>{{ k }}</li>
    {% endfor %}
    </ul>
  </div>
  {% endif %}
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
    If an existing report.html lacks required visualization placeholders, overwrite it with a default.
    """
    module_dir = Path(__file__).resolve().parent
    cwd = Path.cwd()

    candidates = []
    if provided:
        candidates.append(Path(provided))
    candidates.extend(
        [
            module_dir / "templates",
            cwd / "templates",
            cwd.parent / "templates",
        ]
    )

    for c in candidates:
        try:
            if c.exists() and c.is_dir():
                logger.info("Using templates directory: %s", c)
                return c
        except Exception:
            continue

    # none found -> create templates next to module
    target = module_dir / "templates"
    logger.warning(
        "No templates dir found in candidates. Creating templates at: %s", target
    )
    target.mkdir(parents=True, exist_ok=True)

    return target


def _ensure_default_template_file(templates_dir: Path, filename: str = "report.html") -> Path:
    """
    Ensure templates_dir/filename exists and contains the visualization placeholders.
    If the file is missing or doesn't contain expected placeholders, overwrite it with the default.
    Returns the Path to the template file.
    """
    target_file = templates_dir / filename

    must_have_markers = ["segmentation_image_url", "campaign_analysis_image_url", "roi_prediction_image_url", "<img"]

    if not target_file.exists():
        logger.info("Template file missing, writing default template to %s", target_file)
        target_file.write_text(_DEFAULT_TEMPLATE, encoding="utf-8")
        return target_file

    try:
        content = target_file.read_text(encoding="utf-8")
    except Exception:
        logger.exception("Failed to read existing template file; overwriting with default: %s", target_file)
        target_file.write_text(_DEFAULT_TEMPLATE, encoding="utf-8")
        return target_file

    # If any of required markers absent, overwrite (user likely has an older minimal template)
    if not all(marker in content for marker in must_have_markers):
        logger.warning(
            "Existing template does not contain required visualization placeholders; overwriting %s", target_file
        )
        target_file.write_text(_DEFAULT_TEMPLATE, encoding="utf-8")
    else:
        logger.info("Existing template appears to contain visualization placeholders; not overwriting %s", target_file)

    return target_file


def generate_report(
    report_data: Optional[Dict[str, Any]] = None,
    template_name: str = "report.html",
    templates_dir: Optional[str] = None,
    **extra_context: Any
) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Render the HTML report and return (report_data, html_report_str).

    - Will locate or create a templates directory if one isn't found.
    - Ensures the template file contains visualization placeholders (overwrites only if necessary).
    - Accepts extra keyword arguments (e.g. analysis_results=...) and merges them into template context.
    """
    tpl_dir_path = _find_or_create_templates_dir(templates_dir)
    tpl_file = _ensure_default_template_file(tpl_dir_path, template_name)

    # Use select_autoescape for HTML templates to avoid accidental double-escaping
    env = Environment(
        loader=FileSystemLoader(str(tpl_dir_path)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    # Filters
    env.filters["round"] = _safe_round
    env.filters["safe_round"] = _safe_round
    env.filters["tojson"] = lambda obj: json.dumps(obj, default=str, ensure_ascii=False, indent=2)

    # Build context
    context: Dict[str, Any] = dict(report_data or {})
    # Merge extra_context into context (callers can override values)
    context.update(extra_context)

    # Upload images and add URLs to context
    report_dir = Path("reports")
    image_mapping = {
        "segmentation_image_url": report_dir / "segmentation_visualization.png",
        "campaign_analysis_image_url": report_dir / "campaign_analysis.png",
        "roi_prediction_image_url": report_dir / "roi_prediction_accuracy.png",
    }

    # Small wait if some other process is writing files (your code logs show this)
    time.sleep(0.5)

    for key, path in image_mapping.items():
        if path.exists():
            try:
                url = upload_image_to_cloudinary(str(path))
                if url:
                    context[key] = url
                else:
                    # fallback to local file path if upload failed
                    context[key] = f"file://{path.resolve()}"
                    logger.warning("Using local path for image because upload failed: %s", path)
            except Exception as e:
                logger.exception("Cloudinary upload attempt threw an exception for %s: %s", path, e)
                context[key] = f"file://{path.resolve()}"
        else:
            context[key] = None
            logger.debug("Image not found, leaving %s as None: %s", key, path)

    # Log the image URLs/values so we can see exactly what will be inserted
    logger.info("Image context values: segmentation=%s campaign=%s roi=%s",
                context.get("segmentation_image_url"),
                context.get("campaign_analysis_image_url"),
                context.get("roi_prediction_image_url")
               )

    # Provide a list of keys to template for debugging/display
    context["context_keys"] = sorted(list(context.keys()))

    template = env.get_template(template_name)
    try:
        html_report = template.render(**context)
    except Exception as e:
        logger.exception("Failed to render template: %s", e)
        logger.info("Template dir used: %s", tpl_dir_path)
        logger.info("Template file ensured at: %s", tpl_file)
        logger.info("Template context keys (%d): %s", len(context), sorted(context.keys()))
        raise

    return report_data, html_report
