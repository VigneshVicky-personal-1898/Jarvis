// AI-ASSISTED: Cursor
// PROMPT: ForgeMind-inspired mark for Jarvis header and orb (original SVG)
// ACCEPTED-BY: vignesh

type Props = {
  size?: number;
  className?: string;
};

/** Abstract forge spark — replace with official ForgeMind asset if licensed. */
export function ForgeMarkLogo({ size = 48, className = "" }: Props) {
  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 64 64"
      aria-hidden
    >
      <defs>
        <linearGradient id="fm-core" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#f5d078" />
          <stop offset="45%" stopColor="#e8a838" />
          <stop offset="100%" stopColor="#22d3ee" />
        </linearGradient>
        <filter id="fm-glow">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <circle cx="32" cy="32" r="30" fill="#0a0e14" stroke="url(#fm-core)" strokeWidth="1.5" />
      <path
        d="M32 12 L38 28 L54 32 L38 36 L32 52 L26 36 L10 32 L26 28 Z"
        fill="url(#fm-core)"
        filter="url(#fm-glow)"
        opacity="0.95"
      />
      <circle cx="32" cy="32" r="6" fill="#0f172a" stroke="#f5d078" strokeWidth="1" />
    </svg>
  );
}
