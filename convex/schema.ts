import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // ─── Users ───────────────────────────────────────────
  users: defineTable({
    name: v.string(),
    email: v.string(),
    password_hash: v.optional(v.string()), // For authentication
    avatarUrl: v.optional(v.string()),
    riskProfile: v.optional(v.union(v.literal("conservative"), v.literal("moderate"), v.literal("aggressive"))),
    preferences: v.optional(v.object({
      theme: v.optional(v.union(v.literal("light"), v.literal("dark"))),
      focus: v.optional(v.union(v.literal("dividend"), v.literal("growth"), v.literal("value"), v.literal("balanced"))),
    })),
    createdAt: v.number(),
    lastActiveAt: v.optional(v.number()),
    upstox_access_token: v.optional(v.string())
  }).index("by_email", ["email"]),

  // ─── Portfolios ──────────────────────────────────────
  portfolios: defineTable({
    userId: v.id("users"),
    name: v.string(),
    capital: v.number(),
    riskProfile: v.union(v.literal("conservative"), v.literal("moderate"), v.literal("aggressive")),
    timeHorizon: v.string(),
    status: v.union(v.literal("active"), v.literal("archived")),
    createdAt: v.number(),
    updatedAt: v.number(),
  }).index("by_user", ["userId"]),

  // ─── Holdings (stocks within a portfolio) ────────────
  holdings: defineTable({
    portfolioId: v.id("portfolios"),
    userId: v.id("users"),
    symbol: v.string(),
    quantity: v.number(),
    avgBuyPrice: v.number(),
    allocation: v.optional(v.number()), // percentage weight
    addedAt: v.number(),
  })
    .index("by_portfolio", ["portfolioId"])
    .index("by_user", ["userId"])
    .index("by_symbol", ["symbol"]),

  // ─── Watchlist ───────────────────────────────────────
  watchlist: defineTable({
    userId: v.id("users"),
    symbol: v.string(),
    notes: v.optional(v.string()),
    targetPrice: v.optional(v.number()),
    addedAt: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_symbol", ["symbol"]),

  // ─── Investment Memos (Brain output) ─────────────────
  memos: defineTable({
    userId: v.optional(v.id("users")),
    symbol: v.string(),
    verdict: v.union(v.literal("BUY"), v.literal("SELL"), v.literal("HOLD")),
    confidence: v.number(), // 0-100
    summary: v.string(),
    reasoning: v.string(),
    priceAtGeneration: v.optional(v.number()),
    generatedAt: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_symbol", ["symbol"])
    .index("by_date", ["generatedAt"]),

  // ─── Diagnosis Reports (Doctor output) ───────────────
  diagnoses: defineTable({
    userId: v.id("users"),
    portfolioId: v.id("portfolios"),
    overallScore: v.number(), // 0-100
    risks: v.array(v.object({
      type: v.string(),
      severity: v.union(v.literal("low"), v.literal("medium"), v.literal("high"), v.literal("critical")),
      description: v.string(),
    })),
    recommendations: v.array(v.string()),
    generatedAt: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_portfolio", ["portfolioId"]),

  // ─── Backtest Results ────────────────────────────────
  backtests: defineTable({
    userId: v.id("users"),
    portfolioId: v.optional(v.id("portfolios")),
    holdings: v.array(v.object({
      symbol: v.string(),
      allocation: v.number(),
    })),
    durationYears: v.number(),
    totalReturn: v.number(),
    cagr: v.optional(v.number()),
    maxDrawdown: v.optional(v.number()),
    sharpeRatio: v.optional(v.number()),
    resultData: v.optional(v.string()), // JSON string for chart data
    generatedAt: v.number(),
  })
    .index("by_user", ["userId"]),

  // ─── Activity Log (admin audit trail) ────────────────
  activityLog: defineTable({
    userId: v.optional(v.id("users")),
    action: v.string(),
    details: v.optional(v.string()),
    timestamp: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_time", ["timestamp"]),
});
