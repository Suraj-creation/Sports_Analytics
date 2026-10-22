import { Link } from "@tanstack/react-router";
import { useState } from "react";
import { Card, Page } from "./ui";

type Display = { theme: "light" | "dark" | "system"; reducedMotion: boolean };
const key = "rally-display-v1";
export function readDisplay(): Display {
  try {
    const value = JSON.parse(localStorage.getItem(key) ?? "{}");
    return {
      theme: ["light", "dark", "system"].includes(value.theme) ? value.theme : "light",
      reducedMotion: value.reducedMotion === true,
    };
  } catch {
    return { theme: "light", reducedMotion: false };
  }
}
export function applyDisplay(value = readDisplay()) {
  if (value.theme === "system") document.documentElement.removeAttribute("data-theme");
  else document.documentElement.dataset.theme = value.theme;
  document.documentElement.dataset.reducedMotion = String(value.reducedMotion);
}

export function SettingsPage() {
  const [display, setDisplay] = useState(readDisplay);
  const [notice, setNotice] = useState("");
  function save(next: Display) {
    setDisplay(next);
    applyDisplay(next);
    try {
      localStorage.setItem(key, JSON.stringify(next));
      setNotice("Display preferences saved on this browser.");
    } catch {
      setNotice("This browser could not save preferences. They apply until you close the page.");
    }
  }
  return (
    <Page title="Settings" lead="Your display, recordings and privacy.">
      <div className="rally-stack">
        <Card title="Display">
          <label className="rally-person-select">
            Appearance
            <select
              value={display.theme}
              onChange={(event) => save({ ...display, theme: event.target.value as Display["theme"] })}
            >
              <option value="light">Court Daylight</option>
              <option value="dark">Arena Night</option>
              <option value="system">Use device setting</option>
            </select>
          </label>
          <label className="rally-checkbox">
            <input
              type="checkbox"
              checked={display.reducedMotion}
              onChange={(event) => save({ ...display, reducedMotion: event.target.checked })}
            />
            Reduce motion
          </label>
          <p role="status" className="rally-caption">
            {notice}
          </p>
        </Card>
        <Card title="Privacy and your data">
          <p className="rally-muted">
            Recordings and analytics are held on your connected server. Its access policy applies to playback,
            exports and corrections. Player names in the people view are the labels entered for each
            recording.
          </p>
          <Link to="/library" className="rally-text-action">
            Manage recordings and exports →
          </Link>
        </Card>
        <Card title="Notifications">
          <p className="rally-muted">
            Processing status updates while the app is open. Background email and push notifications are not
            configured on this server.
          </p>
        </Card>
      </div>
    </Page>
  );
}
