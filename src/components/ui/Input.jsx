function Input({ label, helper, className = "", ...props }) {
  return (
    <label className={`ui-field ${className}`}>
      {label ? <span>{label}</span> : null}
      <input {...props} />
      {helper ? <small>{helper}</small> : null}
    </label>
  );
}

export default Input;
