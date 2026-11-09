export function ComingSoon({ title, phase, children }: { title: string; phase: number; children: React.ReactNode }) {
  return (
    <div className="space-y-3">
      <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
      <p className="max-w-2xl text-zinc-600 dark:text-zinc-400">{children}</p>
      <p className="text-sm text-zinc-500">Planned for build phase {phase}.</p>
    </div>
  );
}
