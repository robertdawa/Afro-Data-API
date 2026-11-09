import type { Metadata } from "next";
import { ComingSoon } from "@/components/coming-soon";

export const metadata: Metadata = { title: "Dashboard" };

export default function Page() {
  return (
    <ComingSoon title="Dashboard" phase={7}>
      Manage API keys and scopes, see usage, and manage your team and billing.
    </ComingSoon>
  );
}
