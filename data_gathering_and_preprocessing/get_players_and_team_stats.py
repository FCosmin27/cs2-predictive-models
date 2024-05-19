import requests
from bs4 import BeautifulSoup
import time
import json

url = "https://www.hltv.org/ranking/teams/"
prefix = "https://www.hltv.org"
matches_tab_suffix = "#tab-matchesBox"


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.5',
}



def get_player_stats(player_url):
    print(f'Getting player stats from {player_url}')
    response = requests.get(player_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        stats = {
            'Rating': soup.select_one('.player-stat:has(> b:-soup-contains("Rating 2.0")) .statsVal').text.strip(),
            'Kills Per Round': soup.select_one('.player-stat:has(> b:-soup-contains("Kills per round")) .statsVal').text.strip(),
            'Headshots': soup.select_one('.player-stat:has(> b:-soup-contains("Headshots")) .statsVal').text.strip(),
            'Deaths Per Round': soup.select_one('.player-stat:has(> b:-soup-contains("Deaths per round")) .statsVal').text.strip(),
            'Rounds Contributed': soup.select_one('.player-stat:has(> b:-soup-contains("Rounds contributed")) .statsVal').text.strip()
        }

        return stats
    else:
        print(f'Failed to retrieve player profile page: {response.status_code}')
        return None

def get_team_win_percentage(team_matches_url):
    print(f'Getting team win percentage from {team_matches_url}')
    response = requests.get(team_matches_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        win_rate_stat = soup.select_one('.highlighted-stat .description:-soup-contains("Win rate")')
        if win_rate_stat:
            win_percentage = win_rate_stat.find_previous_sibling(class_="stat").text.strip()
        else:
            win_percentage = 'Not found'

        return win_percentage

    else:
        print(f'Failed to retrieve team matches page: {response.status_code}')
        return None


def main():

    teams_data = {}
    players_data = {}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        ranking_elements = soup.select('.ranked-team.standard-box')

        for team_element in ranking_elements:
            team_name = team_element.select_one('.teamLine .name').text
            team_position = team_element.select_one('.position').text
            team_points = team_element.select_one('.points').text.strip('()')  

            teams_data[team_name] = {
                'position': team_position,
                'points': team_points
            }

            more_link_element = team_element.select_one('.more .moreLink')
            if more_link_element:
                team_matches_url = prefix + more_link_element['href'] + matches_tab_suffix
                team_win_percentage = get_team_win_percentage(team_matches_url)

                if team_win_percentage:
                    teams_data[team_name]['win_percentage'] = team_win_percentage
            else:
                print('No more link found')
            time.sleep(0.3)

            players_info = team_element.select('.lineup-con .player-holder a')

            for player in players_info:
                player_name = player.text.strip()
                player_url = prefix + player['href']
                player_stats = get_player_stats(player_url)
                if player_stats:
                    players_data[player_name] = player_stats
                time.sleep(0.3)   

        with open('teams_stats.json', 'w') as outfile:
            json.dump(teams_data, outfile, indent=4)  
        with open('players_stats.json', 'w') as outfile:
            json.dump(players_data, outfile, indent=4)                                                                                                                                                                                                                                                                                                                                                                                                                                                                              

    else:
        print('Failed to retrieve the rankings page: ', response.status_code)


if __name__ == '__main__':
    main()