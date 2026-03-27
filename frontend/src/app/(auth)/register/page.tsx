import { Suspense } from "react";
import { RegisterForm } from "@/components/auth/register-form";

export default function RegisterPage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4">
      <h1 className="text-2xl font-bold text-text mb-8">Create Account</h1>
      <Suspense
        fallback={<div className="text-text-secondary">Loading...</div>}
      >
        <RegisterForm />
      </Suspense>
      <p className="mt-6 text-text-secondary text-sm">
        Already have an account?{" "}
        <a href="/login" className="text-primary hover:underline">
          Log in
        </a>
      </p>
    </main>
  );
}
