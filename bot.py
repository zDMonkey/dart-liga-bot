import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime

# ─────────────────────────────────────────
#  KONFIGURATION
# ─────────────────────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN", "DEIN_TOKEN_HIER")
ERGEBNIS_KANAL = "ergebnisse"
DATA_FILE = "liga_data.json"

LIGEN = {
    "liga1": {"name": "🎯 Liga 1", "first_to": 9},
    "liga2": {"name": "🥈 Liga 2", "first_to": 7},
    "liga3": {"name": "🥉 Liga 3", "first_to": 7},
}

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"liga1": {}, "liga2": {}, "liga3": {}, "matches": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_or_create_player(data, liga_key, name):
    if name not in data[liga_key]:
        data[liga_key][name] = {
            "spiele": 0, "siege": 0, "niederlagen": 0,
            "legs_gewonnen": 0, "legs_verloren": 0, "punkte": 0
        }
    return data[liga_key][name]

def record_result(data, liga_key, spieler1, legs1, spieler2, legs2):
    p1 = get_or_create_player(data, liga_key, spieler1)
    p2 = get_or_create_player(data, liga_key, spieler2)
    p1["spiele"] += 1
    p2["spiele"] += 1
    p1["legs_gewonnen"] += legs1
    p1["legs_verloren"] += legs2
    p2["legs_gewonnen"] += legs2
    p2["legs_verloren"] += legs1
    if legs1 > legs2:
        p1["siege"] += 1
        p1["punkte"] += 3
        p2["niederlagen"] += 1
    else:
        p2["siege"] += 1
        p2["punkte"] += 3
        p1["niederlagen"] += 1
    data["matches"].append({
        "liga": liga_key,
        "spieler1": spieler1, "legs1": legs1,
        "spieler2": spieler2, "legs2": legs2,
        "datum": datetime.now().strftime("%d.%m.%Y %H:%M")
    })

def build_tabelle(data, liga_key):
    # Nach insert: [0]=pos [1]=name [2]=sp [3]=s [4]=n [5]=lg [6]=ll [7]=diff(int) [8]=pkt
    spieler = data[liga_key]
    if not spieler:
        return None
    rows = []
    for name, s in spieler.items():
        diff = s["legs_gewonnen"] - s["legs_verloren"]
        rows.append([name, s["spiele"], s["siege"], s["niederlagen"],
                     s["legs_gewonnen"], s["legs_verloren"], diff, s["punkte"]])
    rows.sort(key=lambda x: (-x[7], -x[6], -x[2]))
    for i, r in enumerate(rows):
        r.insert(0, i + 1)
    return rows

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot gestartet als {bot.user}")

liga_choices = [
    app_commands.Choice(name="🎯 Liga 1 (First to 9)", value="liga1"),
    app_commands.Choice(name="🥈 Liga 2 (First to 7)", value="liga2"),
    app_commands.Choice(name="🥉 Liga 3 (First to 7)", value="liga3"),
]

# ── /ergebnis ──────────────────────────────

@tree.command(name="ergebnis", description="Liga-Ergebnis eintragen (501 Double Out)")
@app_commands.describe(liga="Welche Liga?", spieler1="Spieler 1", legs1="Legs Spieler 1",
                       spieler2="Spieler 2", legs2="Legs Spieler 2")
