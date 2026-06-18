function Card({ children, className = "", title, action }) {
  return (
    <section className={`card ${className}`}>
      {title || action ? (
        <header className="card-header">
          {title ? <h2>{title}</h2> : <span></span>}
          {action}
        </header>
      ) : null}
      {children}
    </section>
  );
}

export default Card;
