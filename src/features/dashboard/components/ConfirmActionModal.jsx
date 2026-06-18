import Modal from "../../../components/ui/Modal.jsx";
import Button from "../../../components/ui/Button.jsx";

function ConfirmActionModal({
  actionLabel = "Confirm",
  error = "",
  isOpen,
  isSubmitting = false,
  message,
  onCancel,
  onConfirm,
  title,
}) {
  const confirmVariant = /delete|cancel/i.test(actionLabel) ? "danger" : "primary";

  return (
    <Modal isOpen={isOpen} onClose={onCancel} title={title}>
      <div className="modal-body">
        <p>{message}</p>
        {error ? <p className="auth-alert error">{error}</p> : null}
      </div>
      <footer className="modal-actions">
        <Button disabled={isSubmitting} variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
        <Button disabled={isSubmitting} variant={confirmVariant} onClick={onConfirm}>
          {isSubmitting ? "Working..." : actionLabel}
        </Button>
      </footer>
    </Modal>
  );
}

export default ConfirmActionModal;