@app_commands.choices(liga=liga_choices)
async def ergebnis(interaction: discord.Interaction, liga: app_commands.Choice[str],
                   spieler1: str, legs1: int, spieler2: str, legs2: int):
    liga_key = liga.value
    liga_info = LIGEN[liga_key]
    first_to = liga_info["first_to"]
    if legs1 == legs2:
        await interaction.response.send_message("❌ Unentschieden nicht möglich.", ephemeral=True); return
    if max(legs1, legs2) != first_to:
        await interaction.response.send_message(
            f"❌ Gewinner braucht genau **{first_to} Legs**. Eingabe: {spieler1} {legs1}–{legs2} {spieler2}", ephemeral=True); return
    if min(legs1, legs2) < 0:
        await interaction.response.send_message("❌ Negative Legs nicht erlaubt.", ephemeral=True); return

    data = load_data()
    record_result(data, liga_key, spieler1.strip(), legs1, spieler2.strip(), legs2)
    save_data(data)

    gewinner = spieler1 if legs1 > legs2 else spieler2
    verlierer = spieler2 if legs1 > legs2 else spieler1
    gew_legs = max(legs1, legs2)
    ver_legs = min(legs1, legs2)

    embed = discord.Embed(title=f"{liga_info['name']} • Ergebnis", color=0x00cc44, timestamp=datetime.now())
    embed.add_field(name="🏆 Match", value=f"**{gewinner}**  `{gew_legs} – {ver_legs}`  {verlierer}", inline=False)
    embed.add_field(name="📋 Format", value=f"501 Double Out • First to {first_to}", inline=True)
    embed.add_field(name="📝 Eingetragen von", value=interaction.user.mention, inline=True)

    rows = build_tabelle(data, liga_key)
    if rows:
        top5 = rows[:5]
        medals = ["🥇", "🥈", "🥉", "4.", "5."]
        t = "```\n"
        t += f"{'#':<3} {'Spieler':<14} {'Sp':>3} {'S':>3} {'N':>3} {'LG':>4} {'Diff':>5} {'Pkt':>4}\n"
        t += "─" * 45 + "\n"
        for i, r in enumerate(top5):
            t += f"{medals[i]:<3} {r[1]:<14} {r[2]:>3} {r[3]:>3} {r[4]:>3} {r[5]:>4} {r[7]:>+5} {r[8]:>4}\n"
        t += "```"
        embed.add_field(name="📊 Top 5  •  LG = Legs gewonnen", value=t, inline=False)

    embed.set_footer(text="Dart Liga • 501 Double Out")
    kanal = discord.utils.get(interaction.guild.text_channels, name=ERGEBNIS_KANAL)
    if kanal:
        await kanal.send(embed=embed)
        await interaction.response.send_message(f"✅ Eingetragen und in {kanal.mention} gepostet!", ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed)

# ── /tabelle ──────────────────────────────

