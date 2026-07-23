"""Drupal marker scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class DrupalScanner(PassiveMarkerScanner):
    """Observes public Drupal markers without probing administration paths."""
    id="cms.drupal"; name="Drupal Marker Scanner"; category="cms"; description="Detects public Drupal resource markers."; severity=Severity.INFO; tags=frozenset({"cms","drupal","passive"}); enabled=True
    markers=("sites/default/files", "drupalsettings"); observation="drupal_marker_observed"; finding_title="Drupal marker observed"; finding_description="Public Drupal resource markers were observed; no administrative path was requested."; references=()
