import { API_PUBLIC_URL, getApiStatus } from "@/lib/api";

// Always render on request so the API status is live.
export const dynamic = "force-dynamic";

const categories = [
  { id: "mining", name: "Mining", blurb: "Mineral production, exports and reserves." },
  { id: "tourism", name: "Tourism", blurb: "Arrivals, receipts and capacity." },
  { id: "agriculture", name: "Agriculture", blurb: "Crop production, prices and rainfall." },
  { id: "finance", name: "Finance", blurb: "Macro indicators, rates and commodity prices." },
  { id: "healthcare", name: "Healthcare", blurb: "Aggregate health statistics." },
];

export default async function HomePage() {
  const status = await getApiStatus();

  return (
    <div className="space-y-12">
      <section className="space-y-4">
        <h1 className="text-4xl font-bold tracking-tight">Clean African data, ready to use.</h1>
        <p className="max-w-2xl text-lg text-zinc-600 dark:text-zinc-400">
          Mining, tourism, agriculture, finance and healthcare data for all 54 African countries,
          starting with Botswana and the SADC region. Use it through a REST API, ask questions in
          plain English, or download it.
        </p>
      </section>

      <section aria-labelledby="categories-heading" className="space-y-4">
        <h2 id="categories-heading" className="text-xl font-semibold">
          Categories
        </h2>
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {categories.map((c) => (
            <li
              key={c.id}
              className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800"
            >
              <h3 className="font-medium">{c.name}</h3>
              <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">{c.blurb}</p>
            </li>
          ))}
        </ul>
      </section>

      <section
        aria-label="Service status"
        className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-400"
      >
        <span
          aria-hidden
          className={`inline-block h-2.5 w-2.5 rounded-full ${
            status.reachable ? "bg-brand-500" : "bg-red-500"
          }`}
        />
        {status.reachable ? (
          <span>
            API online (v{status.version}) ·{" "}
            <a className="underline" href={`${API_PUBLIC_URL}/docs`}>
              API reference
            </a>
          </span>
        ) : (
          <span>API unreachable ({status.error})</span>
        )}
      </section>
    </div>
  );
}
