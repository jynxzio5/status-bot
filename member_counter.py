import discord
from discord.ext import commands
from discord import app_commands
import os
import json

# Load configuration
def load_config():
    try:
        with open('config2.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            'DISCORD_TOKEN': os.getenv('DISCORD_TOKEN'),
            'CHANNEL_NAME': os.getenv('CHANNEL_NAME', 'Members: {count}'),
            'COUNTER_CHANNELS': {}  # تخزين معرفات القنوات
        }

def save_config():
    try:
        with open('config2.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {str(e)}")

config = load_config()
if 'COUNTER_CHANNELS' not in config:
    config['COUNTER_CHANNELS'] = {}
    save_config()

# Bot setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class MemberCounterBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='/', intents=intents)
        
    async def setup_hook(self):
        await self.tree.sync()

bot = MemberCounterBot()

@bot.event
async def on_ready():
    print(f'Bot is ready! Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="Use /setup to create counter"
    ))

@bot.event
async def on_member_join(member):
    """تحديث العداد عند انضمام عضو جديد"""
    if member and member.guild:
        await update_member_count(member.guild)

@bot.event
async def on_member_remove(member):
    """تحديث العداد عند مغادرة عضو"""
    if member and member.guild:
        await update_member_count(member.guild)

async def update_member_count(guild, channel=None):
    """تحديث عدد الأعضاء في اسم القناة"""
    if not guild:
        return

    try:
        # البحث عن القناة الموجودة
        if not channel:
            # البحث عن معرف القناة المخزن
            channel_id = config['COUNTER_CHANNELS'].get(str(guild.id))
            if channel_id:
                channel = guild.get_channel(int(channel_id))
                if not channel:
                    # إذا لم يتم العثور على القناة، نزيل معرفها من التخزين
                    del config['COUNTER_CHANNELS'][str(guild.id)]
                    save_config()
                    return
        
        # تحديث القناة فقط إذا كانت موجودة
        if channel and isinstance(channel, discord.VoiceChannel):
            try:
                new_name = config['CHANNEL_NAME'].format(count=guild.member_count)
                if channel.name != new_name:
                    await channel.edit(name=new_name)
            except discord.Forbidden:
                print(f"لا يمكن تعديل اسم القناة في {guild.name}")
            except Exception as e:
                print(f"خطأ في تحديث اسم القناة: {str(e)}")
    except Exception as e:
        print(f"خطأ في تحديث عدد الأعضاء: {str(e)}")

@bot.tree.command(name="setup", description="Setup the member counter channel")
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    try:
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("This command can only be used in a server!")
            return

        # البحث عن قناة موجودة باستخدام المعرف المخزن
        existing_channel = None
        channel_id = config['COUNTER_CHANNELS'].get(str(guild.id))
        if channel_id:
            existing_channel = guild.get_channel(int(channel_id))

        if existing_channel:
            # تحديث القناة الموجودة
            await update_member_count(guild, existing_channel)
            await interaction.response.send_message(f"Updated existing counter channel: {existing_channel.mention}")
            return

        # إنشاء أذونات القناة
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=True,  # يمكن رؤية القناة
                connect=False,      # لا يمكن الانضمام
                speak=False,        # لا يمكن التحدث
                stream=False,       # لا يمكن بث الفيديو
                send_messages=False # لا يمكن إرسال رسائل
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                manage_channels=True,
                connect=True
            )
        }

        # إنشاء القناة الصوتية
        channel = await guild.create_voice_channel(
            name=config['CHANNEL_NAME'].format(count=guild.member_count),
            overwrites=overwrites,
            reason="Member counter channel"
        )
        
        if channel:
            # تخزين معرف القناة
            config['COUNTER_CHANNELS'][str(guild.id)] = channel.id
            save_config()
            await interaction.response.send_message(f"Counter channel has been created! {channel.mention}")
        else:
            await interaction.response.send_message("Failed to create counter channel.")
        
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to create channels!")
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}")

# تشغيل البوت
if __name__ == "__main__":
    token = config.get('DISCORD_TOKEN')
    if not token:
        print("Error: No Discord token found in config2.json")
        exit(1)
    bot.run(token)
