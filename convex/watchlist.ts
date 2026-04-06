import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

// ─── Add to Watchlist ──────────────────────────────────
export const add = mutation({
  args: {
    userId: v.id("users"),
    symbol: v.string(),
    notes: v.optional(v.string()),
    targetPrice: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("watchlist", {
      ...args,
      addedAt: Date.now(),
    });
  },
});

// ─── List Watchlist by User ────────────────────────────
export const listByUser = query({
  args: { userId: v.id("users") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("watchlist")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .collect();
  },
});

// ─── Remove from Watchlist ─────────────────────────────
export const remove = mutation({
  args: { id: v.id("watchlist") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});
