import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Emits a self-contained server bundle for the production image (Phase 10).
  output: "standalone",
};

export default nextConfig;
