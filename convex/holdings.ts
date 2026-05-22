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

// ─── Sync Broker Holdings ─────────────────────────────
export const sync = mutation({
  args: {
    userId: v.id("users"),
    holdings: v.any() // List of arbitrary holding data from broker
  },
  handler: async (ctx, args) => {
    // Basic sync logic: find existing default portfolio, or create one.
    // Clear old holdings and insert new ones.

    let portfolio = await ctx.db
      .query("portfolios")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .first();

    if (!portfolio) {
        const portId = await ctx.db.insert("portfolios", {
            userId: args.userId,
            name: "Default Portfolio",
            capital: 0,
            riskProfile: "moderate",
            timeHorizon: "long-term",
            status: "active",
            createdAt: Date.now(),
            updatedAt: Date.now(),
        });
        portfolio = await ctx.db.get(portId);
    }

    // Clear old
    const oldHoldings = await ctx.db
      .query("holdings")
      .withIndex("by_portfolio", (q) => q.eq("portfolioId", portfolio!._id))
      .collect();

    for (const h of oldHoldings) {
        await ctx.db.delete(h._id);
    }

    // Insert new
    for (const h of args.holdings) {
        await ctx.db.insert("holdings", {
            portfolioId: portfolio!._id,
            userId: args.userId,
            symbol: h.tradingsymbol || h.instrument_token || h.symbol || "UNKNOWN",
            quantity: h.quantity || 0,
            avgBuyPrice: h.average_price || h.buy_price || 0,
            addedAt: Date.now()
        });
    }
  }
});
