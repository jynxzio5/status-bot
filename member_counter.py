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
            'CHANNEL_NAME': os.getenv('CHANNEL_NAME', 'Members: {count}')
        }

config = load_config()

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
    await update_member_count(member.guild)

@bot.event
async def on_member_remove(member):
    """تحديث العداد عند مغادرة عضو"""
    await update_member_count(member.guild)

async def update_member_count(guild, channel=None):
    """تحديث عدد الأعضاء في اسم القناة"""
    # البحث عن القناة الموجودة
    if not channel:
        for ch in guild.channels:
            if ch.name.startswith(config['CHANNEL_NAME'].format(count='').strip()):
                channel = ch
                break
    
    # تحديث القناة فقط إذا كانت موجودة
    if channel:
        try:
            new_name = config['CHANNEL_NAME'].format(count=guild.member_count)
            if channel.name != new_name:
                await channel.edit(name=new_name)
        except discord.Forbidden:
            print(f"لا يمكن تعديل اسم القناة في {guild.name}")
        except Exception as e:
            print(f"خطأ في تحديث اسم القناة: {str(e)}")

@bot.tree.command(name="setup", description="Setup the member counter channel")
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    try:
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("This command can only be used in a server!")
            return

        # البحث عن قناة موجودة
        existing_channel = None
        for channel in guild.channels:
            if channel.name.startswith(config['CHANNEL_NAME'].format(count='').strip()):
                existing_channel = channel
                break

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
        
        await interaction.response.send_message(f"Counter channel has been created! {channel.mention}")
        
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
