# -*- coding: utf-8 -*-
import os
import json
import logging
import discord
import roleplay
from discord.ext import commands
from discord.ext import commands, tasks

# إعدادات البيئة
os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
logging.basicConfig(level=logging.INFO)

# تعريف البوت (هنا يتم تعريف المتغير bot)
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

ADMIN_ROLE_IDS = {1515005601347010600}
OWNER_ID = 1310615228786147412

# تحميل البيانات
rp_data = {"chars": {}, "items": {}}
if os.path.exists("rp_data.json"):
    try:
        with open("rp_data.json", "r", encoding="utf-8") as f:
            rp_data = json.load(f)
    except Exception as e:
        print(f"⚠️ خطأ في قراءة ملف البيانات: {e}")

def is_admin():
    async def predicate(ctx):
        if ctx.author.id == OWNER_ID or any(r.id in ADMIN_ROLE_IDS for r in ctx.author.roles):
            return True
        raise commands.CheckFailure("❌ ليس لديك رتبة الإدارة.")
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f"✅ تم تشغيل البوت بنجاح: {bot.user.name}")

status_index = 0

@tasks.loop(seconds=10)
async def rotate_status():
    global status_index

    if status_index == 0:
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="!help"
            )
        )
    else:
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="Dev: @hc6f"
            )
        )

    status_index = (status_index + 1) % 2

# --- تشغيل البوت يكون دائماً في نهاية الملف ---
if __name__ == "__main__":
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ خطأ: لم يتم العثور على التوكن في إعدادات البيئة!")
