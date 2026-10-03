// AI-ASSISTED: Cursor
// PROMPT: Confirmation UI for permission-gated tools
// ACCEPTED-BY: vignesh

type Props = {
  open: boolean;
  message: string;
  confirmationId: string | null;
  onConfirm: () => void;
  onCancel: () => void;
};

export function ConfirmationModal({
  open,
  message,
  onConfirm,
  onCancel,
}: Props) {
  if (!open) return null;
  return (
    <div className="confirm-overlay" role="dialog" aria-modal="true">
      <div className="confirm-card panel panel--glass">
        <h2>Confirm action</h2>
        <p>{message}</p>
        <div className="confirm-actions">
          <button type="button" className="btn btn-ghost" onClick={onCancel}>
            Cancel
          </button>
          <button type="button" className="btn btn-primary btn--3d" onClick={onConfirm}>
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
}
