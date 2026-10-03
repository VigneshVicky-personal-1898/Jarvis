// AI-ASSISTED: Cursor
// PROMPT: Header microphone icon toggle with listening pulse state
// ACCEPTED-BY: vignesh

type Props = {
  listening: boolean;
  disabled?: boolean;
  labelStart: string;
  labelStop: string;
  onToggle: () => void;
};

function MicIcon({ active }: { active: boolean }) {
  return (
    <svg
      className="header-mic-icon"
      viewBox="0 0 24 24"
      width={22}
      height={22}
      aria-hidden
    >
      <path
        fill="currentColor"
        d="M12 14a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2Z"
      />
      {active && (
        <circle
          className="header-mic-icon-wave"
          cx="12"
          cy="12"
          r="10"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
        />
      )}
    </svg>
  );
}

export function MicToggleButton({
  listening,
  disabled,
  labelStart,
  labelStop,
  onToggle,
}: Props) {
  const label = listening ? labelStop : labelStart;

  return (
    <button
      type="button"
      className={`header-mic-btn ${listening ? "header-mic-btn--active" : ""}`}
      onClick={onToggle}
      disabled={disabled}
      aria-pressed={listening}
      aria-label={label}
      title={label}
    >
      <span className="header-mic-btn-ring" aria-hidden />
      <MicIcon active={listening} />
    </button>
  );
}
