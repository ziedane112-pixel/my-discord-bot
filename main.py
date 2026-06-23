import os
import discord
from discord.ext import commands, tasks

# الإعدادات
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

@bot.event
async def on_ready():
    # تحميل ملف الرول بلاي تلقائياً
    await bot.load_extension("roleplay")
    print(f"✅ البوت متصل: {bot.user.name}")
    rotate_status.start()

# نظام الحالة
status_index = 0
@tasks.loop(seconds=10)
async def rotate_status():
    global status_index
    if status_index == 0:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="-help"))
    else:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Dev: @hc6f"))
    status_index = (status_index + 1) % 2

if __name__ == "__main__":
    bot.run(os.environ.get("DISCORD_TOKEN"))
