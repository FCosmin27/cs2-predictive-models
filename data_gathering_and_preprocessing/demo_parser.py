import pandas as pd
import os
from demoparser2 import DemoParser

demo_files = [f for f in os.listdir("../demos/") if f.endswith(".dem")]
all_rounds_data = []

for demo_file in demo_files:
    parser = DemoParser(f"../demos/{demo_file}")
    
    wanted_ticks = parser.parse_event("round_freeze_end")["tick"].tolist()
    wanted_props = [
        "kills_total", "deaths_total", "balance", "current_equip_value",
        "round_start_equip_value", "total_rounds_played", "team_num",
        "inventory", "has_helmet", "has_defuser", "armor_value", "team_clan_name"
    ]
    player_data = parser.parse_ticks(wanted_props, ticks=wanted_ticks)
    
    round_end_data = parser.parse_event("round_end")[['tick', 'winner']]
    round_end_data['total_rounds_played'] = range(len(round_end_data))  # Manual computation of rounds

    grouped_player_data = player_data.groupby('total_rounds_played')
    grouped_round_end_data = round_end_data.groupby('total_rounds_played').last()  # Last winner tick per round

    for name, group in grouped_player_data:
        round_winner = grouped_round_end_data.loc[name, 'winner'] if name in grouped_round_end_data.index else None
        
        pivot_columns = {
            'team_clan_name': 'player_{}_team_name',
            'name': 'player_{}_name',
            'team_num': 'player_{}_team_num',
            'kills_total': 'player_{}_kills_total',
            'deaths_total': 'player_{}_deaths_total',
            'inventory': 'player_{}_inventory',
            'has_defuser': 'player_{}_has_defuser',
            'has_helmet': 'player_{}_has_helmet',
            'armor_value': 'player_{}_armor_value',
            'current_equip_value': 'player_{}_current_equip_value',
            'balance': 'player_{}_balance'
        }

        round_df = pd.DataFrame()  # Reset DataFrame for each round
        player_idx = 1  # Reset player index for each round

        for idx, row in group.iterrows():
            if player_idx > 10:
                break  # Limit to 10 players per round
            for key, val in pivot_columns.items():
                round_df[val.format(player_idx)] = [row[key]]
            player_idx += 1

        if round_winner:
            round_df['round_winner'] = round_winner

        all_rounds_data.append(round_df)

final_df = pd.concat(all_rounds_data, ignore_index=True)
final_df.to_csv('data.csv', index=False)
