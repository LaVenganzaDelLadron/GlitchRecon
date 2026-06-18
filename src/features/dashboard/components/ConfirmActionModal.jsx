import Modal from "../../../components/ui/Modal.jsx";
import Button from "../../../components/ui/Button.jsx";

function ConfirmActionModal({ actionLabel = "Confirm", isOpen, message, onCancel, onConfirm, title }) {
  return (
    <Modal isOpen={isOpen} onClose={onCancel} title={title}>
      <div className="modal-body">
        <p>{message}</p>
      </div>
      <footer className="modal-actions">
        <Button variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
        <Button variant="primary" onClick={onConfirm}>
          {actionLabel}
        </Button>
      </footer>
    </Modal>
  );
}

export default ConfirmActionModal;
