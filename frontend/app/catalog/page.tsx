import type { Metadata } from "next";
import { ComingSoon } from "@/components/coming-soon";

export const metadata: Metadata = { title: "Catalogue" };

export default function Page() {
  return (
    <ComingSoon title="Catalogue" phase={7}>
      Browse datasets by category, data type and dataset, with licences, previews and charts.
    </ComingSoon>
  );
}
