import Button from "./Button.jsx";

function Modal({ children, isOpen, onClose, title }) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <section className="modal-panel" role="dialog" aria-modal="true">
        <header className="modal-header">
          <h2>{title}</h2>
          <Button variant="ghost" size="sm" onClick={onClose} aria-label="Close modal">
            Close
          </Button>
        </header>
        {children}
      </section>
    </div>
  );
}

export default Modal;
