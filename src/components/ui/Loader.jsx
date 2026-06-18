function Loader({ label = "Loading" }) {
  return (
    <div className="loader" role="status">
      <span className="loader-dot"></span>
      {label}
    </div>
  );
}

export default Loader;
