export interface ContractZone {
  risk: "low" | "medium" | "high";
  summary: string;
}

export interface UploadResponse {
  success: boolean;
  risk: "low" | "medium" | "high";
  zones: Record<string, ContractZone>;
  report_url: string;
  recommendations: string[];
  emailed: boolean;
  metadata: {
    title: string;
    page_estimate: number;
    char_count: number;
  };
}

export interface ScanRecord {
  id: string;
  filename: string;
  date: string;
  risk: "low" | "medium" | "high" | "pending";
  status: "pending" | "processing" | "done" | "failed";
  reportData?: UploadResponse;
}

export type AccentColor = "indigo" | "purple" | "rose" | "emerald";
export type Density = "comfortable" | "compact";
export type Theme = "dark" | "light";
