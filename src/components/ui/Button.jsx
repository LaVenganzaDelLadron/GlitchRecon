function Button({
  children,
  className = "",
  size = "md",
  variant = "secondary",
  ...props
}) {
  return (
    <button
      className={`ui-button ui-button-${variant} ui-button-${size} ${className}`}
      type={props.type || "button"}
      {...props}
    >
      {children}
    </button>
  );
}

export default Button;
