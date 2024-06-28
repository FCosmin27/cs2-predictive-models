import pandas as pd
import json

with open('data/teams_stats_with_matches.json', 'r') as file:
    data = json.load(file)

teams_data = []
players_data = []
matches_data = []
missing_teams = set()

for team_name, details in data.items():
    teams_data.append({
        'Team_Name': team_name.replace(' ', '_'),
        'Position': int(details['position']),
        'Win_Percentage': float(details['win_percentage']),
    })
    for player_name, stats in details['players'].items():
        players_data.append({
            'Team_Name': team_name.replace(' ', '_'),
            'Player_Name': player_name.replace(' ', '_'),
            'Rating': float(stats.get('Rating', 0)),
            'Kills_Per_Round': float(stats.get('Kills Per Round', 0)),
            'Deaths_Per_Round': float(stats.get('Deaths Per Round', 0)),
            'Headshots': float(stats.get('Headshots', '0%').rstrip('%')),
            'Maps_Played': int(stats.get('Maps Played', 0)),
        })

df_teams = pd.DataFrame(teams_data)
df_players = pd.DataFrame(players_data)

for team_name, details in data.items():
    team1_name = team_name.replace(' ', '_').lower()
    team1_filter = df_teams[df_teams['Team_Name'] == team1_name]

    if team1_filter.empty:
        missing_teams.add(team1_name)  
        continue

    for match in details['matches']:
        if match['score'] != '-:-':
            team2_name = match['team2'].replace(' ', '_').lower()
            team2_filter = df_teams[df_teams['Team_Name'] == team2_name]

            if team2_filter.empty:
                missing_teams.add(team2_name)
                continue

            match_dict = {
                'Date': match['date'],
                'Team1': team1_name,
                'Team2': team2_name,
                'Score': 1 if int(match['score'].split(':')[0]) > int(match['score'].split(':')[1]) else 0,
                'Team1_Position': team1_filter.iloc[0]['Position'],
                'Team1_Win_Percentage': team1_filter.iloc[0]['Win_Percentage'],
                'Team2_Position': team2_filter.iloc[0]['Position'],
                'Team2_Win_Percentage': team2_filter.iloc[0]['Win_Percentage'],
            }

            for team, team_name in [('Team1', team1_name), ('Team2', team2_name)]:
                players = df_players[df_players['Team_Name'] == team_name]
                if not players.empty:
                    for i, row in enumerate(players.itertuples(), 1):
                        match_dict[f'{team}_Player{i}_Rating'] = getattr(row, 'Rating', 0)
                        match_dict[f'{team}_Player{i}_Kills_Per_Round'] = getattr(row, 'Kills_Per_Round', 0)
                        match_dict[f'{team}_Player{i}_Deaths_Per_Round'] = getattr(row, 'Deaths_Per_Round', 0)
                        match_dict[f'{team}_Player{i}_Headshots'] = getattr(row, 'Headshots', 0)

            matches_data.append(match_dict)

print("Missing team data for the following teams:")
for team in missing_teams:
    print(team)

df_matches = pd.DataFrame(matches_data)
df_matches.to_csv('data/match_data.csv', index=False)
