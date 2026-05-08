import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

// ─── Create Portfolio ──────────────────────────────────
export const create = mutation({
  args: {
    userId: v.id("users"),
    name: v.string(),
    capital: v.number(),
    riskProfile: v.union(v.literal("conservative"), v.literal("moderate"), v.literal("aggressive")),
    timeHorizon: v.string(),
  },
  handler: async (ctx, args) => {
    const now = Date.now();
    return await ctx.db.insert("portfolios", {
      ...args,
      status: "active",
      createdAt: now,
      updatedAt: now,
    });
  },
});
// ─── Sync Upstox Live Portfolio ─────────────────────────
export const syncUpstox = mutation({
  args: {
    userId: v.id("users"),
    holdings: v.array(
        v.object({
            symbol: v.string(),
            quantity: v.number(),
            avgBuyPrice: v.number()
        })
    )
  },
  handler: async (ctx, args) => {
      const now = Date.now();
      
      // Look for existing Upstox Live portfolio
      let portfolio = await ctx.db
          .query("portfolios")
          .withIndex("by_user", (q) => q.eq("userId", args.userId))
          .filter((q) => q.eq(q.field("name"), "Upstox Live"))
          .first();

      let portfolioId;

      if (!portfolio) {
          portfolioId = await ctx.db.insert("portfolios", {
              userId: args.userId,
              name: "Upstox Live",
              capital: 0,
              riskProfile: "moderate",
              timeHorizon: "Live",
              status: "active",
              createdAt: now,
              updatedAt: now,
          });
      } else {
          portfolioId = portfolio._id;
          await ctx.db.patch(portfolioId, { updatedAt: now });

          // Clear existing holdings for this portfolio
          const existingHoldings = await ctx.db
            .query("holdings")
            .withIndex("by_portfolio", (q) => q.eq("portfolioId", portfolioId))
            .collect();
            
          for (const h of existingHoldings) {
              await ctx.db.delete(h._id);
          }
      }

      // Insert new fresh holdings
      for (const holding of args.holdings) {
          await ctx.db.insert("holdings", {
              portfolioId: portfolioId,
              userId: args.userId,
              symbol: holding.symbol,
              quantity: holding.quantity,
              avgBuyPrice: holding.avgBuyPrice,
              addedAt: now
          });
      }

      return portfolioId;
  }
});
// ─── List Portfolios by User ───────────────────────────
export const listByUser = query({
  args: { userId: v.id("users") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("portfolios")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .collect();
  },
});

// ─── List All Portfolios (Admin) ───────────────────────
export const listAll = query({
  handler: async (ctx) => {
    return await ctx.db.query("portfolios").collect();
  },
});

// ─── Get Portfolio ─────────────────────────────────────
export const get = query({
  args: { id: v.id("portfolios") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// ─── Archive Portfolio ─────────────────────────────────
export const archive = mutation({
  args: { id: v.id("portfolios") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { status: "archived", updatedAt: Date.now() });
  },
});
