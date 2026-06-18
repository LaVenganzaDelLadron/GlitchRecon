function EmptyState({ action, message = "No records found.", title = "Nothing here yet" }) {
  return (
    <div className="empty-state">
      <h3>{title}</h3>
      <p>{message}</p>
      {action}
    </div>
  );
}

export default EmptyState;
