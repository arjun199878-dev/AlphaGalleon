import { action } from "./_generated/server";

export const triggerGlobalScan = action({
  // No args needed for global scheduled action
  handler: async (ctx) => {
    try {
      // In production, this would be your deployed FastAPI URL (e.g., https://api.alphagalleon.com)
      // Since FASTAPI_URL env var could exist in Convex dashboard, we'll use that or fallback
      const backendUrl = process.env.FASTAPI_URL || "https://alphagalleon-backend.vercel.app";
      
      const response = await fetch(`${backendUrl}/api/v1/sentinel/global-scan`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // Adding a chronos token for basic API security
          "Authorization": `Bearer ${process.env.CRON_SECRET || 'alpha-galleon-cron-secure'}`, 
        },
      });

      if (!response.ok) {
        throw new Error(`FastAPI returned ${response.status}`);
      }
      
      console.log("Global Scan Triggered Successfully at", new Date().toISOString());
      return { success: true };
    } catch (error) {
      console.error("Failed to trigger Global Sentinel Scan from Convex:", error);
      return { success: false, error: String(error) };
    }
  },
});
