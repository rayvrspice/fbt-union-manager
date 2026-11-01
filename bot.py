
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


@bot.tree.command(
    name="setup_staff",
    description="Create a private staff headquarters in the test server.",
    guild=TEST_GUILD,
)
async def setup_staff(interaction: discord.Interaction):
    if not is_test_admin(interaction):
        await interaction.response.send_message(
            "Only test server administrators can use this.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(
        ephemeral=True,
        thinking=True,
    )

    guild = interaction.guild

    staff_channels = [
        "📢・staff-announcements",
        "💬・staff-chat",
        "🛡️・moderation",
        "📁・incident-reports",
        "📋・staff-resources",
        "👑・executive-office",
    ]

    category_name = "🔒 STAFF HEADQUARTERS"

    try:
        category = discord.utils.get(
            guild.categories, name=category_name
        )

        if category is None:
            category = await guild.create_category(
                category_name,
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(
                        view_channel=False
                    )
                },
                reason="FBT UNION private staff setup",
            )
        else:
            await category.set_permissions(
                guild.default_role,
                view_channel=False,
            )

        created = 0

        for name in staff_channels:
            channel = discord.utils.get(
                category.text_channels, name=name
            )

            if channel is None:
                channel = await guild.create_text_channel(
                    name,
                    category=category,
                    overwrites=category.overwrites,
                    reason="FBT UNION private staff setup",
                )
                created += 1
            else:
                await channel.set_permissions(
                    guild.default_role,
                    view_channel=False,
                )

        await interaction.followup.send(
            f"Staff headquarters configured.\n"
            f"New channels created: {created}\n"
            "Access: Server administrators only for now.",
            ephemeral=True,
        )

    except discord.DiscordException as error:
        await interaction.followup.send(
            f"Setup failed: {error}",
            ephemeral=True,
        )


# FBT UNION - Save and compare server layouts

import json
from datetime import datetime, timezone
from pathlib import Path


def save_permission_overwrites(channel):
    results = []

    for target, overwrite in channel.overwrites.items():
        allow, deny = overwrite.pair()
        results.append({
            "target_id": target.id,
            "target_name": target.name,
            "target_type": (
                "role" if isinstance(target, discord.Role)
                else "member"
            ),
            "allow": allow.value,
            "deny": deny.value,
        })

    return sorted(results, key=lambda x: x["target_id"])


def capture_server_layout(guild):
    categories = []

    for category in sorted(
        guild.categories, key=lambda c: c.position
    ):
        categories.append({
            "id": category.id,
            "name": category.name,
            "position": category.position,
            "permissions": save_permission_overwrites(category),
        })

    channels = []

    for channel in guild.channels:
        if isinstance(channel, discord.CategoryChannel):
            continue

        channels.append({
            "id": channel.id,
            "name": channel.name,
            "type": str(channel.type),
            "category_id": channel.category_id,
            "position": channel.position,
            "topic": getattr(channel, "topic", None),
            "slowmode": getattr(
                channel, "slowmode_delay", None
            ),
            "nsfw": getattr(channel, "nsfw", False),
            "bitrate": getattr(channel, "bitrate", None),
            "user_limit": getattr(
                channel, "user_limit", None
            ),
            "permissions": save_permission_overwrites(
                channel
            ),
            "forum_tags": [
                {
                    "id": tag.id,
                    "name": tag.name,
                    "moderated": tag.moderated,
                    "emoji": (
                        str(tag.emoji) if tag.emoji else None
                    ),
                }
                for tag in getattr(
                    channel, "available_tags", []
                )
            ],
        })

    roles = []

    for role in guild.roles:
        roles.append({
            "id": role.id,
            "name": role.name,
            "position": role.position,
            "color": role.color.value,
            "permissions": role.permissions.value,
            "hoist": role.hoist,
            "mentionable": role.mentionable,
            "managed": role.managed,
        })

    return {
        "saved_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "server_id": guild.id,
        "server_name": guild.name,
        "categories": categories,
        "channels": channels,
        "roles": roles,
    }


def compare_layout_items(previous, current, section):
    old = {
        item["id"]: item
        for item in previous.get(section, [])
    }
    new = {
        item["id"]: item
        for item in current.get(section, [])
    }

    added = len(new.keys() - old.keys())
    removed = len(old.keys() - new.keys())
    changed = sum(
        old[item_id] != new[item_id]
        for item_id in old.keys() & new.keys()
    )

    return f"{section}: +{added} / -{removed} / {changed} edited"


@bot.tree.command(
    name="save_layout",
    description="Scan and save the current FBT UNION test server.",
    guild=TEST_GUILD,
)
async def save_layout(interaction: discord.Interaction):
    if not is_test_admin(interaction):
        await interaction.response.send_message(
            "Only test server administrators can use this.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(
        ephemeral=True,
        thinking=True,
    )

    try:
        folder = Path(__file__).resolve().parent / "snapshots"
        folder.mkdir(parents=True, exist_ok=True)
        folder.chmod(0o700)

        latest = folder / "latest.json"
        previous = None

        if latest.exists():
            previous = json.loads(
                latest.read_text(encoding="utf-8")
            )

        snapshot = capture_server_layout(interaction.guild)

        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%d_%H%M%S_%f")

        archive = folder / f"layout_{timestamp}.json"
        content = json.dumps(
            snapshot, indent=2, ensure_ascii=False
        )

        for file in (archive, latest):
            file.write_text(content, encoding="utf-8")
            file.chmod(0o600)

        message = (
            "**FBT UNION Layout Saved**\n"
            f"Categories: {len(snapshot['categories'])}\n"
            f"Channels: {len(snapshot['channels'])}\n"
            f"Roles: {len(snapshot['roles'])}\n"
        )

        if previous:
            message += "\n**Changes since previous save:**\n"
            for section in ("categories", "channels", "roles"):
                message += (
                    compare_layout_items(
                        previous, snapshot, section
                    ) + "\n"
                )
        else:
            message += "\nFirst snapshot saved as baseline."

        message += "\nBackup stored privately on Oracle."

        await interaction.followup.send(
            message, ephemeral=True
        )

    except Exception as error:
        await interaction.followup.send(
            f"Unable to save layout: {error}",
            ephemeral=True,
        )





bot.run(TOKEN)
