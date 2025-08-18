# report_generator.py
from __future__ import annotations
import logging
from typing import Any, Dict, Optional, Tuple, Union, List
from pathlib import Path
import numbers
from jinja2 import Environment, FileSystemLoader, Undefined, select_autoescape
import cloudinary
import cloudinary.uploader
import os
import time
import json
import requests
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

# Default Worqhat trigger URL (from your snippet)
_DEFAULT_WORQHAT_FLOW_URL = "https://api.worqhat.com/flows/trigger/b3563f77-29a9-4ec8-af19-b531d8e44d4c"


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
        url = response.get("secure_url") or response.get("url")
        if not url:
            logger.error("Cloudinary upload returned no URL. Response: %r", response)
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
    logger.warning("No templates dir found in candidates. Creating templates at: %s", target)
    target.mkdir(parents=True, exist_ok=True)
    return target


def _ensure_default_template_file(templates_dir: Path, filename: str = "report.html") -> Path:
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
    if not all(marker in content for marker in must_have_markers):
        logger.warning("Existing template does not contain required visualization placeholders; overwriting %s", target_file)
        target_file.write_text(_DEFAULT_TEMPLATE, encoding="utf-8")
    else:
        logger.info("Existing template appears to contain visualization placeholders; not overwriting %s", target_file)
    return target_file


def _find_nested_value(data: Union[Dict, List], target_keys: Tuple[str, ...]) -> Optional[Any]:
    """Recursively search for any of target keys in nested dictionaries/lists"""
    if isinstance(data, dict):
        # Check if any target key exists at current level
        for key in target_keys:
            if key in data:
                return data[key]
        # Recurse into nested structures
        for value in data.values():
            result = _find_nested_value(value, target_keys)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = _find_nested_value(item, target_keys)
            if result is not None:
                return result
    return None


