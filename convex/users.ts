import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

// ─── Create User ───────────────────────────────────────
export const create = mutation({
  args: {
    name: v.string(),
    email: v.string(),
    password_hash: v.optional(v.string()),
    avatarUrl: v.optional(v.string()),
    riskProfile: v.optional(v.union(v.literal("conservative"), v.literal("moderate"), v.literal("aggressive"))),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", args.email))
      .first();
    if (existing) return existing._id;

    return await ctx.db.insert("users", {
      ...args,
      preferences: { theme: "dark", focus: "balanced" },
      createdAt: Date.now(),
      lastActiveAt: Date.now(),
    });
  },
});

// ─── Get User by Email ─────────────────────────────────
export const getByEmail = query({
  args: { email: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", args.email))
      .first();
  },
});

// ─── Get User by ID ────────────────────────────────────
export const get = query({
  args: { id: v.id("users") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// ─── List All Users (Admin) ────────────────────────────
export const list = query({
  handler: async (ctx) => {
    return await ctx.db.query("users").collect();
  },
});

// ─── Update User Preferences ──────────────────────────
export const updatePreferences = mutation({
  args: {
    id: v.id("users"),
    riskProfile: v.optional(v.union(v.literal("conservative"), v.literal("moderate"), v.literal("aggressive"))),
    preferences: v.optional(v.object({
      theme: v.optional(v.union(v.literal("light"), v.literal("dark"))),
      focus: v.optional(v.union(v.literal("dividend"), v.literal("growth"), v.literal("value"), v.literal("balanced"))),
    })),
  },
  handler: async (ctx, args) => {
    const { id, ...updates } = args;
    await ctx.db.patch(id, { ...updates, lastActiveAt: Date.now() });
  },
});

// ─── Delete User (Admin) ──────────────────────────────
export const remove = mutation({
  args: { id: v.id("users") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});

// ─── Update Upstox Token ──────────────────────────────
export const updateUpstoxToken = mutation({
  args: {
    id: v.id("users"),
    upstox_access_token: v.optional(v.string())
  },
  handler: async (ctx, args) => {
    const { id, upstox_access_token } = args;
    await ctx.db.patch(id, { upstox_access_token, lastActiveAt: Date.now() });
  }
});

// ─── Save Expo Push Token ─────────────────────────────
export const savePushToken = mutation({
  args: {
    id: v.id("users"),
    pushToken: v.string()
  },
  handler: async (ctx, args) => {
    const { id, pushToken } = args;
    await ctx.db.patch(id, { expoPushToken: pushToken, lastActiveAt: Date.now() });
  }
});
