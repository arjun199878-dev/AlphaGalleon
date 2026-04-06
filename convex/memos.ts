import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

// ─── List Memos ────────────────────────────────────────
export const list = query({
  args: {
    limit: v.optional(v.number()),
    userId: v.optional(v.id("users")),
  },
  handler: async (ctx, args) => {
    const limit = args.limit ?? 20;
    if (args.userId) {
      return await ctx.db
        .query("memos")
        .withIndex("by_user", (q) => q.eq("userId", args.userId!))
        .order("desc")
        .take(limit);
    }
    // Return latest memos across all users
    return await ctx.db
      .query("memos")
      .withIndex("by_date")
      .order("desc")
      .take(limit);
  },
});

// ─── Get Memo by Symbol ────────────────────────────────
export const getBySymbol = query({
  args: { symbol: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("memos")
      .withIndex("by_symbol", (q) => q.eq("symbol", args.symbol))
      .order("desc")
      .first();
  },
});

// ─── Create Memo ──────────────────────────────────────
export const create = mutation({
  args: {
    userId: v.optional(v.id("users")),
    symbol: v.string(),
    verdict: v.union(v.literal("BUY"), v.literal("SELL"), v.literal("HOLD")),
    confidence: v.number(),
    summary: v.string(),
    reasoning: v.string(),
    priceAtGeneration: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("memos", {
      ...args,
      generatedAt: Date.now(),
    });
  },
});