def _send_html_to_worqhat(
    html: str,
    api_key: Optional[str],
    flow_url: str = _DEFAULT_WORQHAT_FLOW_URL,
    save_to: Optional[Path] = None,
) -> Optional[Tuple[Path, str]]:
    """
    Send the rendered HTML to Worqhat flow (trigger) and save the produced PDF locally if possible.
    - api_key: Bearer token for Worqhat. If None, function will log and return None.
    - flow_url: full trigger URL for the flow.
    - save_to: Path to save the resulting PDF (if detected). If None, defaults to reports/business_creativity_report.pdf.
    Returns tuple (saved_path, pdf_url) on success, otherwise None.
    """
    if api_key is None:
        logger.info("No Worqhat API key provided; skipping HTML->PDF conversion.")
        return None

    if save_to is None:
        reports_dir = Path("reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        save_to = reports_dir / "business_creativity_report.pdf"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"html": html}

    try:
        logger.info("Sending HTML to Worqhat flow: %s", flow_url)
        resp = requests.post(flow_url, json=payload, headers=headers)
    except Exception as exc:
        logger.exception("Failed to call Worqhat flow: %s", exc)
        return None

    if resp.status_code in (200, 201):
        content_type = resp.headers.get("content-type", "")
        # Case A: response itself is a PDF
        if "application/pdf" in content_type.lower():
            try:
                save_to.write_bytes(resp.content)
                logger.info("Saved PDF returned directly from Worqhat to: %s", save_to)
                return save_to, None  # type: ignore # No URL for direct PDF response
            except Exception:
                logger.exception("Failed to write PDF bytes to %s", save_to)
                return None

        # Case B: JSON response containing a URL we can download
        try:
            response_json = resp.json()
        except Exception:
            logger.warning("Worqhat response is not JSON and not PDF. status=%s text=%s", resp.status_code, resp.text)
            return None

        # Look for PDF URL in nested structure
        pdf_url = _find_nested_value(
            response_json, 
            target_keys=("pdf_url", "download_url", "url", "file_url")
        )

        if pdf_url and isinstance(pdf_url, str) and pdf_url.startswith(("http://", "https://")):
            logger.info("Found PDF URL in response: %s", pdf_url)
            try:
                # Download the PDF from the URL
                r2 = requests.get(pdf_url)
                if r2.status_code == 200 and "application/pdf" in r2.headers.get("content-type", "").lower():
                    save_to.write_bytes(r2.content)
                    logger.info("Downloaded generated PDF from %s to %s", pdf_url, save_to)
                    return save_to, pdf_url
                else:
                    logger.warning(
                        "Downloaded file from %s but it wasn't a PDF (status=%s, type=%s)", 
                        pdf_url, r2.status_code, r2.headers.get("content-type")
                    )
            except Exception as e:
                logger.exception("Failed to download PDF from %s: %s", pdf_url, e)
                return None
        else:
            # No obvious PDF URL - log json for debugging
            logger.warning(
                "Worqhat returned JSON but did not contain a valid PDF URL. "
                "Searched keys: pdf_url, download_url, url, file_url. "
                "Response JSON: %s", 
                json.dumps(response_json, indent=2)
            )
            return None
    else:
        logger.error("Worqhat API returned status %s: %s", resp.status_code, resp.text)
        return None


def generate_report(
    report_data: Optional[Dict[str, Any]] = None,
    template_name: str = "report.html",
    templates_dir: Optional[str] = None,
    **extra_context: Any
) -> Tuple[Optional[Dict[str, Any]], str, Optional[str]]:
    """
    Render the HTML report and return (report_data, html_report_str, pdf_url).
    If Worqhat API key is provided (via extra_context['worqhat_api_key'] or env var WORQHAT_API_KEY),
    the rendered HTML will be sent to the Worqhat flow to attempt HTML->PDF conversion.
    Returns pdf_url if available.
    """
    tpl_dir_path = _find_or_create_templates_dir(templates_dir)
    tpl_file = _ensure_default_template_file(tpl_dir_path, template_name)

    env = Environment(loader=FileSystemLoader(str(tpl_dir_path)), autoescape=select_autoescape(["html", "xml"]))
    env.filters["round"] = _safe_round
    env.filters["safe_round"] = _safe_round
    env.filters["tojson"] = lambda obj: json.dumps(obj, default=str, ensure_ascii=False, indent=2)

    # Build context
    context: Dict[str, Any] = dict(report_data or {})
    context.update(extra_context)

    # Upload images and add URLs to context
    report_dir = Path("reports")
    image_mapping = {
        "segmentation_image_url": report_dir / "segmentation_visualization.png",
        "campaign_analysis_image_url": report_dir / "campaign_analysis.png",
        "roi_prediction_image_url": report_dir / "roi_prediction_accuracy.png",
    }

    # allow a small wait if some other process is writing files
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

    logger.info(
        "Image context values: segmentation=%s campaign=%s roi=%s",
        context.get("segmentation_image_url"),
        context.get("campaign_analysis_image_url"),
        context.get("roi_prediction_image_url"),
    )

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

    # Save HTML to reports/ so it's available locally and for Worqhat if needed
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    html_file = reports_dir / "business_creativity_report.html"
    try:
        html_file.write_text(html_report, encoding="utf-8")
        logger.info("Report saved to %s", html_file)
    except Exception:
        logger.exception("Failed to save HTML report to %s", html_file)

    # Attempt to send to Worqhat if the API key is provided
    worqhat_api_key = extra_context.get("worqhat_api_key") or os.getenv("WORQHAT_API_KEY")
    worqhat_flow_url = extra_context.get("worqhat_flow_url") or _DEFAULT_WORQHAT_FLOW_URL

    pdf_result = _send_html_to_worqhat(html_report, api_key=worqhat_api_key, flow_url=worqhat_flow_url, save_to=reports_dir / "business_creativity_report.pdf")
    pdf_url = None
    
    if pdf_result:
        pdf_path, pdf_url = pdf_result
        if pdf_url:
            logger.info("PDF available at: %s", pdf_url)
        else:
            logger.info("PDF saved locally at: %s", pdf_path)

    return report_data, html_report, pdf_url