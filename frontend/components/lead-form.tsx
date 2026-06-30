"use client";

import { useState, type ReactNode } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { apiBaseUrl, ApiError, type Lead } from "@/lib/api";
import { Spinner } from "@/components/spinner";

const MAX_RESUME_BYTES = 10 * 1024 * 1024;
const PDF_TYPE = "application/pdf";

const schema = z.object({
  first_name: z.string().trim().min(1, "First name is required"),
  last_name: z.string().trim().min(1, "Last name is required"),
  email: z.string().trim().min(1, "Email is required").email("Enter a valid email"),
  // NOTE: `FileList` is browser-only. This is a client component but Next.js
  // still evaluates the module during SSR, where `FileList` is undefined.
  // `z.custom<FileList>()` keeps the static type (so the field error stays a
  // string) while referencing `FileList` only inside refine callbacks, which
  // run on submit (client-side) — avoiding a server-side ReferenceError.
  resume: z
    .custom<FileList>()
    .refine((files) => files instanceof FileList && files.length > 0, "A resume is required")
    .refine((files) => files?.[0]?.type === PDF_TYPE, "Resume must be a PDF")
    .refine(
      (files) => (files?.[0]?.size ?? 0) <= MAX_RESUME_BYTES,
      "Resume must be 10MB or smaller",
    ),
});

type FormValues = z.infer<typeof schema>;

export function LeadForm() {
  const [formError, setFormError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = handleSubmit(async (values) => {
    setFormError(null);
    const body = new FormData();
    body.set("first_name", values.first_name.trim());
    body.set("last_name", values.last_name.trim());
    body.set("email", values.email.trim());
    body.set("resume", values.resume[0]);

    try {
      const res = await fetch(`${apiBaseUrl()}/leads`, { method: "POST", body });
      if (!res.ok) {
        let message = res.statusText;
        try {
          const data = await res.json();
          message = data?.error?.message ?? message;
        } catch {
          /* non-JSON error body */
        }
        throw new ApiError("HTTP_ERROR", message, res.status);
      }
      const lead = (await res.json()) as Lead;
      toast.success("Application submitted", {
        description: `Thanks ${lead.first_name} — we'll be in touch at ${lead.email}.`,
      });
      reset();
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Something went wrong. Please try again.";
      setFormError(message);
      toast.error(message);
    }
  });

  return (
    <form
      onSubmit={onSubmit}
      noValidate
      className="rounded-lg border border-stone-200 bg-white p-8 shadow-sm"
    >
      <div className="flex flex-col gap-5">
        {formError && (
          <div
            role="alert"
            className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
          >
            {formError}
          </div>
        )}

        <Field
          label="First name"
          htmlFor="first_name"
          error={errors.first_name?.message}
        >
          <input
            id="first_name"
            type="text"
            autoComplete="given-name"
            aria-invalid={errors.first_name ? true : undefined}
            aria-describedby={errors.first_name ? "first_name-error" : undefined}
            className={inputClass(!!errors.first_name)}
            {...register("first_name")}
          />
        </Field>

        <Field label="Last name" htmlFor="last_name" error={errors.last_name?.message}>
          <input
            id="last_name"
            type="text"
            autoComplete="family-name"
            aria-invalid={errors.last_name ? true : undefined}
            aria-describedby={errors.last_name ? "last_name-error" : undefined}
            className={inputClass(!!errors.last_name)}
            {...register("last_name")}
          />
        </Field>

        <Field label="Email" htmlFor="email" error={errors.email?.message}>
          <input
            id="email"
            type="email"
            autoComplete="email"
            aria-invalid={errors.email ? true : undefined}
            aria-describedby={errors.email ? "email-error" : undefined}
            className={inputClass(!!errors.email)}
            {...register("email")}
          />
        </Field>

        <Field
          label="Resume (PDF, max 10MB)"
          htmlFor="resume"
          error={errors.resume?.message}
        >
          <input
            id="resume"
            type="file"
            accept=".pdf,application/pdf"
            aria-invalid={errors.resume ? true : undefined}
            aria-describedby={errors.resume ? "resume-error" : undefined}
            className="block w-full text-sm text-stone-600 file:mr-4 file:rounded-md file:border-0 file:bg-stone-100 file:px-4 file:py-2 file:text-sm file:font-medium file:text-stone-700 hover:file:bg-stone-200"
            {...register("resume")}
          />
        </Field>

        <button
          type="submit"
          disabled={isSubmitting}
          className="mt-1 inline-flex items-center justify-center gap-2 rounded-md bg-stone-900 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-stone-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting && <Spinner />}
          {isSubmitting ? "Submitting…" : "Submit application"}
        </button>
      </div>
    </form>
  );
}

function inputClass(hasError: boolean): string {
  return [
    "block w-full rounded-md border bg-white px-3 py-2 text-sm text-stone-900 shadow-sm outline-none transition placeholder:text-stone-400 focus:ring-2",
    hasError
      ? "border-red-300 focus:border-red-400 focus:ring-red-100"
      : "border-stone-300 focus:border-stone-400 focus:ring-stone-100",
  ].join(" ");
}

interface FieldProps {
  label: string;
  htmlFor: string;
  error?: string;
  children: ReactNode;
}

function Field({ label, htmlFor, error, children }: FieldProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={htmlFor} className="text-sm font-medium text-stone-700">
        {label}
      </label>
      {children}
      {error && (
        <p id={`${htmlFor}-error`} className="text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  );
}
