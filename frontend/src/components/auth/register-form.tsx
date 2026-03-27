"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiPost } from "@/lib/api-client";

interface UserData {
  id: number;
  username: string;
  email: string;
  role: string;
  status: string;
}

type RegistrationPath = "invite" | "approval";

export function RegisterForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const prefillCode = searchParams.get("code") ?? "";

  const [path, setPath] = useState<RegistrationPath>(
    prefillCode ? "invite" : "approval",
  );
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [inviteCode, setInviteCode] = useState(prefillCode);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [pendingApproval, setPendingApproval] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const body: Record<string, unknown> = {
        username,
        email,
        password,
      };
      if (path === "invite" && inviteCode) {
        body.invite_code = inviteCode;
      }

      const res = await apiPost<UserData>("/api/auth/register", body);

      if (res.error) {
        setError(res.error.message);
      } else if (res.data?.status === "pending") {
        setPendingApproval(true);
      } else {
        router.push("/");
      }
    } catch {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  if (pendingApproval) {
    return (
      <div className="text-center space-y-4">
        <div className="text-4xl">⏳</div>
        <h2 className="text-xl font-semibold text-text">Account Created</h2>
        <p className="text-text-secondary">
          Your account is pending admin approval. You will be notified when
          approved.
        </p>
        <a href="/login" className="text-primary hover:underline">
          Back to login
        </a>
      </div>
    );
  }

  return (
    <div className="w-full max-w-sm space-y-6">
      {/* Path selector */}
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setPath("invite")}
          className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
            path === "invite"
              ? "bg-primary text-bg"
              : "bg-surface text-text-secondary hover:bg-surface-hover"
          }`}
        >
          I have an invite code
        </button>
        <button
          type="button"
          onClick={() => setPath("approval")}
          className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
            path === "approval"
              ? "bg-primary text-bg"
              : "bg-surface text-text-secondary hover:bg-surface-hover"
          }`}
        >
          Sign up for approval
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="reg-username"
            className="block text-sm text-text-secondary mb-1"
          >
            Username
          </label>
          <input
            id="reg-username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            minLength={3}
            maxLength={50}
            pattern="^[a-zA-Z0-9_-]+$"
            className="w-full px-3 py-2 bg-surface border border-border rounded-lg text-text focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Username"
          />
        </div>

        <div>
          <label
            htmlFor="reg-email"
            className="block text-sm text-text-secondary mb-1"
          >
            Email
          </label>
          <input
            id="reg-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-3 py-2 bg-surface border border-border rounded-lg text-text focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Email"
          />
        </div>

        <div>
          <label
            htmlFor="reg-password"
            className="block text-sm text-text-secondary mb-1"
          >
            Password
          </label>
          <input
            id="reg-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            className="w-full px-3 py-2 bg-surface border border-border rounded-lg text-text focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Min 8 characters"
          />
        </div>

        {path === "invite" && (
          <div>
            <label
              htmlFor="invite-code"
              className="block text-sm text-text-secondary mb-1"
            >
              Invite Code
            </label>
            <input
              id="invite-code"
              type="text"
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value)}
              required
              className="w-full px-3 py-2 bg-surface border border-border rounded-lg text-text focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Enter invite code"
            />
          </div>
        )}

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
          ) : path === "invite" ? (
            "Register with Invite"
          ) : (
            "Sign Up for Approval"
          )}
        </button>
      </form>
    </div>
  );
}
