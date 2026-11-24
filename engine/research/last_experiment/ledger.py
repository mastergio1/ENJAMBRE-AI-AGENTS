"""L6 — Ledger sellado append-only (SQLite) y estructuras de pronóstico/resultado.

Base AISLADA del experimento (no toca la SQLite de producción). Separa eventos,
pronósticos, resoluciones y fallos (I.8). `INSERT` transaccional, nunca `REPLACE`/
`UPDATE` de pronósticos. Repetir un sellado idéntico devuelve la fila original; si el
hash difiere, es error de integridad. Triggers bloquean UPDATE/DELETE de pronósticos y
outcomes. Exportación hash-chain para auditoría.

Honestidad (I.8): un hash local NO vuelve la base invulnerable a un administrador con
acceso de escritura directo. Se documenta la amenaza; no se vende como criptográfica-
mente inmutable. Los triggers defienden del uso normal de la app, no de `sqlite3` crudo.
"""
from __future__ import annotations

import datetime as dt
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path

from .config import hash_canonico


@dataclass(frozen=True)
class SealedForecast:
    experiment_id: str
    event_id: str
    model_id: str          # P0..P5
    symbol: str            # SPY
    issued_at: str         # UTC aware ISO
    cutoff_at: str
    deadline_at: str
    p_up: float            # finito; 0 <= p <= 1
    abstained: bool        # decisión, no ausencia de probabilidad
    model_hash: str
    evidence_hash: str
    config_hash: str
    feature_hash: str
    code_commit: str
    latency_ms: int
    cost_usd: float

    def validar(self) -> None:
        if not (isinstance(self.p_up, (int, float)) and 0.0 <= self.p_up <= 1.0):
            raise ValueError(f"p_up inválido: {self.p_up}")
        for c in (self.issued_at, self.cutoff_at, self.deadline_at):
            d = dt.datetime.fromisoformat(c)
            if d.tzinfo is None:
                raise ValueError("timestamps del pronóstico deben ser aware (UTC)")
        if dt.datetime.fromisoformat(self.issued_at) > dt.datetime.fromisoformat(self.deadline_at):
            raise ValueError("issued_at posterior al deadline (sellado tardío)")

    @property
    def row_hash(self) -> str:
        return hash_canonico(asdict(self))


@dataclass(frozen=True)
class Outcome:
    event_id: str
    entry_session: str
    exit_session: str
    entry_price: float
    exit_price: float
    return_decimal: float
    label_available_at: str
    data_hash: str
    resolved_at: str

    @property
    def y(self) -> int:
        return 1 if self.return_decimal > 0 else 0  # subida ESTRICTA


@dataclass(frozen=True)
class RunFailure:
    event_id: str
    model_id: str
    reason: str
    timestamp: str


_ESQUEMA = """
CREATE TABLE IF NOT EXISTS le_experiment (
  experiment_id TEXT PRIMARY KEY, manifest_hash TEXT, commit_sha TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS le_event (
  event_id TEXT PRIMARY KEY, experiment_id TEXT, symbol TEXT,
  cutoff_utc TEXT, deadline_utc TEXT, entry_session TEXT, exit_session TEXT,
  evidence_hash TEXT, version TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS le_forecast (
  forecast_id TEXT PRIMARY KEY, experiment_id TEXT, event_id TEXT, model_id TEXT,
  symbol TEXT, issued_at TEXT, cutoff_at TEXT, deadline_at TEXT,
  p_up REAL, abstained INTEGER, model_hash TEXT, evidence_hash TEXT,
  config_hash TEXT, feature_hash TEXT, code_commit TEXT, latency_ms INTEGER,
  cost_usd REAL, row_hash TEXT, prev_hash TEXT, chain_hash TEXT, created_at TEXT,
  UNIQUE(experiment_id, event_id, model_id));
CREATE TABLE IF NOT EXISTS le_outcome (
  event_id TEXT PRIMARY KEY, entry_session TEXT, exit_session TEXT,
  entry_price REAL, exit_price REAL, return_decimal REAL,
  label_available_at TEXT, data_hash TEXT, resolved_at TEXT);
CREATE TABLE IF NOT EXISTS le_failure (
  id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT, model_id TEXT,
  reason TEXT, timestamp TEXT);
-- Triggers: bloquear modificación/borrado de pronósticos y outcomes (uso normal).
CREATE TRIGGER IF NOT EXISTS le_forecast_no_update BEFORE UPDATE ON le_forecast
BEGIN SELECT RAISE(ABORT, 'le_forecast es append-only'); END;
CREATE TRIGGER IF NOT EXISTS le_forecast_no_delete BEFORE DELETE ON le_forecast
BEGIN SELECT RAISE(ABORT, 'le_forecast es append-only'); END;
CREATE TRIGGER IF NOT EXISTS le_outcome_no_update BEFORE UPDATE ON le_outcome
BEGIN SELECT RAISE(ABORT, 'le_outcome es inmutable'); END;
CREATE TRIGGER IF NOT EXISTS le_outcome_no_delete BEFORE DELETE ON le_outcome
BEGIN SELECT RAISE(ABORT, 'le_outcome es inmutable'); END;
"""


