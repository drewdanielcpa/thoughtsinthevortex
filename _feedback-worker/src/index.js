// Thoughts in the Vortex: anonymous feedback and topic suggestions.
// Cloudflare Worker + D1. Stores no name, email, IP address or user agent.
//
//   POST /submit                 public: {kind, writeup, writeup_title, message, website, t}
//   GET  /entries[?kind=&status=]  admin: JSON list (Authorization: Bearer <ADMIN_KEY>)
//   GET  /entries.csv              admin: CSV export
//   POST /entries/<id>/status      admin: {status: "new" | "read" | "archived"}

const MAX_MESSAGE = 5000;
const MIN_MESSAGE = 3;
const DAILY_LIMIT = 10;        // submissions per visitor per day (tracked by a one-way daily hash)
const MIN_FILL_MS = 2500;      // forms filled faster than this are treated as bots

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    const allowed = (env.ALLOWED_ORIGINS || "").split(",").map(s => s.trim()).filter(Boolean);
    const cors = corsHeaders(origin, allowed);

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });

    try {
      if (url.pathname === "/submit" && request.method === "POST") {
        if (origin && !allowed.includes(origin)) return json({ ok: false, error: "Origin not allowed" }, 403, cors);
        return await submit(request, env, cors);
      }
      if (url.pathname === "/entries" || url.pathname === "/entries.csv" || url.pathname.startsWith("/entries/")) {
        if (!(await isAdmin(request, env))) return json({ ok: false, error: "Unauthorized" }, 401, cors);
        if (request.method === "GET" && url.pathname === "/entries") return await list(url, env, cors, false);
        if (request.method === "GET" && url.pathname === "/entries.csv") return await list(url, env, cors, true);
        const m = url.pathname.match(/^\/entries\/(\d+)\/status$/);
        if (m && request.method === "POST") return await setStatus(Number(m[1]), request, env, cors);
      }
      if (url.pathname === "/" && request.method === "GET") return json({ ok: true, service: "Thoughts in the Vortex feedback" }, 200, cors);
      return json({ ok: false, error: "Not found" }, 404, cors);
    } catch (err) {
      console.error(err);
      return json({ ok: false, error: "Server error" }, 500, cors);
    }
  },
};

async function submit(request, env, cors) {
  let body;
  try { body = await request.json(); } catch { return json({ ok: false, error: "Bad request" }, 400, cors); }

  // Bots: the hidden "website" field is filled, or the form was sent implausibly fast. Pretend success, store nothing.
  if ((body.website && String(body.website).trim()) || (Number(body.t) > 0 && Number(body.t) < MIN_FILL_MS)) {
    return json({ ok: true }, 200, cors);
  }

  const kind = body.kind === "suggestion" ? "suggestion" : body.kind === "feedback" ? "feedback" : null;
  if (!kind) return json({ ok: false, error: "Choose feedback or a suggestion." }, 400, cors);

  const message = clean(body.message, MAX_MESSAGE);
  if (message.length < MIN_MESSAGE) return json({ ok: false, error: "Please write a little more." }, 400, cors);

  let writeup = null, writeupTitle = null;
  if (kind === "feedback") {
    writeup = clean(body.writeup, 80);
    writeupTitle = clean(body.writeup_title, 200);
    if (!writeup) return json({ ok: false, error: "Choose which write-up this is about." }, 400, cors);
  }

  // Rate limit without keeping the IP: a one-way hash of (secret, IP, date) that is discarded the next day.
  const day = new Date().toISOString().slice(0, 10);
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  const key = await sha256(`${env.ADMIN_KEY}|${ip}|${day}`);
  await env.DB.prepare("DELETE FROM ratelimit WHERE day <> ?").bind(day).run();
  const row = await env.DB.prepare("SELECT count FROM ratelimit WHERE key = ?").bind(key).first();
  if (row && row.count >= DAILY_LIMIT) {
    return json({ ok: false, error: "Thanks! You've sent the most we take from one visitor in a day. Please try again tomorrow." }, 429, cors);
  }
  await env.DB.batch([
    env.DB.prepare("INSERT INTO ratelimit (key, day, count) VALUES (?, ?, 1) ON CONFLICT(key) DO UPDATE SET count = count + 1").bind(key, day),
    env.DB.prepare("INSERT INTO entries (created_at, kind, writeup, writeup_title, message) VALUES (?, ?, ?, ?, ?)")
      .bind(new Date().toISOString(), kind, writeup, writeupTitle, message),
  ]);
  return json({ ok: true }, 200, cors);
}

async function list(url, env, cors, csv) {
  const where = [], args = [];
  const kind = url.searchParams.get("kind");
  const status = url.searchParams.get("status");
  if (kind === "feedback" || kind === "suggestion") { where.push("kind = ?"); args.push(kind); }
  if (["new", "read", "archived"].includes(status)) { where.push("status = ?"); args.push(status); }
  const sql = `SELECT id, created_at, kind, writeup, writeup_title, message, status FROM entries${where.length ? " WHERE " + where.join(" AND ") : ""} ORDER BY id DESC`;
  const { results } = await env.DB.prepare(sql).bind(...args).all();
  if (!csv) return json({ ok: true, entries: results }, 200, cors);
  const cols = ["id", "created_at", "kind", "writeup", "writeup_title", "message", "status"];
  const esc = v => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const text = "﻿" + [cols.join(","), ...results.map(r => cols.map(c => esc(r[c])).join(","))].join("\r\n");
  return new Response(text, {
    headers: { ...cors, "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="vortex-feedback-${new Date().toISOString().slice(0, 10)}.csv"` },
  });
}

async function setStatus(id, request, env, cors) {
  let body;
  try { body = await request.json(); } catch { return json({ ok: false, error: "Bad request" }, 400, cors); }
  if (!["new", "read", "archived"].includes(body.status)) return json({ ok: false, error: "Bad status" }, 400, cors);
  await env.DB.prepare("UPDATE entries SET status = ? WHERE id = ?").bind(body.status, id).run();
  return json({ ok: true }, 200, cors);
}

async function isAdmin(request, env) {
  const h = request.headers.get("Authorization") || "";
  const given = h.startsWith("Bearer ") ? h.slice(7) : "";
  if (!env.ADMIN_KEY || !given) return false;
  // Compare hashes so the comparison time doesn't depend on how much of the key matches.
  const [a, b] = await Promise.all([sha256(given), sha256(env.ADMIN_KEY)]);
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

function clean(v, max) {
  return String(v ?? "").replace(/\r\n?/g, "\n").replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "").trim().slice(0, max);
}

async function sha256(s) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, "0")).join("");
}

function corsHeaders(origin, allowed) {
  const h = { "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type, Authorization", "Access-Control-Max-Age": "86400", "Vary": "Origin" };
  if (allowed.includes(origin)) h["Access-Control-Allow-Origin"] = origin;
  return h;
}

function json(obj, status, cors) {
  return new Response(JSON.stringify(obj), { status, headers: { ...cors, "Content-Type": "application/json" } });
}
