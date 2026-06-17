import requests
import urllib3
import webbrowser
import json
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os

API_KEY = os.environ["FOOTBALL_DATA_API_KEY"]

players = {
    "Aksel": ["Iraq", "Argentina", "England", "Uruguay"],
    "Aure": ["Netherlands", "United States", "Mexico", "Croatia"],
    "Børre": ["Egypt", "Portugal", "Jordan", "Saudi Arabia"],
    "Caspar": ["Uzbekistan", "Canada", "Norway", "Switzerland"],
    "Danny": ["Colombia", "Iran", "Turkey", "Belgium"],
    "Didrik": ["Germany", "Ivory Coast", "France", "Senegal"],
    "Emil": ["Austria", "Spain", "Curaçao", "Ecuador"],
    "Hofstad": ["Czechia", "Ghana", "Congo DR", "South Africa"],
    "Leis": ["Panama", "Scotland", "Bosnia-Herzegovina", "Qatar"],
    "Opie": ["Morocco", "Algeria", "Sweden", "Paraguay"],
    "Wilmer": ["Japan", "Cape Verde Islands", "Brazil", "South Korea"],
    "Zerv": ["Tunisia", "New Zealand", "Australia", "Haiti"],
}


def get_owner(team):
    for player, teams in players.items():
        if team in teams:
            return player
    return "Unassigned"


def get_live_standings():
    url = "https://api.football-data.org/v4/competitions/WC/standings"
    headers = {"X-Auth-Token": API_KEY}

    for attempt in range(3):
        try:
            response = requests.get(
                url,
                headers=headers,
                verify=False,
                timeout=20
            )
            response.raise_for_status()
            break

        except requests.exceptions.RequestException as error:
            print(f"API request failed, attempt {attempt + 1}/3: {error}")

            if attempt == 2:
                raise

    data = response.json()

    standings = []

    for group in data["standings"]:
        group_name = group.get("group", "")

        for row in group["table"]:
            team_name = row["team"]["name"]

            standings.append({
                "Team": team_name,
                "Owner": get_owner(team_name),
                "Group": group_name,
                "Pts": row["points"],
                "GD": row["goalDifference"],
                "Played": row["playedGames"],
                "W": row["won"],
                "D": row["draw"],
                "L": row["lost"],
                "GF": row["goalsFor"],
                "GA": row["goalsAgainst"],
            })

    return standings


def gd_format(gd):
    return f"+{gd}" if gd > 0 else str(gd)


def owner_class(owner):
    return owner.lower().replace("ø", "o").replace(" ", "-")

