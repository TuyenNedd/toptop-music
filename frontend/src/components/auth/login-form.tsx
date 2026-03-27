"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiPost } from "@/lib/api-client";

interface TokenData {
  access_token: string;
  token_type: string;
}

export function LoginForm() {
  const router = useRouter();
  const [usernameOrEmail, setUsernameOrEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await apiPost<TokenData>("/api/auth/login", {
        username_or_email: usernameOrEmail,
        password,
      });

      if (res.error) {
        setError(res.error.message);
      } else {
        // Store token and redirect
        if (res.data?.access_token) {
          localStorage.setItem("access_token", res.data.access_token);
        }
        router.push("/");
      }
    } catch {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 w-full max-w-sm">
      <div>
        <label
          htmlFor="username"
          className="block text-sm text-text-secondary mb-1"
        >
          Username or Email
        </label>
        <input
          id="username"
          type="text"
          value={usernameOrEmail}
          onChange={(e) => setUsernameOrEmail(e.target.value)}
          required
          className="w-full px-3 py-2 bg-surface border border-border rounded-lg text-text focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="Username or email"
        />
      </div>

      <div>
        <label
          htmlFor="password"
          className="block text-sm text-text-secondary mb-1"
        >
          Password
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
          className="w-full px-3 py-2 bg-surface border border-border rounded-lg text-text focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="Password"
        />
      </div>

      {error && (
        <p className="text-error text-sm" role="alert">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full py-2 bg-primary text-bg font-semibold rounded-lg hover:opacity-90 disabled:opacity-50 transition-opacity"
      >
        {loading ? (
          <span className="inline-block w-5 h-5 border-2 border-bg border-t-transparent rounded-full animate-spin" />
        ) : (
          "Log in"
        )}
      </button>
    </form>
  );
}
