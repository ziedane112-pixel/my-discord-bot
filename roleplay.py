import json
import os
import random
import discord
from discord.ext import commands

class Roleplay(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.RP_DB_FILE = "rp_data.json"
        self.rp_data = self.load_rp()

    def load_rp(self) -> dict:
        if os.path.exists(self.RP_DB_FILE) and os.path.getsize(self.RP_DB_FILE) > 0:
            try:
                with open(self.RP_DB_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "chars" not in data: data["chars"] = {}
                    if "shops" not in data or not data["shops"]:
                        data["shops"] = {
                            "🍎 تفاحة": {"price": 10, "desc": "ترجع 20 من الصحة ❤️"},
                            "🧪 جرعة طاقة": {"price": 30, "desc": "ترجع الصحة كاملة 100% ✨"},
                            "⚔️ سيف حديدي": {"price": 150, "desc": "سيف حاد يزيد الهجوم بمقدار +15"},
                            "🛡️ درع برونزي": {"price": 200, "desc": "درع يحميك ويقلل الضرر المتلقى"}
                        }
                    return data
            except json.JSONDecodeError:
                pass
        default_data = {
            "chars": {},
            "items": {},
            "quests": {},
            "shops": {
                "🍎 تفاحة": {"price": 10, "desc": "ترجع 20 من الصحة ❤️"},
                "🧪 جرعة طاقة": {"price": 30, "desc": "ترجع الصحة كاملة 100% ✨"},
                "⚔️ سيف حديدي": {"price": 150, "desc": "سيف حاد يزيد الهجوم بمقدار +15"},
                "🛡️ درع برونزي": {"price": 200, "desc": "درع يحميك ويقلل الضرر المتلقى"}
            },
        }
        with open(self.RP_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data

    @commands.command(name="help")
    async def help(self, ctx):
        embed = discord.Embed(
            title="🛡️ | مركز المساعدة - كوفا سيتي",
            description="أهلاً بك يا مواطن، إليك قائمة الأوامر المتاحة لخدمتك في المدينة:",
            color=discord.Color.gold()
        )
        embed.add_field(name="💼 | الأوامر العامة", value="`-id` لعرض بطاقتك الشخصية\n`-job` لمعرفة وظيفتك الحالية", inline=False)
        embed.add_field(name="🚔 | أوامر الشرطة", value="`-arrest` للقبض على المطلوبين\n`-ticket` لتحرير مخالفة مرورية", inline=False)
        embed.add_field(name="🏦 | أوامر البنك", value="`-balance` لمعرفة رصيدك\n`-transfer` لتحويل الأموال", inline=False)
        embed.set_footer(text="Cova City RP | نظام المدينة الرسمي")
        embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.send(embed=embed)

    @commands.command(name="انشاء_رتب")
    @commands.has_permissions(administrator=True)
    async def create_roles(self, ctx):
        guild = ctx.guild
        roles_to_create = {
            "👑 | Owner": discord.Color.gold(),
            "💎 | Co-Owner": discord.Color.blue(),
            "🛡️ | Admin": discord.Color.red(),
            "👮 | Moderator": discord.Color.green()
        }
        await ctx.send("⚙️ | جاري تأسيس هيكلة السيرفر... يرجى الانتظار.")
        for role_name, color in roles_to_create.items():
            existing_role = discord.utils.get(guild.roles, name=role_name)
            if not existing_role:
                await guild.create_role(name=role_name, color=color, reason="تأسيس تلقائي لرتب السيرفر")
                await ctx.send(f"✅ | تم إنشاء رتبة: **{role_name}**")
            else:
                await ctx.send(f"⚠️ | الرتبة **{role_name}** موجودة بالفعل.")
        await ctx.send("🚀 | اكتملت عملية التأسيس بنجاح، السيرفر جاهز!")

async def setup(bot):
    await bot.add_cog(Roleplay(bot))

    
    @commands.command(name="انشاء")
    async def create_char(self, ctx):
        """إنشاء شخصية RP جديدة"""
        if "chars" in self.rp_data and str(ctx.author.id) in self.rp_data["chars"]:
            await ctx.send("⚠️ عندك شخصية بالفعل! استخدم أمر `!بطاقة` لعرضها.")
            return
            
        view = CreateCharView(self)
        embed = discord.Embed(
            title="🎭 إنشاء شخصيتك الأسطورية",
            description="مرحباً بك في عالم الرول بلاي! 🌟\nاضغط على الزر بالأسفل لتعبئة بيانات شخصيتك وبدء المغامرة.",
            color=0x00FF99,
        )
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
            
        await ctx.send(embed=embed, view=view)

    @commands.command(name="بطاقة")
    async def char_card(self, ctx, member: discord.Member = None):
        """عرض بطاقة الشخصية"""
        target = member or ctx.author
        if "chars" not in self.rp_data:
            self.rp_data["chars"] = {}
            
        c = self.rp_data["chars"].get(str(target.id))
        if not c:
            msg = "ما عندك شخصية حتى الآن! استخدم أمر `!انشاء` لبناء شخصيتك 🎭" if target == ctx.author else f"العضو {target.mention} ليس لديه شخصية مسجلة حالياً."
            await ctx.send(f"⚠️ {msg}")
            return
            
        inv_text = " • ".join(c.get("inv", [])) or "الحقيبة فارغة تماماً 🎒"
        
        embed = discord.Embed(
            title=f"🎭 الهوية الرسمية: {c['name']}", 
            description=f"**الوصف الشخصي:**\n{c['desc']}", 
            color=0x00FF99
        )
        if target.display_avatar:
            embed.set_thumbnail(url=target.display_avatar.url)
        
        embed.add_field(name="⭐ المستوى", value=f"**{c.get('level', 1)}**", inline=True)
        embed.add_field(name="❤️ الصحة", value=f"**{c.get('hp', 100)}%**", inline=True)
        embed.add_field(name="💰 الذهب الحالي", value=f"**{c.get('gold', 0)}** 💰", inline=True)
        embed.add_field(name="🎒 ممتلكات الحقيبة", value=f"```{inv_text}```", inline=False)
        embed.set_footer(text=f"بطاقة العضو: {target.display_name} 💳")
        await ctx.send(embed=embed)

    @commands.command(name="لف")
    async def roll_dice(self, ctx, dice: str = "1d20"):
        """رمي نرد الحظ"""
        try:
            n, sides = dice.lower().split("d")
            n, sides = int(n), int(sides)
            if n < 1 or n > 20 or sides < 2 or sides > 100:
                raise ValueError
                
            results = [random.randint(1, sides) for _ in range(n)]
            total = sum(results)
            detail = " + ".join(str(r) for r in results) if n > 1 else str(total)
            
            embed = discord.Embed(title="🎲 رمية نرد الحظ", color=0xFFD700)
            embed.add_field(name="📊 نوع النرد", value=f"`{dice}`", inline=True)
            embed.add_field(name="🎯 النتيجة الإجمالية", value=f"**{total}**", inline=True)
            if n > 1:
                embed.add_field(name="📝 تفاصيل الرميات", value=f"({detail})", inline=False)
            embed.set_footer(text=f"بواسطة اللاعب: {ctx.author.display_name}")
            await ctx.send(embed=embed)
        except Exception:
            await ctx.send("❌ | الصيغة خاطئة! الاستخدام الصحيح: `!لف 1d20`")
        
    @commands.command(name="سوق")
    async def shop(self, ctx):
        """عرض السوق والسلع المتاحة"""
        items = self.rp_data.get("shops", {})
        embed = discord.Embed(
            title="🛒 سوق المدينة الفخم", 
            description="مرحباً بك في السوق! استخدم أمر `!شراء اسم السلعة` لامتلاكها 🛍",
            color=0xFFD700
        )
        if ctx.guild.icon:
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)

        for name, item in items.items():
            embed.add_field(
                name=f"🔹 {name}",
                value=f"**السعر:** {item['price']} 💰\n**الميزة:** {item['desc']}",
                inline=False,
            )
        await ctx.send(embed=embed)

    @commands.command(name="شراء")
    async def buy_item(self, ctx, *, item_name: str):
        """شراء سلعة من سوق المدينة"""
        uid = str(ctx.author.id)
        if "chars" not in self.rp_data or uid not in self.rp_data["chars"]:
            await ctx.send("⚠️ ما عندك شخصية حتى الآن! استخدم أمر `!انشاء` أولاً.")
            return
            
        user_char = self.rp_data["chars"][uid]
        items = self.rp_data.get("shops", {})
        
        target_item = None
        actual_item_name = ""
        for name, data in items.items():
            if item_name.strip() in name or name in item_name:
                target_item = data
                actual_item_name = name
                break
                
        if not target_item:
            await ctx.send("❌ | هذه السلعة غير موجودة في السوق! تأكد من الاسم عبر أمر `!سوق`.")
            return
            
        cost = target_item["price"]
        current_gold = user_char.get("gold", 0)
        if current_gold < cost:
            await ctx.send(f"❌ | ما عندك ذهب كافٍ! السعر: `{cost}` 💰، والذهب اللي معك: `{current_gold}` 💰.")
            return
            
        user_char["gold"] = current_gold - cost
        if "inv" not in user_char:
            user_char["inv"] = []
            
        user_char["inv"].append(actual_item_name)
        self.save_rp()
        await ctx.send(f"🛍️ | تم شراء **{actual_item_name}** بنجاح! تفقد حقيبتك عبر أمر `!بطاقة`.")

    @commands.command(name="بلاغ")
    async def report_command(self, ctx, *, report_text: str):
        """إرسال بلاغ رسمي إلى غرفة الاتصال الرقابي"""
        uid = str(ctx.author.id)
        if "chars" not in self.rp_data or uid not in self.rp_data["chars"]:
            await ctx.send("⚠️ يجب أن تملك شخصية أولاً لإرسال البلاغات!")
            return
            
        user_char = self.rp_data["chars"][uid]
        CENSORSHIP_CHANNEL_ID = 123456789012345678  # <--- استبدل هذا المعرف بالمعرف الحقيقي لقناتك ديسكورد
        
        channel = self.bot.get_channel(CENSORSHIP_CHANNEL_ID)
        if not channel:
            await ctx.send("❌ | خطأ: لم يتم العثور على غرفة الاتصال الرقابي.")
            return
            
        embed = discord.Embed(
            title="🚨 اتصال رقابي وارد | New Censorship Call",
            description=f"**تفاصيل البلاغ والمخالفة:**\n```{report_text}```",
            color=0xFF0000
        )
        embed.add_field(name="👤 مقدم البلاغ", value=f"**{user_char['name']}**", inline=True)
        embed.add_field(name="🆔 الحساب الرقمي", value=ctx.author.mention, inline=True)
        
        await channel.send(content="@everyone 🚨 **إشعار رقابي عاجل!**", embed=embed)
        try:
            await ctx.message.delete()
        except Exception:
            pass
        await ctx.send(f"✅ {ctx.author.mention} تم إرسال بلاغك السري بنجاح.")

    @commands.command(name="تحويل")
    async def transfer_gold(self, ctx, member: discord.Member, amount: int):
        """تحويل الذهب لعضو آخر"""
        uid = str(ctx.author.id)
        target_id = str(member.id)
        if uid == target_id:
            await ctx.send("❌ | لا يمكنك التحويل لنفسك!")
            return
        if amount <= 0:
            await ctx.send("❌ | يرجى كتابة مبلغ تحويل صحيح.")
            return
        if "chars" not in self.rp_data or uid not in self.rp_data["chars"]:
            await ctx.send("⚠️ ما عندك شخصية! استخدم أمر `!انشاء` أولاً.")
            return
        if target_id not in self.rp_data["chars"]:
            await ctx.send(f"❌ | العضو {member.mention} ليس لديه شخصية مسجلة.")
            return
            
        sender = self.rp_data["chars"][uid]
        receiver = self.rp_data["chars"][target_id]
        if sender.get("gold", 0) < amount:
            await ctx.send(f"❌ | رصيدك لا يكفي! الذهب الحالي لديك: `{sender.get('gold', 0)}`.")
            return
            
        sender["gold"] -= amount
        receiver["gold"] = receiver.get("gold", 0) + amount
        self.save_rp()
        
        embed = discord.Embed(title="💸 حوافظ ومعاملات مالية مصدقة", color=0xFFD700)
        embed.add_field(name="📤 من حساب", value=f"**{sender['name']}**", inline=True)
        embed.add_field(name="📥 إلى حساب", value=f"**{receiver['name']}**", inline=True)
        embed.add_field(name="💰 المبلغ المحول", value=f"`{amount}` ذهبة", inline=False)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 86400, commands.BucketType.user)
    @commands.command(name="راتب")
    async def daily_salary(self, ctx):
        """صرف الراتب الدوري للمواطنين"""
        uid = str(ctx.author.id)
        if "chars" not in self.rp_data or uid not in self.rp_data["chars"]:
            await ctx.send("⚠️ ما عندك شخصية لاستلام الراتب!")
            ctx.command.reset_cooldown(ctx)
            return
            
        salary = random.randint(50, 150)
        self.rp_data["chars"][uid]["gold"] = self.rp_data["chars"][uid].get("gold", 0) + salary
        self.save_rp()
        await ctx.send(f"💰 | {ctx.author.mention} استلمت راتبك الدوري بمقدار **{salary}** ذهبة!")

    @daily_salary.error
    async def daily_salary_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            hours = int(error.retry_after // 3600)
            minutes = int((error.retry_after % 3600) // 60)
            await ctx.send(f"⏳ | يرجى العودة بعد: `{hours} ساعة و {minutes} دقيقة`.")

    @commands.command(name="علاج")
    async def heal_command(self, ctx):
        """استهلاك المأكولات أو الجرعات لزيادة الصحة"""
        uid = str(ctx.author.id)
        if "chars" not in self.rp_data or uid not in self.rp_data["chars"]:
            await ctx.send("⚠️ ما عندك شخصية لتطبيق العلاج عليها!")
            return
            
        user_char = self.rp_data["chars"][uid]
        inv = user_char.get("inv", [])
        current_hp = user_char.get("hp", 100)
        if current_hp >= 100:
            await ctx.send("❤️ | صحتك كاملة بالفعل 100%.")
            return
            
        if "🧪 جرعة طاقة" in inv:
            inv.remove("🧪 جرعة طاقة")
            user_char["hp"] = 100
            msg = "🧪 | استخدمت **جرعة طاقة**! تم استعادة صحتك كاملة **100%** ✨"
        elif "🍎 تفاحة" in inv:
            inv.remove("🍎 تفاحة")
            user_char["hp"] = min(100, current_hp + 20)
            msg = f"🍎 | أكلت **تفاحة**! صحتك الحالية: **{user_char['hp']}%** ❤️"
        else:
            await ctx.send("🎒 | حقيبتك فارغة من المستلزمات الطبية! توجه إلى الـ `!سوق`.")
            return
            
        self.save_rp()
        await ctx.send(f"{ctx.author.mention} {msg}")

    @commands.command(name="فحص")
    async def check_bot(self, ctx):
        """فحص حالة البوت وسرعة الاستجابة"""
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(title="🟢 فحص حالة النظام", description=f"📡 سرعة الاستجابة: `{latency}ms`", color=0x00FF99)
        await ctx.send(embed=embed)

    @commands.command(name="حذف_شخصية")
    @commands.has_permissions(administrator=True)
    async def delete_char(self, ctx, member: discord.Member):
        """حذف شخصية عضو (للإدارة فقط)"""
        uid = str(member.id)
        if "chars" not in self.rp_data or uid not in self.rp_data["chars"]:
            await ctx.send(f"❌ {member.mention} ما عنده شخصية.")
            return
        del self.rp_data["chars"][uid]
        self.save_rp()
        await ctx.send(f"🗑️ تم حذف شخصية {member.mention}.")

    @commands.cooldown(1, 1800, commands.BucketType.user)
    @commands.command(name="عمل")
    async def work_command(self, ctx):
        """تأدية وظيفة في المدينة لتجميع الذهب"""
        uid = str(ctx.author.id)
        if "chars" not in self.rp_data or uid not in self.rp_data["chars"]:
            await ctx.send("⚠️ ما عندك شخصية لتشتغل بها! أنشئ شخصيتك أولاً عبر أمر `!انشاء`.")
            ctx.command.reset_cooldown(ctx)
            return

        user_char = self.rp_data["chars"][uid]
        jobs = [
            {"title": "حارس شخصي في ديوان الرقابة 🥷", "pay": random.randint(40, 90), "desc": "قمت بتأمين الموكب الرسمي وحصلت على مكافأة مالية."},
            {"title": "مستشار استثماري في البنك المركزي 🏦", "pay": random.randint(50, 110), "desc": "أشرفت على صفقة تجارية ضخمة لإنعاش خزينة المدينة."},
            {"title": "خبير تقني وأنظمة برمجية 💻", "pay": random.randint(45, 95), "desc": "قمت بتحديث الجدار الأمني الفرعي للشبكة وحميتها من الاختراق."},
            {"title": "مستثمر عقاري في الأحياء الفخمة 🏙️", "pay": random.randint(60, 120), "desc": "بعت قطعة أرض استراتيجية لأحد التجار وحققت عمولة ممتازة."},
            {"title": "مهرّب سري في السوق السوداء 🤫", "pay": random.randint(70, 140), "desc": "نجحت في تمرير شحنة جرعات طاقة نادرة وحصلت على ذهب وفير."}
        ]
        
        job = random.choice(jobs)
        pay_amount = job["pay"]
        user_char["gold"] = user_char.get("gold", 0) + pay_amount
        self.save_rp()
        
        embed = discord.Embed(
            title="💼 | سِجِلُّ المِهَنِ وَالتَّكْلِيفَاتِ الرَّسْمِيَّة",
            description=f"**الوظيفة الحالية:** `{job['title']}`\n\n📝 **تقرير العمل:**\n*{job['desc']}*",
            color=0x00FF99
        )
        embed.add_field(name="💰 الذهب المكتسب", value=f"**+{pay_amount}** ذهبة", inline=True)
        embed.add_field(name="💳 الرصيد الإجمالي", value=f"`{user_char['gold']}` 💰", inline=True)
        await ctx.send(embed=embed)

    @work_command.error
    async def work_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            minutes = int(error.retry_after // 60)
            seconds = int(error.retry_after % 60)
            await ctx.send(f"⏳ | خذ قسطاً من الراحة وعد بعد: `{minutes} دقيقة و {seconds} ثانية`.")

    @commands.command(name="موكب")
    @commands.has_permissions(administrator=True)
    async def royal_convoy(self, ctx, *, details: str = "تحرك الموكب الرسمي الفخم في شوارع المدينة."):
        """أمر الهيبة: إعلان تحرك الموكب الرسمي أو حالة الاستنفار"""
        try:
            await ctx.message.delete()
        except Exception:
            pass

        embed = discord.Embed(
            title="🔱 | دِيوَانُ الرِّقَابَةِ وَالعَمَلِيَّاتِ المَلَكِيَّة",
            description=f"🚨 **إِعْلَانٌ رَسْمِيٌّ صَادِرٌ عَنِ القِيَادَةِ العُلْيَا:**\n\n```⚠️ {details}```\n\nيرجى من كافة المواطنين إخلاء الطرق الرئيسية فوراً والالتزام بالتعليمات.",
            color=0xD4AF37
        )
        embed.set_footer(text=f"صُدرت الأوامر بواسطة السيّد: {ctx.author.display_name} 👑")
        await ctx.send(content="@everyone 🔱 **تَنْبِيهٌ مَلَكِيٌّ صَارِم!**", embed=embed)

    @commands.command(name="خزينة")
    async def state_treasury(self, ctx):
        """عرض الحالة المالية العامة لخزينة المدينة"""
        total_gold = sum(char.get("gold", 0) for char in self.rp_data.get("chars", {}).values())
        total_chars = len(self.rp_data.get("chars", {}))
        
        embed = discord.Embed(
            title="🏦 | STATE TREASURY - خزينة الدولة",
            description="التقرير المالي الدوري المعتمد للمدينة والبنك المركزي 📊",
            color=0xD4AF37
        )
        embed.add_field(name="💰 الاحتياطي الإجمالي للمدينة", value=f"**{total_gold:,}** ذهبة", inline=False)
        embed.add_field(name="👥 عدد الحسابات النشطة", value=f"**{total_chars}** شخصية مسجلة", inline=True)
        embed.add_field(name="🏛️ التصنيف الاقتصادي", value="`مستقر وممتاز (AAA)` 📈", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="مداهمة")
    @commands.has_permissions(administrator=True)
    async def raid_member(self, ctx, member: discord.Member):
        """مداهمة مقرات الخارجين عن القانون ومصادرة جزء من أموالهم وحقيبتهم"""
        target_id = str(member.id)
        if "chars" not in self.rp_data or target_id not in self.rp_data["chars"]:
            await ctx.send(f"❌ | {member.mention} ما عنده شخصية أصلاً لتتم مداهمته!")
            return

        target_char = self.rp_data["chars"][target_id]
        gold_lost = int(target_char.get("gold", 0) * 0.3)
        target_char["gold"] -= gold_lost
        
        confiscated_item = "لا يوجد"
        if target_char.get("inv"):
            confiscated_item = target_char["inv"].pop()

        self.save_rp()
        try:
            await ctx.message.delete()
        except Exception:
            pass

        embed = discord.Embed(
            title="🚔 | دِيوَانُ الرِّقَابَةِ - أَمْرُ دَاهِمَةٍ عَمَلِيَّاتِيَّة",
            description=f"🚨 **تَمَّتْ مُدَاهَمَةُ مَقَرِّ المَطْلُوبِ:** {member.mention}\n\nتم اقتحام الموقع وتفتيش السجل والحقيبة وتطبيق العقوبات النقدية.",
            color=0xFF0000
        )
        embed.add_field(name="💰 الذهب المصادر", value=f"`-{gold_lost}` ذهبة", inline=True)
        embed.add_field(name="📦 الممتلكات المحجوزة", value=f"`{confiscated_item}`", inline=True)
        await ctx.send(content=f"{member.mention} 🚨 **لقد تم رصدك واقتحام موقعك!**", embed=embed)

    @commands.command(name="ثروة")
    async def wealth_leaderboard(self, ctx):
        """عرض قائمة أغنى 5 مواطنين في المدينة"""
        chars = self.rp_data.get("chars", {})
        if not chars:
            await ctx.send("⚠️ المدينة فارغة حالياً، لا يوجد مواطنون مسجلون!")
            return

        sorted_chars = sorted(chars.items(), key=lambda x: x[1].get("gold", 0), reverse=True)[:5]
        embed = discord.Embed(title="👑 | سِجِلُّ شَرَفِ صَفْوَةِ الأَثْرِيَاءِ", description="قائمة توب 5 لأكثر الشخصيات نفوذاً وثروة في المدينة 🏆\n" + "─" * 35, color=0xD4AF37)

        medals = ["🥇", "🥈", "🥉", "🏅", "🏅"]
        for i, (uid, data) in enumerate(sorted_chars):
            embed.add_field(
                name=f"{medals[i]} المركز {i+1}: {data['name']}",
                value=f"**الرصيد المالي:** `{data.get('gold', 0):,}` ذهبة 💰",
                inline=False
            )
        await ctx.send(embed=embed)


class CreateCharModal(discord.ui.Modal, title="إنشاء شخصية"):
    char_name = discord.ui.TextInput(label="اسم الشخصية", min_length=2, max_length=50)
    char_desc = discord.ui.TextInput(label="وصف الشخصية", style=discord.TextStyle.paragraph, min_length=10, max_length=300)

    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        if "chars" not in self.cog.rp_data:
            self.cog.rp_data["chars"] = {}
            
        if uid in self.cog.rp_data["chars"]:
            await interaction.response.send_message("⚠️ عندك شخصية بالفعل!", ephemeral=True)
            return
        name = self.char_name.value.strip()
        desc = self.char_desc.value.strip()
        self.cog.rp_data["chars"][uid] = {
            "name": name,
            "desc": desc,
            "level": 1,
            "hp": 100,
            "gold": 500,
            "inv": []
        }
        self.cog.save_rp()
        embed = discord.Embed(title="🎭 تم إنشاء الشخصية بنجاح!", color=0x00FF99)
        embed.add_field(name="الاسم", value=name, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class CreateCharView(discord.ui.View):

    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="إنشاء شخصية", style=discord.ButtonStyle.green, emoji="🎭")
    async def create_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CreateCharModal(self.cog))


async def setup(bot):
    await bot.add_cog(Roleplay(bot))
