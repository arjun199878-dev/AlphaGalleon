import { cronJobs } from "convex/server";
import { internal } from "./_generated/api";

const crons = cronJobs();

// Schedule the Sentinel to wake up everyday at Market Close (approx 4 PM IST = 10:30 AM UTC)
// This will evaluate portfolios based on EOD data and alert users if drawdowns hit
crons.daily(
  "trigger-sentinel-market-close",
  { hourUTC: 10, minuteUTC: 30 },
  // Note: we can't directly call an action from cron in earlier Convex versions without using internal or public action reference
  // We defined a public action `triggerGlobalScan` in actions.ts, let's call it via api reference (will compile when generated)
  // Wait, the correct way is using api.actions.triggerGlobalScan or internal.actions.triggerGlobalScan.
  // We'll export it as a public action so `api.actions.triggerGlobalScan` works.
  // But wait, the string needs to be valid. The compiler will check `api`.
  // Using an inline function isn't supported for crons, we pass the function reference.
  "actions:triggerGlobalScan" as any
);

export default crons;
