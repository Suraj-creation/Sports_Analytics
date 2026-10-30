import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { Logo } from "@/components/AppShell";
import { Button, ErrorNote, Field, inputClass } from "@/components/ui";
import { ApiError, api, setCsrf } from "@/lib/api";
import "@/features/product/product.css";

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
      ? new Error("That passphrase wasn’t accepted. Check it and try again.")
      : login.error;

  return (
    <div className="rally-login">
      <form
        className="rally-login-form"
        onSubmit={(e) => {
          e.preventDefault();
          login.mutate();
        }}
      >
        <div className="rally-login-brand">
          <Logo />
        </div>
        <div>
          <h1>Sign in to Rally</h1>
          <p>Enter your server passphrase to access your recordings and match workspace.</p>
        </div>
        <Field label="Passphrase">
          <input
            className={inputClass}
            type="password"
            autoComplete="current-password"
            required
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
