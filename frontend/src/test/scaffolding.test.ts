/**
 * Tests for frontend project scaffolding (Story 1.2)
 * Verifies structure, config files, and key content.
 */
import { readFileSync, existsSync } from "fs";
import { resolve } from "path";
import { describe, it, expect } from "vitest";

const ROOT = resolve(__dirname, "../../");

describe("Frontend Project Scaffolding", () => {
  describe("Directory structure", () => {
    it("src/app/ directory exists", () => {
      expect(existsSync(resolve(ROOT, "src/app"))).toBe(true);
    });

    it("src/app/layout.tsx exists", () => {
      expect(existsSync(resolve(ROOT, "src/app/layout.tsx"))).toBe(true);
    });

    it("src/app/globals.css exists", () => {
      expect(existsSync(resolve(ROOT, "src/app/globals.css"))).toBe(true);
    });

    it("next.config.ts exists", () => {
      expect(existsSync(resolve(ROOT, "next.config.ts"))).toBe(true);
    });

    it(".env.example exists", () => {
      expect(existsSync(resolve(ROOT, ".env.example"))).toBe(true);
    });

    it("tsconfig.json exists", () => {
      expect(existsSync(resolve(ROOT, "tsconfig.json"))).toBe(true);
    });
  });

  describe("globals.css — color token system", () => {
    const css = readFileSync(resolve(ROOT, "src/app/globals.css"), "utf-8");

    it("contains all 14 CSS variable tokens", () => {
      const tokens = [
        "--color-primary",
        "--color-secondary",
        "--color-bg",
        "--color-surface",
        "--color-surface-hover",
        "--color-surface-active",
        "--color-text",
        "--color-text-secondary",
        "--color-text-tertiary",
        "--color-border",
        "--color-success",
        "--color-warning",
        "--color-error",
      ];
      for (const token of tokens) {
        expect(css, `Missing token: ${token}`).toContain(token);
      }
    });

    it("primary color is #25f4ee (TikTok cyan)", () => {
      expect(css).toContain("#25f4ee");
    });

    it("secondary color is #fe2c55 (TikTok red)", () => {
      expect(css).toContain("#fe2c55");
    });

    it("has .dark override block", () => {
      expect(css).toContain(".dark");
    });

    it("dark bg is #010101", () => {
      expect(css).toContain("#010101");
    });

    it("uses @theme inline (not bare @theme)", () => {
      expect(css).toContain("@theme inline");
    });
  });

  describe("layout.tsx — root layout", () => {
    const layout = readFileSync(resolve(ROOT, "src/app/layout.tsx"), "utf-8");

    it('sets lang="vi" on html element', () => {
      expect(layout).toContain('lang="vi"');
    });

    it("applies dark class by default", () => {
      expect(layout).toContain("dark");
    });

    it("uses Inter font variable", () => {
      expect(layout).toContain("Inter");
      expect(layout).toContain("--font-inter");
    });

    it("imports globals.css", () => {
      expect(layout).toContain("globals.css");
    });
  });

  describe("next.config.ts — BFF proxy", () => {
    const config = readFileSync(resolve(ROOT, "next.config.ts"), "utf-8");

    it("contains rewrites function", () => {
      expect(config).toContain("rewrites");
    });

    it("proxies /api/* to backend", () => {
      expect(config).toContain("/api/:path*");
    });

    it("uses BACKEND_URL env var", () => {
      expect(config).toContain("BACKEND_URL");
    });
  });

  describe(".env.example", () => {
    const env = readFileSync(resolve(ROOT, ".env.example"), "utf-8");

    it("contains NEXT_PUBLIC_APP_URL", () => {
      expect(env).toContain("NEXT_PUBLIC_APP_URL");
    });

    it("contains BACKEND_URL", () => {
      expect(env).toContain("BACKEND_URL");
    });
  });

  describe("tsconfig.json", () => {
    // String search instead of JSON.parse — tsconfig uses JSONC (comments allowed)
    const tsconfig = readFileSync(resolve(ROOT, "tsconfig.json"), "utf-8");

    it("has strict mode enabled", () => {
      expect(tsconfig).toContain('"strict": true');
    });

    it("has @/* path alias", () => {
      expect(tsconfig).toContain('"@/*"');
    });
  });
});
