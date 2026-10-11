# ==========================================
#   Discord Music Bot
#   Created & Maintained by Bikio
#   GitHub: https://github.com/bikiogirl
# ==========================================
import asyncio
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
print("done!")
# ----------------------------- Configuration -----------------------------
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PANEL_CHANNEL_ID = int(os.getenv("PANEL_CHANNEL_ID", "0"))
TICKET_CATEGORY_ID = int(os.getenv("TICKET_CATEGORY_ID", "0"))

# (value, label, emoji) - labels are shown in the dropdown menu
TICKET_TOPICS = [
    ("member-staff-issue", "Issues with other members / Staff", "👥"),
    ("server-idea", "Server idea", "💡"),
    ("channel-role-issue", "Problem with channels / roles", "🛠️"),
    ("partnership", "Partnership / Collab", "🤝"),
    ("staff-application", "Staff Team application", "📝"),
    ("other", "Other", "❓"),
]
TOPIC_LABELS = {value: label for value, label, _ in TICKET_TOPICS}

EMBED_COLOR = discord.Color.blurple()
TOPIC_PREFIX = "ticket_owner:"  # stored in the channel topic to identify the ticket owner


# ------------------------------- Helpers --------------------------------
def get_ticket_owner_id(channel: discord.abc.GuildChannel) -> int | None:
    """Read the ticket owner ID from the channel topic."""
    topic = getattr(channel, "topic", None)
    if topic and topic.startswith(TOPIC_PREFIX):
        try:
            return int(topic[len(TOPIC_PREFIX):].split()[0])
        except (ValueError, IndexError):
            return None
    return None


def find_existing_ticket(guild: discord.Guild, user_id: int) -> discord.TextChannel | None:
    """Return the open ticket channel of a user, if any."""
    for channel in guild.text_channels:
        if get_ticket_owner_id(channel) == user_id:
            return channel
    return None


def is_staff(member: discord.Member) -> bool:
    perms = member.guild_permissions
    return perms.administrator or perms.manage_channels


# --------------------------------- Views ---------------------------------
class CloseTicketView(discord.ui.View):
    """Persistent view with the close button."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Ticket",
        style=discord.ButtonStyle.danger,
        emoji="🔒",
        custom_id="ticket:close",
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        owner_id = get_ticket_owner_id(channel)

        if interaction.user.id != owner_id and not is_staff(interaction.user):
            await interaction.response.send_message(
                "You can't close this ticket.", ephemeral=True
            )
            return

        await interaction.response.send_message("🔒 This ticket will be closed in 5 seconds...")
        await asyncio.sleep(5)
        await channel.delete(reason=f"Ticket closed by {interaction.user}")


class TopicSelect(discord.ui.Select):
    """Dropdown menu where the user chooses the ticket topic."""

    def __init__(self):
        options = [
            discord.SelectOption(label=label, value=value, emoji=emoji)
            for value, label, emoji in TICKET_TOPICS
        ]
        super().__init__(
            placeholder="Select the topic of your ticket...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket:topic",
        )

    async def callback(self, interaction: discord.Interaction):
        channel = interaction.channel
        owner_id = get_ticket_owner_id(channel)

        if interaction.user.id != owner_id:
            await interaction.response.send_message(
                "Only the ticket owner can choose the topic.", ephemeral=True
            )
            return

        value = self.values[0]
        label = TOPIC_LABELS[value]

        embed = discord.Embed(
            title="🎫 Ticket",
            description=(
                f"**Topic:** {label}\n\n"
                "Please describe your request in detail and a staff member will reply soon."
            ),
            color=EMBED_COLOR,
        )

        # Replace the dropdown message with the chosen topic + close button
        await interaction.response.edit_message(embed=embed, view=CloseTicketView())

        # Rename the channel to reflect the topic (done once, so rate limits are not an issue)
        try:
            await channel.edit(name=f"{value}-{interaction.user.name}"[:100])
        except discord.HTTPException:
            pass


class TopicSelectView(discord.ui.View):
    """Persistent view containing the topic dropdown."""

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TopicSelect())


class TicketPanelView(discord.ui.View):
    """Persistent view with the 'Open Ticket' button in the panel channel."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Open Ticket",
        style=discord.ButtonStyle.primary,
        emoji="🎫",
        custom_id="ticket:open",
    )
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        user = interaction.user

        # Prevent multiple tickets per user
        existing = find_existing_ticket(guild, user.id)
        if existing:
            await interaction.followup.send(
                f"You already have an open ticket: {existing.mention}", ephemeral=True
            )
            return

        # Permissions: hidden for everyone, visible to the user, the bot and staff roles
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True,
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_channels=True,
                read_message_history=True,
                embed_links=True,
            ),
        }

        # Add every role that has Administrator or Manage Channels
        for role in guild.roles:
            if role.is_default() or role.managed:
                continue
            if role.permissions.administrator or role.permissions.manage_channels:
                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    manage_channels=True,
                )

        category = guild.get_channel(TICKET_CATEGORY_ID) if TICKET_CATEGORY_ID else None

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}"[:100],
            category=category if isinstance(category, discord.CategoryChannel) else None,
            overwrites=overwrites,
            topic=f"{TOPIC_PREFIX}{user.id}",
            reason=f"Ticket opened by {user}",
        )

        embed = discord.Embed(
            title="🎫 New Ticket",
            description=(
                f"Welcome {user.mention}!\n\n"
                "Please select the topic of your ticket from the menu below."
            ),
            color=EMBED_COLOR,
        )
        await channel.send(content=user.mention, embed=embed, view=TopicSelectView())

        await interaction.followup.send(
            f"Your ticket has been created: {channel.mention}", ephemeral=True
        )


# --------------------------------- Bot ----------------------------------
class TicketBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())

    async def setup_hook(self):
        # Register persistent views so buttons/menus keep working after a restart
        self.add_view(TicketPanelView())
        self.add_view(TopicSelectView())
        self.add_view(CloseTicketView())
        await self.tree.sync()


bot = TicketBot()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


@bot.tree.command(name="ticket_panel", description="Post the ticket panel in the configured channel")
@app_commands.default_permissions(administrator=True)
@app_commands.guild_only()
async def ticket_panel(interaction: discord.Interaction):
    channel = interaction.guild.get_channel(PANEL_CHANNEL_ID)
    if channel is None:
        await interaction.response.send_message(
            "Panel channel not found. Check PANEL_CHANNEL_ID in your .env file.", ephemeral=True
        )
        return

    embed = discord.Embed(
        title="🎫 Support Tickets",
        description="Need help or want to talk to the staff team?\nPress the button below to open a ticket.",
        color=EMBED_COLOR,
    )
    await channel.send(embed=embed, view=TicketPanelView())
    await interaction.response.send_message(f"Panel sent to {channel.mention}.", ephemeral=True)


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("DISCORD_TOKEN is missing. Add it to your .env file.")
    bot.run(TOKEN)
