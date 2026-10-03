// AI-ASSISTED: Cursor
// PROMPT: English and Tamil UI strings for RAYA dashboard
// ACCEPTED-BY: vignesh

export type UiLanguage = "en" | "ta";

export const UI: Record<
  UiLanguage,
  {
    title: string;
    tagline: string;
    wakeMode: string;
    clapMode: string;
    micStart: string;
    micStop: string;
    manualPlaceholder: string;
    send: string;
    langLabel: string;
  }
> = {
  en: {
    title: "RAYA",
    tagline: "Agentic command center · voice · configurable LLM · connected systems",
    wakeMode: "Wake word mode",
    clapMode: "Clap activation",
    micStart: "Start microphone",
    micStop: "Stop microphone",
    manualPlaceholder:
      'Command, e.g. "latest test plan results" or "analyze raya project"',
    send: "Send",
    langLabel: "Language",
  },
  ta: {
    title: "RAYA",
    tagline: "நிர்வாக மையம் · குரல் · LLM · இணைக்கப்பட்ட அமைப்புகள்",
    wakeMode: "விழிப்பு சொல் முறை",
    clapMode: "கைத்தட்டல் செயல்படுத்தல்",
    micStart: "மைக்ரோஃபோன் தொடங்கு",
    micStop: "மைக்ரோஃபோன் நிறுத்து",
    manualPlaceholder:
      'கட்டளை, எ.கா. "சமீப test plan முடிவுகள்" அல்லது "raya project பகுப்பு"',
    send: "அனுப்பு",
    langLabel: "மொழி",
  },
};
