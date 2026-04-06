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
