import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4">
      <h1 className="text-2xl font-bold text-text mb-8">
        Log in to TopTop Music
      </h1>
      <LoginForm />
      <p className="mt-6 text-text-secondary text-sm">
        Don&apos;t have an account?{" "}
        <a href="/register" className="text-primary hover:underline">
          Register
        </a>
      </p>
    </main>
  );
}
