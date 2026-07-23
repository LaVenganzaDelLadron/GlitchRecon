"""Joomla marker scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class JoomlaScanner(PassiveMarkerScanner):
    """Observes public Joomla markers without enumerating extensions."""
    id="cms.joomla"; name="Joomla Marker Scanner"; category="cms"; description="Detects public Joomla resource markers."; severity=Severity.INFO; tags=frozenset({"cms","joomla","passive"}); enabled=True
    markers=("/media/system/js/", "joomla!"); observation="joomla_marker_observed"; finding_title="Joomla marker observed"; finding_description="Public Joomla markers were observed; no extension enumeration was performed."; references=()
