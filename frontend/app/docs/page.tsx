import type { Metadata } from "next";
import { ComingSoon } from "@/components/coming-soon";

export const metadata: Metadata = { title: "Docs" };

export default function Page() {
  return (
    <ComingSoon title="Docs" phase={9}>
      Quick start, authentication, scopes, endpoints, and examples in Python, JavaScript, R and Excel.
    </ComingSoon>
  );
}
