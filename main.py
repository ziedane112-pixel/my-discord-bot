# -*- coding: utf-8 -*-
import os
# بدل قراءة ملف، سيقرأ التوكن من إعدادات الموقع
TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)
import json
import logging
import discord
from discord.ext import commands

# إعدادات لضمان عدم حدوث تداخل مع بيئة الاستضافة
os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

logging.basicConfig(level=logging.INFO)

# تفعيل جميع الـ Intents لضمان عمل الأوامر بكفاءة
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

ADMIN_ROLE_IDS = {1515005601347010600}
OWNER_ID = 1310615228786147412

# تحميل البيانات من ملف الـ JSON
rp_data = {"chars": {}, "items": {}}
if os.path.exists("rp_data.json"):
    try:
        with open("rp_data.json", "r", encoding="utf-8") as f:
            rp_data = json.load(f)
    except Exception as e:
        print(f"⚠️ خطأ في قراءة ملف البيانات: {e}")

# نظام التحقق من الإدارة
def is_admin():
    async def predicate(ctx):
        if ctx.author.id == OWNER_ID or any(r.id in ADMIN_ROLE_IDS for r in ctx.author.roles):
            return True
        raise commands.CheckFailure("❌ ليس لديك رتبة الإدارة.")
    return commands.check(predicate)

@bot.event
async def on_ready():
    # هنا يجب أن يكون هناك 4 مسافات قبل الـ print
    print(f"✅ تم تشغيل البوت بنجاح: {bot.user.name}")
    
@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(title="📋 قائمة الأوامر المتاحة", color=0x5865F2)
    embed.add_field(name="🎭 نظام الرول بلاي", value="`-بطاقة` — عرض بطاقتك\n`-اعطاء_ذهب` — إضافة ذهب لعضو", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="بطاقة")
async def char_card(ctx, member: discord.Member = None):
    target = member or ctx.author
    c = rp_data.get("chars", {}).get(str(target.id))
    if not c: return await ctx.send("⚠️ الشخصية غير مسجلة!")
    inv_list = c.get("inv", [])
    inv_text = " • ".join(inv_list) if inv_list else "الحقيبة فارغة 🎒"
    embed = discord.Embed(title=f"🎭 الهوية: {c.get('name', 'بدون اسم')}", color=0x00FF99)
    embed.add_field(name="💰 الذهب", value=f"{c.get('gold', 0)}", inline=True)
    embed.add_field(name="🎒 الحقيبة", value=f"```\n{inv_text}\n```", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="اعطاء_ذهب")
@is_admin()
async def give_gold(ctx, member: discord.Member = None, amount: int = None):
    global rp_data
    if not member or amount is None: return await ctx.send("❌ | الاستخدام: `-اعطاء_ذهب @العضو المبلغ`")
    if amount <= 0: return await ctx.send("❌ | يجب أن يكون المبلغ أكبر من صفر!")
    if "chars" not in rp_data: rp_data["chars"] = {}
    if str(member.id) not in rp_data["chars"]: return await ctx.send("❌ | العضو غير مسجل!")
    rp_data["chars"][str(member.id)]["gold"] = rp_data["chars"][str(member.id)].get("gold", 0) + amount
    with open("rp_data.json", "w", encoding="utf-8") as f:
        json.dump(rp_data, f, ensure_ascii=False, indent=4)
    await ctx.send(f"✅ | تم إعطاء **{amount}** ذهب لـ {member.mention}!")

    TOKEN = os.environ.get("DISCORD_TOKEN")

    if TOKEN:
        print("✅ التوكن تم العثور عليه، جاري تشغيل البوت...")
    else:
        print("❌ خطأ: لم يتم العثور على التوكن في إعدادات البيئة!")
        return # يوقف التشغيل إذا لم يوجد توكن

    bot.run(TOKEN) # هذا السطر يجب أن يكون في الخارج (مستوى الصفر)
