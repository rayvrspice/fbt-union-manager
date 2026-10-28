
import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("TEST_GUILD_ID", "0"))

if not TOKEN or not GUILD_ID:
    raise RuntimeError(
        "Set DISCORD_BOT_TOKEN and TEST_GUILD_ID in your .env file."
    )

TEST_GUILD = discord.Object(id=GUILD_ID)

LAYOUT = {
    "👋 START HERE": [
        "📢・announcements",
        "📜・rules-and-info",
        "✅・get-verified",
        "🎭・choose-roles",
        "🎫・support-tickets",
    ],
    "💬 COMMUNITY": [
        "💬・general-chat",
        "👋・introductions",
        "📸・media-sharing",
        "🎮・gaming-and-music",
        "💡・suggestions",
    ],
    "🎨 CREATORS STUDIO": [
        "💬・creator-chat",
        "🎨・creator-showcase",
        "🤝・collabs-and-commissions",
        "📚・creator-resources",
        "📣・creator-promotions",
    ],
    "🎉 EVENTS & DANCE": [
        "📅・upcoming-events",
        "🎟️・event-registration",
        "💃・dance-and-djs",
        "🏆・event-highlights",
    ],
    "🤖 FULL BODY TRACKING": [
        "💬・fbt-chat",
        "🛠️・setup-and-support",
        "📚・fbt-guides",
        "🌐・fbt-worlds",
        "📸・tracking-showcase",
    ],
    "🌍 WORLDS & PARTNERS": [
        "🌐・world-directory",
        "🤝・partner-clubs",
        "📩・partnership-applications",
        "📸・world-showcase",
    ],
    "🤝 COLLABORATIONS": [
        "📢・collab-announcements",
        "💬・collab-lounge",
        "🤝・find-collaborators",
        "📅・collab-events",
    ],
    "💃 DANCE ACADEMY": [
        "📢・academy-info",
        "📚・dance-lessons",
        "🎬・practice-and-feedback",
        "🤝・practice-partners",
    ],
}

FORUMS = {
    "🎨・creator-showcase",
    "🛠️・setup-and-support",
    "🌐・world-directory",
    "🤝・find-collaborators",
    "📚・dance-lessons",
}

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync(guild=TEST_GUILD)
    print(f"Connected as {bot.user}")
    print(f"Test server ID: {GUILD_ID}")


def is_test_admin(interaction):
    return (
        interaction.guild_id == GUILD_ID
        and interaction.user.guild_permissions.administrator
    )


@bot.tree.command(
    name="preview_layout",
    description="Preview the FBT UNION server layout.",
    guild=TEST_GUILD,
)
async def preview_layout(interaction: discord.Interaction):
    if not is_test_admin(interaction):
        await interaction.response.send_message(
            "Only test server administrators can use this.",
            ephemeral=True,
        )
        return

    lines = [
        f"**{category}** — {len(channels)} channels"
        for category, channels in LAYOUT.items()
    ]

    await interaction.response.send_message(
        "**FBT UNION Proposed Layout**\n\n"
        + "\n".join(lines)
        + "\n\nNo changes have been made.",
        ephemeral=True,
    )


@bot.tree.command(
    name="build_layout",
    description="Create the FBT UNION test server layout.",
    guild=TEST_GUILD,
)
@app_commands.describe(
    confirm="Select true to create the categories and channels."
)
async def build_layout(
    interaction: discord.Interaction,
    confirm: bool,
):
    if not is_test_admin(interaction):
        await interaction.response.send_message(
            "Only test server administrators can use this.",
            ephemeral=True,
        )
        return

    if not confirm:
        await interaction.response.send_message(
            "Cancelled. No changes were made.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(
        ephemeral=True,
        thinking=True,
    )

    guild = interaction.guild
    created_categories = 0
    created_channels = 0
    errors = []

    for category_name, channel_names in LAYOUT.items():
        category = discord.utils.get(
            guild.categories,
            name=category_name,
        )

        if category is None:
            try:
                category = await guild.create_category(
                    category_name,
                    reason="FBT UNION test layout",
                )
                created_categories += 1
            except discord.HTTPException as error:
                errors.append(f"{category_name}: {error}")
                continue

        for channel_name in channel_names:
            existing = discord.utils.get(
                category.channels,
                name=channel_name,
            )

            if existing:
                continue

            try:
                if channel_name in FORUMS:
                    await guild.create_forum(
                        channel_name,
                        category=category,
                        reason="FBT UNION test layout",
                    )
                else:
                    await guild.create_text_channel(
                        channel_name,
                        category=category,
                        reason="FBT UNION test layout",
                    )

                created_channels += 1

            except discord.HTTPException as error:
                errors.append(f"{channel_name}: {error}")

    result = (
        "**FBT UNION Layout Build Finished**\n"
        f"Categories created: {created_categories}\n"
        f"Channels created: {created_channels}\n"
        f"Errors: {len(errors)}"
    )

    if errors:
        result += "\n\n" + "\n".join(errors[:5])

    await interaction.followup.send(
        result,
        ephemeral=True,
    )


bot.run(TOKEN)
