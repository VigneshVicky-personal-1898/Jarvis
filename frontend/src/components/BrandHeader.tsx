// AI-ASSISTED: Cursor
// PROMPT: Header mic, wake word, clap activation, ElevenLabs badge
// ACCEPTED-BY: vignesh

import { ForgeMarkLogo } from "./ForgeMarkLogo";
import { MicToggleButton } from "./MicToggleButton";
import { UI, type UiLanguage } from "../i18n/uiStrings";

type Props = {
  onSignOut?: () => void;
  wakeMode: boolean;
  onWakeModeChange: (enabled: boolean) => void;
  llmOnline?: boolean;
  language: UiLanguage;
  onLanguageChange: (lang: UiLanguage) => void;
  listening: boolean;
  micSupported?: boolean;
  onMicToggle: () => void;
  clapMode: boolean;
  onClapModeChange: (enabled: boolean) => void;
  ttsOnline?: boolean;
};

export function BrandHeader({
  onSignOut,
  wakeMode,
  onWakeModeChange,
  llmOnline,
  language,
  onLanguageChange,
  listening,
  micSupported = true,
  onMicToggle,
  clapMode,
  onClapModeChange,
  ttsOnline,
}: Props) {
  const copy = UI[language];

  return (
    <header className="header header--glass header--forgemind animate-in">
      <div className="brand">
        <ForgeMarkLogo size={52} className="brand-mark" />
        <img
          className="brand-logo brand-logo--fallback"
          src="/assets/raya-logo.jpg"
          alt=""
          width={48}
          height={48}
          aria-hidden
        />
        <div>
          <h1>{copy.title}</h1>
          <p className="tagline">
            {copy.tagline}
            {llmOnline === true && (
              <span className="badge badge--live"> LLM online</span>
            )}
            {llmOnline === false && (
              <span className="badge badge--rules"> Rule mode</span>
            )}
            {ttsOnline && (
              <span className="badge badge--live"> ElevenLabs voice</span>
            )}
          </p>
        </div>
      </div>
      <div className="header-actions">
        <MicToggleButton
          listening={listening}
          disabled={!micSupported}
          labelStart={copy.micStart}
          labelStop={copy.micStop}
          onToggle={onMicToggle}
        />
        <label className="lang-toggle">
          <span>{copy.langLabel}</span>
          <select
            value={language}
            onChange={(e) => onLanguageChange(e.target.value as UiLanguage)}
            aria-label={copy.langLabel}
          >
            <option value="en">English</option>
            <option value="ta">தமிழ்</option>
          </select>
        </label>
        <label className="toggle">
          <input
            type="checkbox"
            checked={wakeMode}
            onChange={(e) => onWakeModeChange(e.target.checked)}
          />
          <span>{copy.wakeMode}</span>
        </label>
        <label className="toggle">
          <input
            type="checkbox"
            checked={clapMode}
            onChange={(e) => onClapModeChange(e.target.checked)}
            disabled={!wakeMode}
          />
          <span>{copy.clapMode}</span>
        </label>
        {onSignOut && (
          <button type="button" className="auth-signout" onClick={onSignOut}>
            Sign out
          </button>
        )}
      </div>
    </header>
  );
}
