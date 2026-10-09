import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { Logo } from "@/components/AppShell";
import { Button, ErrorNote, Field, inputClass } from "@/components/ui";
import { ApiError, api, setCsrf } from "@/lib/api";

export function LoginPage({ onDone }: { onDone: () => void }) {
  const [pass, setPass] = useState("");
  const login = useMutation({
    mutationFn: () => api.login(pass),
    onSuccess: (r) => {
      setCsrf(r.csrf);
      onDone();
    },
  });
  const err =
    login.error instanceof ApiError && login.error.status === 401
      ? new Error("That passphrase isn't right. It's the BAI_PASSPHRASE value in the server's .env file.")
      : login.error;

  return (
    <div className="grid h-full place-items-center px-4">
      <form
        className="panel w-full max-w-sm space-y-5 p-6"
        onSubmit={(e) => {
          e.preventDefault();
          login.mutate();
        }}
      >
        <div className="flex items-center gap-3">
          <Logo />
          <div>
            <h1 className="text-lg font-semibold">Sign in to Badminton AI</h1>
            <p className="text-sm text-line-2">
              This server is reachable on your network, so it asks for a passphrase.
            </p>
          </div>
        </div>
        <Field label="Passphrase">
          <input
            className={inputClass}
            type="password"
            autoComplete="current-password"
            value={pass}
            onChange={(e) => setPass(e.target.value)}
            // biome-ignore lint/a11y/noAutofocus: the only field on a sign-in screen
            autoFocus
          />
        </Field>
        <ErrorNote error={err} />
        <Button variant="primary" type="submit" className="w-full" busy={login.isPending} disabled={!pass}>
          Sign in
        </Button>
      </form>
    </div>
  );
}
