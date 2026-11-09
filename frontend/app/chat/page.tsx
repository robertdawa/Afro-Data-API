import type { Metadata } from "next";
import { ComingSoon } from "@/components/coming-soon";

export const metadata: Metadata = { title: "Ask AI" };

export default function Page() {
  return (
    <ComingSoon title="Ask AI" phase={6}>
      Ask questions about African data in plain English and get answers with tables, charts and sources.
    </ComingSoon>
  );
}
