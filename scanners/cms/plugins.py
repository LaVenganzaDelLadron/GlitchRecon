"""CMS extension disclosure scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class CMSPluginScanner(PassiveMarkerScanner):
    """Observes public extension path markers without requesting extension files."""
    id="cms.plugins"; name="CMS Extension Marker Scanner"; category="cms"; description="Detects public CMS extension path references."; severity=Severity.INFO; tags=frozenset({"cms","plugins","passive"}); enabled=True
    markers=("wp-content/plugins/","modules/custom/","components/com_"); observation="cms_extension_marker_observed"; finding_title="CMS extension marker observed"; finding_description="Public CMS extension paths were observed; no extension files or vulnerabilities were queried."; references=()
