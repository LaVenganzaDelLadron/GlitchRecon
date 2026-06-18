from sqlalchemy import inspect, text


SCAN_COLUMN_SQL = {
    "proposed_plan": "TEXT",
    "parent_scan_id": "INTEGER",
    "executed_command": "TEXT",
    "stdout": "TEXT",
    "stderr": "TEXT",
    "return_code": "INTEGER",
    "error_message": "TEXT",
    "approved_at": "DATETIME",
    "pid": "INTEGER",
    "log_path": "TEXT",
    "exit_path": "TEXT",
    "timed_out": "INTEGER",
    "cancelled_at": "DATETIME",
}


def ensure_scan_columns(engine):
    inspector = inspect(engine)
    if "scans" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("scans")}
    missing_columns = [
        (column_name, column_type)
        for column_name, column_type in SCAN_COLUMN_SQL.items()
        if column_name not in existing_columns
    ]
    if not missing_columns:
        return

    with engine.begin() as connection:
        for column_name, column_type in missing_columns:
            connection.execute(text(f"ALTER TABLE scans ADD COLUMN {column_name} {column_type}"))
