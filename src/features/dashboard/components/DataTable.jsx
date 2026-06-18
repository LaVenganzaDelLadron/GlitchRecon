import EmptyState from "../../../components/shared/EmptyState.jsx";

function DataTable({ actions, columns, emptyAction, emptyMessage, rows }) {
  if (!rows.length) {
    return <EmptyState action={emptyAction} message={emptyMessage} />;
  }

  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.header}</th>
            ))}
            {actions ? <th className="table-actions-header">Actions</th> : null}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={row.id ?? index}>
              {columns.map((column) => (
                <td key={column.key}>{column.render ? column.render(row) : row[column.key]}</td>
              ))}
              {actions ? <td className="table-actions-cell">{actions(row)}</td> : null}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DataTable;
