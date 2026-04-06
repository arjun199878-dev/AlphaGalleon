import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

// ─── Add Holding ───────────────────────────────────────
export const add = mutation({
  args: {
    portfolioId: v.id("portfolios"),
    userId: v.id("users"),
    symbol: v.string(),
    quantity: v.number(),
    avgBuyPrice: v.number(),
    allocation: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("holdings", {
      ...args,
      addedAt: Date.now(),
    });
  },
});

// ─── List Holdings by Portfolio ────────────────────────
export const listByPortfolio = query({
  args: { portfolioId: v.id("portfolios") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("holdings")
      .withIndex("by_portfolio", (q) => q.eq("portfolioId", args.portfolioId))
      .collect();
  },
});

// ─── List Holdings by User ─────────────────────────────
export const listByUser = query({
  args: { userId: v.id("users") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("holdings")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .collect();
  },
});

// ─── Remove Holding ────────────────────────────────────
export const remove = mutation({
  args: { id: v.id("holdings") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});

// ─── Update Holding ────────────────────────────────────
export const update = mutation({
  args: {
    id: v.id("holdings"),
    quantity: v.optional(v.number()),
    avgBuyPrice: v.optional(v.number()),
    allocation: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const { id, ...updates } = args;
    await ctx.db.patch(id, updates);
  },
});
