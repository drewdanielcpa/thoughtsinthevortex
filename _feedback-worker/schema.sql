CREATE TABLE IF NOT EXISTS entries (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at    TEXT NOT NULL,
  kind          TEXT NOT NULL CHECK (kind IN ('feedback', 'suggestion')),
  writeup       TEXT,
  writeup_title TEXT,
  message       TEXT NOT NULL,
  status        TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'read', 'archived'))
);
CREATE INDEX IF NOT EXISTS entries_kind ON entries (kind, status);

CREATE TABLE IF NOT EXISTS ratelimit (
  key   TEXT PRIMARY KEY,
  day   TEXT NOT NULL,
  count INTEGER NOT NULL
);
