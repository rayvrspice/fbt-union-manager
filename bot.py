
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




# MASTER LAYOUT MANAGEMENT

@bot.tree.command(
    name="compare_layout",
    description="Compare the live test server with its master layout.",
    guild=TEST_GUILD,
)
async def compare_master_layout(interaction: discord.Interaction):
    if not is_test_admin(interaction):
        await interaction.response.send_message(
            "Administrator access required.", ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    from pathlib import Path
    import json

    master_file = (
        Path(__file__).resolve().parent
        / "snapshots" / "master.json"
    )

    if not master_file.exists():
        await interaction.followup.send(
            "No master layout has been saved.", ephemeral=True
        )
        return

    try:
        master = json.loads(master_file.read_text(encoding="utf-8"))

        if int(master["server_id"]) != interaction.guild.id:
            await interaction.followup.send(
                "Master belongs to a different server.",
                ephemeral=True,
            )
            return

        current = capture_server_layout(interaction.guild)

        lines = [
            compare_layout_items(master, current, section)
            for section in ("categories", "channels", "roles")
        ]

        await interaction.followup.send(
            "**FBT UNION — Live vs Master**\n"
            + "\n".join(lines)
            + "\n\n+ Added | - Removed | Edited\n"
            + "No server changes were made.",
            ephemeral=True,
        )

    except Exception as error:
        await interaction.followup.send(
            f"Comparison failed: {error}",
            ephemeral=True,
        )


@bot.tree.command(
    name="set_master_layout",
    description="Promote the latest saved snapshot to master.",
    guild=TEST_GUILD,
)
@app_commands.describe(
    confirm="Select true to approve the latest saved layout."
)
async def set_master_layout(
    interaction: discord.Interaction,
    confirm: bool,
):
    if not is_test_admin(interaction):
        await interaction.response.send_message(
            "Administrator access required.", ephemeral=True
        )
        return

    if not confirm:
        await interaction.response.send_message(
            "Cancelled. Master unchanged.", ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    from pathlib import Path
    from datetime import datetime, timezone
    import json
    import shutil

    folder = Path(__file__).resolve().parent / "snapshots"
    latest = folder / "latest.json"
    master = folder / "master.json"

    try:
        if not latest.exists():
            await interaction.followup.send(
                "Run /save_layout first.", ephemeral=True
            )
            return

        data = json.loads(latest.read_text(encoding="utf-8"))

        if int(data["server_id"]) != interaction.guild.id:
            await interaction.followup.send(
                "Saved layout belongs to another server.",
                ephemeral=True,
            )
            return

        if master.exists():
            stamp = datetime.now(timezone.utc).strftime(
                "%Y%m%d_%H%M%S_%f"
            )
            shutil.copy2(
                master,
                folder / f"master_backup_{stamp}.json",
            )

        shutil.copy2(latest, master)
        master.chmod(0o600)

        await interaction.followup.send(
            "**Master layout updated successfully.**\n"
            f"Categories: {len(data['categories'])}\n"
            f"Channels: {len(data['channels'])}\n"
            f"Roles: {len(data['roles'])}\n"
            "Previous master backed up.",
            ephemeral=True,
        )

    except Exception as error:
        await interaction.followup.send(
            f"Master update failed: {error}",
            ephemeral=True,
        )



# FBT UNION — MASTER LAYOUT BUILDER

async def resolve_master_overwrites(guild, saved):
    overwrites = {}

    for item in saved:
        target_id = int(item["target_id"])

        if item["target_type"] == "role":
            target = guild.get_role(target_id)

        elif item["target_type"] == "member":
            target = guild.get_member(target_id)
            if target is None:
                target = await guild.fetch_member(target_id)

        else:
            raise ValueError("Unknown permission target type")

        if target is None:
            raise ValueError(
                f"Missing permission target: {target_id}"
            )

        overwrites[target] = (
            discord.PermissionOverwrite.from_pair(
                discord.Permissions(int(item["allow"])),
                discord.Permissions(int(item["deny"])),
            )
        )

    return overwrites


@bot.tree.command(
    name="build_master_layout",
    description="Preview or rebuild missing items from the master.",
    guild=TEST_GUILD,
)
@app_commands.describe(
    confirm="False previews; True creates missing items."
)
async def build_master_layout(
    interaction: discord.Interaction,
    confirm: bool,
):
    if not is_test_admin(interaction):
        await interaction.response.send_message(
            "Administrator access required.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(
        ephemeral=True, thinking=True
    )

    from pathlib import Path
    import json

    guild = interaction.guild
    master_file = (
        Path(__file__).resolve().parent
        / "snapshots" / "master.json"
    )

    if not master_file.exists():
        await interaction.followup.send(
            "No master layout found.", ephemeral=True
        )
        return

    created_categories = 0
    created_channels = 0

    try:
        master = json.loads(
            master_file.read_text(encoding="utf-8")
        )

        if int(master["server_id"]) != guild.id:
            raise ValueError(
                "Master belongs to a different server."
            )

        categories = master["categories"]
        channels = master["channels"]

        category_specs = {
            int(c["id"]): c for c in categories
        }

        resolved = {}
        missing_categories = []

        for spec in categories:
            old_id = int(spec["id"])
            found = guild.get_channel(old_id)

            if found is None:
                found = discord.utils.get(
                    guild.categories, name=spec["name"]
                )

            if found is not None and not isinstance(
                found, discord.CategoryChannel
            ):
                raise ValueError(
                    f"Invalid category: {spec['name']}"
                )

            resolved[old_id] = found

            if found is None:
                missing_categories.append(spec)

        missing_channels = []

        supported = {
            "text", "news", "forum", "voice",
            "stage_voice"
        }

        for spec in channels:
            if guild.get_channel(int(spec["id"])):
                continue

            kind = spec["type"]

            if kind not in supported:
                raise ValueError(
                    f"Unsupported channel type: {kind}"
                )

            old_cat_id = spec.get("category_id")

            if old_cat_id is not None:
                old_cat_id = int(old_cat_id)

                if old_cat_id not in category_specs:
                    raise ValueError(
                        f"Unknown category for {spec['name']}"
                    )

            category = resolved.get(old_cat_id)

            if category is not None:
                if any(
                    c.name == spec["name"]
                    for c in category.channels
                ):
                    continue

            missing_channels.append(spec)

        if not confirm:
            await interaction.followup.send(
                "**Master Build Preview**\n"
                f"Missing categories: "
                f"{len(missing_categories)}\n"
                f"Missing channels: "
                f"{len(missing_channels)}\n\n"
                "No changes made.\n"
                "Run with confirm:true to create them.",
                ephemeral=True,
            )
            return

        # Validate saved permissions before creating anything.
        category_permissions = {}

        for spec in categories:
            category_permissions[int(spec["id"])] = (
                await resolve_master_overwrites(
                    guild, spec.get("permissions", [])
                )
            )

        channel_permissions = {}

        for spec in missing_channels:
            old_cat_id = spec.get("category_id")
            old_cat_id = (
                int(old_cat_id)
                if old_cat_id is not None else None
            )

            perms = await resolve_master_overwrites(
                guild, spec.get("permissions", [])
            )

            # Never expose a child of a saved private
            # category through an accidental public overwrite.
            parent_perms = category_permissions.get(
                old_cat_id, {}
            )
            everyone = parent_perms.get(
                guild.default_role
            )

            if (
                everyone is not None
                and everyone.view_channel is False
            ):
                child_everyone = perms.get(
                    guild.default_role,
                    discord.PermissionOverwrite(),
                )
                child_everyone.view_channel = False
                perms[guild.default_role] = child_everyone

            channel_permissions[int(spec["id"])] = perms

        # Create missing categories.
        for spec in missing_categories:
            old_id = int(spec["id"])

            category = await guild.create_category(
                spec["name"],
                overwrites=category_permissions[old_id],
                position=spec["position"],
                reason="FBT UNION master layout rebuild",
            )

            resolved[old_id] = category
            created_categories += 1

        # Create missing channels.
        for spec in missing_channels:
            old_id = int(spec["id"])
            old_cat_id = spec.get("category_id")
            old_cat_id = (
                int(old_cat_id)
                if old_cat_id is not None else None
            )

            category = resolved.get(old_cat_id)
            kind = spec["type"]

            options = {
                "category": category,
                "overwrites": channel_permissions[old_id],
                "position": spec["position"],
                "reason": "FBT UNION master layout rebuild",
            }

            if kind in ("text", "news"):
                await guild.create_text_channel(
                    spec["name"],
                    news=(kind == "news"),
                    topic=spec.get("topic") or "",
                    slowmode_delay=spec.get("slowmode") or 0,
                    nsfw=spec.get("nsfw", False),
                    **options,
                )

            elif kind == "forum":
                tags = []

                for tag in spec.get("forum_tags", []):
                    emoji = tag.get("emoji")

                    if emoji and emoji.startswith("<"):
                        emoji = (
                            discord.PartialEmoji.from_str(
                                emoji
                            )
                        )

                    tags.append(
                        discord.ForumTag(
                            name=tag["name"],
                            moderated=tag.get(
                                "moderated", False
                            ),
                            emoji=emoji,
                        )
                    )

                await guild.create_forum(
                    spec["name"],
                    topic=spec.get("topic") or "",
                    available_tags=tags,
                    nsfw=spec.get("nsfw", False),
                    slowmode_delay=spec.get("slowmode") or 0,
                    **options,
                )

            elif kind == "voice":
                await guild.create_voice_channel(
                    spec["name"],
                    **options,
                )

            elif kind == "stage_voice":
                await guild.create_stage_channel(
                    spec["name"],
                    **options,
                )

            created_channels += 1

        await interaction.followup.send(
            "**Master Build Completed**\n"
            f"Categories created: {created_categories}\n"
            f"Channels created: {created_channels}\n"
            "Existing channels and roles were untouched.",
            ephemeral=True,
        )

    except Exception as error:
        await interaction.followup.send(
            "**Master Build Stopped**\n"
            f"Categories created: {created_categories}\n"
            f"Channels created: {created_channels}\n"
            f"Error: {error}",
            ephemeral=True,
        )



bot.run(TOKEN)
