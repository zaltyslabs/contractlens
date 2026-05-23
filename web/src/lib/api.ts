import { UploadResponse } from "./types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8123";

export async function uploadContract(
  file: File,
  email: string,
  userId?: string
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("email", email);
  if (userId) formData.append("user_id", userId);

  const res = await fetch(`${API_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }

  return res.json();
}

export async function healthCheck(): Promise<{
  status: string;
  version: string;
}> {
  const res = await fetch(`${API_URL}/api/health`);
  return res.json();
}
