import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

// ─── Log Activity ──────────────────────────────────────
export const log = mutation({
  args: {
    userId: v.optional(v.id("users")),
    action: v.string(),
    details: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("activityLog", {
      ...args,
      timestamp: Date.now(),
    });
  },
});

// ─── List Recent Activity (Admin) ──────────────────────
export const listRecent = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("activityLog")
      .withIndex("by_time")
      .order("desc")
      .take(args.limit ?? 100);
  },
});

// ─── List Activity by User ─────────────────────────────
export const listByUser = query({
  args: { userId: v.id("users") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("activityLog")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .collect();
  },
});

// ─── Admin Dashboard Stats ─────────────────────────────
export const dashboardStats = query({
  handler: async (ctx) => {
    const users = await ctx.db.query("users").collect();
    const portfolios = await ctx.db.query("portfolios").collect();
    const memos = await ctx.db.query("memos").collect();
    const activePortfolios = portfolios.filter((p) => p.status === "active");

    return {
      totalUsers: users.length,
      totalPortfolios: portfolios.length,
      activePortfolios: activePortfolios.length,
      totalMemos: memos.length,
      recentUsers: users.slice(-5).reverse(),
    };
  },
});
