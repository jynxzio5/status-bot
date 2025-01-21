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
        try:
            channel_id = config['COUNTER_CHANNELS'].get(str(member.guild.id))
            if channel_id:
                channel = member.guild.get_channel(int(channel_id))
                if channel:
                    new_name = config['CHANNEL_NAME'].format(count=member.guild.member_count)
                    await channel.edit(name=new_name)
        except Exception as e:
            print(f"Error updating counter on member join: {str(e)}")

@bot.event
async def on_member_remove(member):
    """تحديث العداد عند مغادرة عضو"""
    if member and member.guild:
        try:
            channel_id = config['COUNTER_CHANNELS'].get(str(member.guild.id))
            if channel_id:
                channel = member.guild.get_channel(int(channel_id))
                if channel:
                    new_name = config['CHANNEL_NAME'].format(count=member.guild.member_count)
                    await channel.edit(name=new_name)
        except Exception as e:
            print(f"Error updating counter on member remove: {str(e)}")

@bot.tree.command(name="setup", description="Setup the member counter channel")
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    try:
        # التحقق من وجود السيرفر
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("This command can only be used in a server!")
            return

        # التحقق من صلاحيات البوت
        if not guild.me.guild_permissions.manage_channels:
            await interaction.response.send_message("I need 'Manage Channels' permission to create/edit channels!")
            return

        await interaction.response.defer()

        try:
            # البحث عن قناة موجودة باستخدام المعرف المخزن
            existing_channel = None
            channel_id = config['COUNTER_CHANNELS'].get(str(guild.id))
            if channel_id:
                try:
                    existing_channel = guild.get_channel(int(channel_id))
                except:
                    config['COUNTER_CHANNELS'].pop(str(guild.id), None)
                    save_config()

            if existing_channel:
                new_name = config['CHANNEL_NAME'].format(count=guild.member_count)
                await existing_channel.edit(name=new_name)
                await interaction.followup.send(f"Updated existing counter channel: {existing_channel.mention}")
                return

            # إنشاء أذونات القناة
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    view_channel=True,
                    connect=False,
                    speak=False,
                    stream=False,
                    send_messages=False
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
            
            if channel and hasattr(channel, 'id'):
                config['COUNTER_CHANNELS'][str(guild.id)] = channel.id
                save_config()
                await interaction.followup.send(f"Counter channel has been created! {channel.mention}")
            else:
                await interaction.followup.send("Failed to create counter channel. Please try again.")

        except discord.Forbidden:
            await interaction.followup.send("I don't have permission to create/edit channels! Please check my permissions.")
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")
            
    except Exception as e:
        try:
            await interaction.followup.send(f"An unexpected error occurred: {str(e)}")
        except:
            print(f"Failed to send error message: {str(e)}")

# تشغيل البوت
if __name__ == "__main__":
    token = config.get('DISCORD_TOKEN')
    if not token:
        print("Error: No Discord token found in config2.json")
        exit(1)
    bot.run(token)
