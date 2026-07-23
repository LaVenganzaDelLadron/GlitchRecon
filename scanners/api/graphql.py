"""GraphQL endpoint marker scanner."""
from app.models.schemas import Severity
from scanners.passive import PassiveMarkerScanner
class GraphQLScanner(PassiveMarkerScanner):
    """Observes public GraphQL references without sending a GraphQL operation."""
    id="api.graphql"; name="GraphQL Surface Scanner"; category="api"; description="Discovers public GraphQL endpoint markers without executing queries."; severity=Severity.INFO; tags=frozenset({"api","graphql","passive"}); enabled=True
    markers=("/graphql", "graphql endpoint", "graphiql"); observation="graphql_marker_observed"; finding_title="GraphQL marker observed"; finding_description="A public GraphQL marker was observed. No query, introspection, or mutation was executed."; references=("https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html",)