@tree.command(name="tabelle", description="Aktuelle Ligatabelle anzeigen")
@app_commands.describe(liga="Welche Liga?")
@app_commands.choices(liga=liga_choices)
async def tabelle(interaction: discord.Interaction, liga: app_commands.Choice[str]):
    liga_key = liga.value
    liga_info = LIGEN[liga_key]
    data = load_data()
    rows = build_tabelle(data, liga_key)
    if not rows:
        await interaction.response.send_message(f"📭 Noch keine Ergebnisse für {liga_info['name']}.", ephemeral=True); return

    medals = ["🥇", "🥈", "🥉"]
    t = "```\n"
    t += f"{'#':<4} {'Spieler':<14} {'Sp':>3} {'S':>3} {'N':>3} {'LG':>4} {'LL':>4} {'Diff':>5} {'Pkt':>4}\n"
    t += "─" * 52 + "\n"
    for r in rows:
        pos = r[0]
        medal = medals[pos-1] if pos <= 3 else f"{pos}.  "
        t += f"{medal:<4} {r[1]:<14} {r[2]:>3} {r[3]:>3} {r[4]:>3} {r[5]:>4} {r[6]:>4} {r[7]:>+5} {r[8]:>4}\n"
    t += "```"

    embed = discord.Embed(title=f"{liga_info['name']} • Tabelle", color=0x0099ff, timestamp=datetime.now())
    embed.add_field(name="📊 Standings", value=t, inline=False)
    embed.add_field(name="📋 Format", value=f"501 Double Out • First to {liga_info['first_to']}", inline=True)
    embed.add_field(name="🎮 Spiele gesamt", value=str(sum(r[2] for r in rows) // 2), inline=True)
    embed.set_footer(text="LG=Legs gewonnen | LL=Legs verloren | Diff=Differenz | Pkt=Punkte")
    await interaction.response.send_message(embed=embed)

# ── /stats ──────────────────────────────

@tree.command(name="stats", description="Statistiken eines Spielers anzeigen")
@app_commands.describe(liga="Welche Liga?", spieler="Name des Spielers")
@app_commands.choices(liga=liga_choices)
async def stats(interaction: discord.Interaction, liga: app_commands.Choice[str], spieler: str):
    liga_key = liga.value
    liga_info = LIGEN[liga_key]
    data = load_data()
    spieler = spieler.strip()
    if spieler not in data[liga_key]:
        await interaction.response.send_message(f"❌ **{spieler}** nicht in {liga_info['name']} gefunden.", ephemeral=True); return

    s = data[liga_key][spieler]
    win_rate = round(s["siege"] / s["spiele"] * 100) if s["spiele"] > 0 else 0
    diff = s["legs_gewonnen"] - s["legs_verloren"]
    rows = build_tabelle(data, liga_key)
    rang = next((r[0] for r in rows if r[1] == spieler), "?")

    embed = discord.Embed(title=f"🎯 {spieler} • {liga_info['name']}", color=0xffd700, timestamp=datetime.now())
    embed.add_field(name="🏅 Rang", value=f"#{rang}", inline=True)
    embed.add_field(name="⭐ Punkte", value=str(s["punkte"]), inline=True)
    embed.add_field(name="📊 Win Rate", value=f"{win_rate}%", inline=True)
    embed.add_field(name="🎮 Spiele", value=str(s["spiele"]), inline=True)
    embed.add_field(name="✅ Siege", value=str(s["siege"]), inline=True)
    embed.add_field(name="❌ Niederlagen", value=str(s["niederlagen"]), inline=True)
    embed.add_field(name="🎯 Legs gewonnen", value=str(s["legs_gewonnen"]), inline=True)
    embed.add_field(name="💔 Legs verloren", value=str(s["legs_verloren"]), inline=True)
    embed.add_field(name="📈 Leg-Differenz", value=f"{diff:+d}", inline=True)

    letzte = [m for m in data["matches"] if m["liga"] == liga_key and
              (m["spieler1"] == spieler or m["spieler2"] == spieler)][-5:]
    if letzte:
        history = ""
        for m in reversed(letzte):
            if m["spieler1"] == spieler:
                gegner, eig, geg = m["spieler2"], m["legs1"], m["legs2"]
            else:
                gegner, eig, geg = m["spieler1"], m["legs2"], m["legs1"]
            icon = "✅" if eig > geg else "❌"
            history += f"{icon} vs **{gegner}** `{eig}–{geg}` • {m['datum']}\n"
        embed.add_field(name="📅 Letzte Matches", value=history, inline=False)
    await interaction.response.send_message(embed=embed)

# ── /reset (nur Rolle "Leiter") ──────────

@tree.command(name="reset", description="⚠️ Liga-Daten zurücksetzen (nur Leiter)")
@app_commands.describe(liga="Welche Liga zurücksetzen?")
@app_commands.choices(liga=liga_choices)
@app_commands.checks.has_role("Leiter")
async def reset(interaction: discord.Interaction, liga: app_commands.Choice[str]):
    liga_key = liga.value
    liga_info = LIGEN[liga_key]
    embed = discord.Embed(title="⚠️ Reset bestätigen",
        description=f"Alle Daten für **{liga_info['name']}** werden unwiderruflich gelöscht!\n\nBist du sicher?",
        color=0xff0000)
    await interaction.response.send_message(embed=embed, view=ResetConfirmView(liga_key, liga_info["name"]), ephemeral=True)

@reset.error
async def reset_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message(
            "❌ Nur Mitglieder mit der Rolle **Leiter** können eine Liga zurücksetzen.", ephemeral=True)

class ResetConfirmView(discord.ui.View):
    def __init__(self, liga_key, liga_name):
        super().__init__(timeout=30)
        self.liga_key = liga_key
        self.liga_name = liga_name

    @discord.ui.button(label="✅ Ja, zurücksetzen", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        data[self.liga_key] = {}
        data["matches"] = [m for m in data["matches"] if m["liga"] != self.liga_key]
        save_data(data)
        await interaction.response.edit_message(
            embed=discord.Embed(title="✅ Reset erfolgreich",
                description=f"**{self.liga_name}** wurde zurückgesetzt. Neue Saison kann beginnen! 🎯",
                color=0x00cc44), view=None)

    @discord.ui.button(label="❌ Abbrechen", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(title="Abgebrochen", description="Reset wurde abgebrochen.", color=0x888888), view=None)

bot.run(TOKEN)