class Ledger:
    def __init__(self, ruta: str | Path):
        self.ruta = str(ruta)
        self.cx = sqlite3.connect(self.ruta)
        self.cx.row_factory = sqlite3.Row
        self.cx.executescript(_ESQUEMA)
        self.cx.commit()

    def cerrar(self):
        self.cx.close()

    # ----------------------------------------------------------- experimento
    def registrar_experimento(self, experiment_id: str, manifest_hash: str,
                              commit_sha: str) -> None:
        self.cx.execute(
            "INSERT OR IGNORE INTO le_experiment VALUES (?,?,?,?)",
            (experiment_id, manifest_hash, commit_sha, _ahora()))
        self.cx.commit()

    def registrar_evento(self, experiment_id: str, event_id: str, symbol: str,
                         cutoff_utc: str, deadline_utc: str, entry_session: str,
                         exit_session: str, evidence_hash: str, version: str) -> None:
        self.cx.execute(
            "INSERT OR IGNORE INTO le_event VALUES (?,?,?,?,?,?,?,?,?,?)",
            (event_id, experiment_id, symbol, cutoff_utc, deadline_utc,
             entry_session, exit_session, evidence_hash, version, _ahora()))
        self.cx.commit()

    # ------------------------------------------------------------- pronóstico
    def _ultimo_chain(self) -> str:
        r = self.cx.execute(
            "SELECT chain_hash FROM le_forecast ORDER BY created_at DESC, forecast_id DESC LIMIT 1"
        ).fetchone()
        return r["chain_hash"] if r else ""

    def sellar(self, f: SealedForecast) -> dict:
        """Sella un pronóstico. Idempotente: repetir idéntico devuelve la fila
        original; hash distinto para misma clave → IntegrityError lógico."""
        f.validar()
        fid = hash_canonico({"e": f.experiment_id, "ev": f.event_id, "m": f.model_id})[:24]
        ya = self.cx.execute(
            "SELECT * FROM le_forecast WHERE experiment_id=? AND event_id=? AND model_id=?",
            (f.experiment_id, f.event_id, f.model_id)).fetchone()
        if ya:
            if ya["row_hash"] != f.row_hash:
                raise IntegrityError(
                    f"sellado divergente para {f.event_id}/{f.model_id}: "
                    f"hash existente {ya['row_hash'][:8]} != nuevo {f.row_hash[:8]}")
            return {"estado": "idempotente", "forecast_id": ya["forecast_id"]}
        prev = self._ultimo_chain()
        chain = hash_canonico({"prev": prev, "row": f.row_hash})
        self.cx.execute(
            "INSERT INTO le_forecast VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (fid, f.experiment_id, f.event_id, f.model_id, f.symbol, f.issued_at,
             f.cutoff_at, f.deadline_at, f.p_up, int(f.abstained), f.model_hash,
             f.evidence_hash, f.config_hash, f.feature_hash, f.code_commit,
             f.latency_ms, f.cost_usd, f.row_hash, prev, chain, _ahora()))
        self.cx.commit()
        return {"estado": "sellado", "forecast_id": fid, "chain_hash": chain}

    # --------------------------------------------------------------- outcome
    def resolver(self, o: Outcome) -> dict:
        """Inserta outcome maduro. No sobreescribe: si existe con hash distinto, error."""
        ya = self.cx.execute(
            "SELECT * FROM le_outcome WHERE event_id=?", (o.event_id,)).fetchone()
        if ya:
            if ya["data_hash"] != o.data_hash:
                raise IntegrityError(f"outcome divergente para {o.event_id}")
            return {"estado": "idempotente"}
        self.cx.execute(
            "INSERT INTO le_outcome VALUES (?,?,?,?,?,?,?,?,?)",
            (o.event_id, o.entry_session, o.exit_session, o.entry_price, o.exit_price,
             o.return_decimal, o.label_available_at, o.data_hash, o.resolved_at))
        self.cx.commit()
        return {"estado": "resuelto", "y": o.y}

    def registrar_fallo(self, fallo: RunFailure) -> None:
        self.cx.execute(
            "INSERT INTO le_failure (event_id, model_id, reason, timestamp) VALUES (?,?,?,?)",
            (fallo.event_id, fallo.model_id, fallo.reason, fallo.timestamp))
        self.cx.commit()

    # --------------------------------------------------------------- lectura
    def registros_evaluables(self, experiment_id: str) -> list[dict]:
        """Une pronósticos con su outcome (si maduró) para el evaluador. Cada fila:
        {model_id, p_up, abstained, y|None, session_id, emision, entry/exit, r}."""
        q = """
        SELECT fo.model_id, fo.p_up, fo.abstained, fo.event_id, fo.cutoff_at,
               ev.entry_session, ev.exit_session,
               oc.return_decimal AS r, oc.label_available_at
        FROM le_forecast fo
        JOIN le_event ev ON ev.event_id = fo.event_id
        LEFT JOIN le_outcome oc ON oc.event_id = fo.event_id
        WHERE fo.experiment_id = ?"""
        out = []
        for row in self.cx.execute(q, (experiment_id,)).fetchall():
            emision = row["event_id"].split(":")[1] if ":" in row["event_id"] else row["event_id"]
            out.append({
                "model_id": row["model_id"], "p_up": row["p_up"],
                "abstained": bool(row["abstained"]), "event_id": row["event_id"],
                "session_id": emision, "emision": emision,
                "entry_session": row["entry_session"], "exit_session": row["exit_session"],
                "y": (1 if row["r"] is not None and row["r"] > 0 else
                      (0 if row["r"] is not None else None)),
                "r": row["r"],
            })
        return out

    def verificar_cadena(self) -> bool:
        """Recorre la hash-chain de pronósticos y verifica su integridad."""
        prev = ""
        for row in self.cx.execute(
                "SELECT row_hash, prev_hash, chain_hash FROM le_forecast "
                "ORDER BY created_at, forecast_id").fetchall():
            if row["prev_hash"] != prev:
                return False
            if hash_canonico({"prev": prev, "row": row["row_hash"]}) != row["chain_hash"]:
                return False
            prev = row["chain_hash"]
        return True

    def exportar(self) -> dict:
        """Export hash-chain + manifiesto de filas para destino de solo escritura."""
        fos = [dict(r) for r in self.cx.execute(
            "SELECT * FROM le_forecast ORDER BY created_at, forecast_id").fetchall()]
        ocs = [dict(r) for r in self.cx.execute("SELECT * FROM le_outcome").fetchall()]
        return {"forecasts": fos, "outcomes": ocs,
                "cadena_ok": self.verificar_cadena(),
                "export_hash": hash_canonico({"f": [x["chain_hash"] for x in fos]})}


class IntegrityError(RuntimeError):
    pass


def _ahora() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()