def load_previous_ranks():
    try:
        with open("previous_ranks.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"top": {}, "worst": {}}


def save_current_ranks(top_race, worst_race):
    ranks = {
        "top": {row["Team"]: i + 1 for i, row in enumerate(top_race)},
        "worst": {row["Team"]: 48 - i for i, row in enumerate(worst_race)}
    }

    with open("previous_ranks.json", "w", encoding="utf-8") as file:
        json.dump(ranks, file, indent=4)


def movement_arrow(current_rank, previous_rank):
    if previous_rank is None:
        return "NEW"

    change = previous_rank - current_rank

    if change > 0:
        return f"↑{change}"
    elif change < 0:
        return f"↓{abs(change)}"
    else:
        return "→"

def make_table(rows, table_type):
    html = """
    <table>
        <tr>
            <th>Rank</th>
            <th>Move</th>
            <th>Owner</th>
            <th>Team</th>
            <th>Group</th>
            <th>Played</th>
            <th>W</th>
            <th>D</th>
            <th>L</th>
            <th>Pts</th>
            <th>GD</th>
            <th>Prize</th>
        </tr>
    """

    for i, row in enumerate(rows):
        if table_type == "top":
            rank = i + 1
            prize = "🥇 600 kr" if i == 0 else "🥈 400 kr" if i == 1 else ""
            row_class = "gold" if i == 0 else "silver" if i == 1 else ""
        else:
            rank = 48 - i
            prize = "🥄 200 kr" if i == 0 else ""
            row_class = "spoon" if i == 0 else ""

        if table_type == "top":
            previous_rank = previous_ranks.get("top", {}).get(row["Team"])
        else:
            previous_rank = previous_ranks.get("worst", {}).get(row["Team"])

        move = movement_arrow(rank, previous_rank)

        html += f"""
        <tr class="{row_class} owner-{owner_class(row["Owner"])}">
            <td>{rank}</td>
            <td>{move}</td>
            <td>{row["Owner"]}</td>
            <td>{row["Team"]}</td>
            <td>{row["Group"]}</td>
            <td>{row["Played"]}</td>
            <td>{row["W"]}</td>
            <td>{row["D"]}</td>
            <td>{row["L"]}</td>
            <td>{row["Pts"]}</td>
            <td>{gd_format(row["GD"])}</td>
            <td>{prize}</td>
        </tr>
        """

    html += "</table>"
    return html


standings = get_live_standings()

top_race = sorted(standings, key=lambda x: (-x["Pts"], -x["GD"], x["Team"]))
worst_race = sorted(standings, key=lambda x: (x["Pts"], x["GD"], x["Team"]))
previous_ranks = load_previous_ranks()
winner = top_race[0]
runner_up = top_race[1]
worst = worst_race[0]

last_updated = datetime.now().strftime("%d %b %Y %H:%M")

html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="300">
    <title>World Cup Sweepstake</title>
    <style>
        body {{
            background:
                linear-gradient(
                    to right,
                    transparent 38%,
                    #f4d8dd 38%,
                    #f4d8dd 42%,
                    #ffffff 42%,
                    #ffffff 44%,
                    #00205b 44%,
                    #00205b 56%,
                    #ffffff 56%,
                    #ffffff 58%,
                    #f4d8dd 58%,
                    #f4d8dd 62%,
                    transparent 62%
                ),
                linear-gradient(
                    to bottom,
                    transparent 42%,
                    #f4d8dd 42%,
                    #f4d8dd 46%,
                    #ffffff 46%,
                    #ffffff 48%,
                    #00205b 48%,
                    #00205b 52%,
                    #ffffff 52%,
                    #ffffff 54%,
                    #f4d8dd 54%,
                    #f4d8dd 58%,
                    transparent 58%
                );

            background-color: #f2f5f8;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 30px;
            color: #102030;
        }}
        body::after {{
            content: "";
            position: fixed;
            top: 10px;
            right: 20px;
            width: 320px;
            height: 320px;
            background-image: url("tanker.png");
            background-repeat: no-repeat;
            background-size: contain;
            opacity: 0.08;
            filter: grayscale(100%);
            pointer-events: none;
            z-index: -1;
        }}

        .sponsors-title {{
            font-family: Georgia, serif;
            font-size: 12px;
            font-style: italic;
            letter-spacing: 2px;
            color: #808080;
            margin-bottom: 15px;
        }}
        .sponsors {{
            position: fixed;
            top: 25px;
            left: 25px;
            width: 180px;
            text-align: center;
            opacity: 0.12;
            pointer-events: none;
            z-index: 0;
        }}

        .sponsor-logo {{
            max-width: 75px;
            height: auto;
            margin: 4px;
            vertical-align: middle;
        }}


        h1 {{
            text-align: center;
            font-size: 42px;
            margin-bottom: 10px;
            color: white;
            font-weight: 800;
            letter-spacing: 1px;
            text-shadow: 0 3px 8px rgba(0,0,0,0.25);
        }}
        .updated {{
            text-align: center;
            margin-bottom: 25px;
            color: #607080;
            font-size: 14px;
        }}

        .summary {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 35px;
        }}

        .card {{
            background: white;
            width: 240px;
            padding: 20px;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 4px 14px rgba(0,0,0,0.12);
        }}

        .card h2 {{
            margin: 0;
            font-size: 24px;
        }}

        .card h3 {{
            margin: 14px 0 6px;
            font-size: 26px;
        }}

        .card p {{
            margin: 0;
            font-size: 18px;
            color: #4a5568;
        }}

        .tables {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
        }}

        .box {{
            background: white;
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.12);
            overflow-x: auto;
        }}

        .box h2 {{
            margin-top: 0;
            text-align: center;
            font-size: 24px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}

        th {{
            background: #12395b;
            color: white;
            padding: 10px;
            position: sticky;
            top: 0;
        }}

        td {{
            padding: 8px;
            border-bottom: 1px solid #e0e0e0;
            text-align: center;
        }}

        tr:nth-child(even) {{
            background: #f7f9fb;
        }}

        .gold {{
            background: #fff3bf !important;
            font-weight: bold;
        }}

        .silver {{
            background: #e5e7eb !important;
            font-weight: bold;
        }}

        .spoon {{
            background: #ffd6a5 !important;
            font-weight: bold;
        }}

        @media (max-width: 1000px) {{
            .summary, .tables {{
                display: block;
            }}

            .card, .box {{
                width: auto;
                margin-bottom: 20px;
            }}
        }}

    </style>
</head>
<body>

<h1>🏆 2026 World Cup Ryktebørsen </h1>
<div class="updated">Last updated: {last_updated}</div>

<div class="summary">
    <div class="card">
        <h2>🥇 600 kr</h2>
        <h3>{winner["Owner"]}</h3>
        <p>{winner["Team"]}</p>
    </div>

    <div class="card">
        <h2>🥈 400 kr</h2>
        <h3>{runner_up["Owner"]}</h3>
        <p>{runner_up["Team"]}</p>
    </div>

    <div class="card">
        <h2>🥄 200 kr</h2>
        <h3>{worst["Owner"]}</h3>
        <p>{worst["Team"]}</p>
    </div>
</div>

<div class="tables">
    <div class="box">
        <h2>Race for 1st and 2nd Prize</h2>
        {make_table(top_race, "top")}
    </div>

    <div class="box">
        <h2>Race for Worst Team</h2>
        {make_table(worst_race, "worst")}
    </div>
</div>
<div class="sponsors">
    <div class="sponsors-title">
        This World Cup is Sponsored by
    </div>

    <img src="kia.png" class="sponsor-logo">
    <img src="kaha.png" class="sponsor-logo">
</div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as file:
    file.write(html)

save_current_ranks(top_race, worst_race)

webbrowser.open("index.html")

print("Live leaderboard created: index.html")