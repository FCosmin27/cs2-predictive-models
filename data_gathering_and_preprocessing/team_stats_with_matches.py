import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import time
import json

url = "https://www.hltv.org/ranking/teams/"
prefix = "https://www.hltv.org"
matches_tab_suffix = "#tab-matchesBox"
results= "/results?team="
results_page_2 = "/results?offset=100&team="
results_page_3 = "/results?offset=200&team="

teams = {
    12334 : 'preasy',
    7020 : 'spirit',
    9565 : 'vitality',
    11837 : 'fluxo',
    5752 : 'cloud9',
    11861 : 'aurora',
    5995 : 'g2',
    11251 : 'eternal-fire',
    5378 : 'virtuspro',
    6667 : 'faze',
    9455 : 'imperial',
    8297 : 'furia',
    4494 : 'mouz',
    5973 : 'liquid',
    9215 : 'mibr',
    12527 : 'guild-eagles',
    6248 : 'themongolz',
    4608 : 'natus-vincere',
    6665 : 'astralis',
    11948 : 'nouns',
    8135 : 'forze',
    10567 : 'saw',
    7176 : 'red-canids',
    4991 : 'fnatic',
    11811 : 'monte',
    10577 : 'sinners',
    11641 : 'metizport',
    12591 : 'koi',
    12289 : 'espionage',
    4773 : 'pain',
    11883 : '9-pandas',
    7532 : 'big',
    12376 : 'm80',
    7175 : 'heroic',
    4914 : '3dmax',
    11419 : 'ecstatic',
    10503 : 'og',
    9806 : 'apeks',
    11283 : 'falcons',
    12394 : 'betboom',
    12586 : 'amkal',
    4869 : 'ence',
    11241 : 'b8',
    5005 : 'complexity',
    9928 : 'gamerlegion',
    9996 : '9z',
    8840 : 'lynn-vision',
    7187 : 'nexus',
    12642 : 'rebels',
    12524 : 'pera',
    12144 : 'bestia',
    11768 : 'oddik'
    }

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.5',
}



def get_player_stats(player_url):
    print(f'Getting player stats from {player_url}')
    response = requests.get(player_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        def extract_stat(label):
            
            stat = soup.select_one(f'.player-stat:has(> b:-soup-contains("{label}")) .statsVal')
            if stat:
                return stat.text.strip()
            return 'N/A'

        stats = {
            'Rating': extract_stat('Rating 2.0'),
            'Headshot': extract_stat('Headshot %', 'Headshots') if extract_stat('Headshot %', 'Headshots') != 'N/A' else 'N/A',
            'Maps Played': extract_stat('Maps played'),
            'Kills per Round': extract_stat('Kills per round'),
            'Deaths per Round': extract_stat('Deaths per round'),
        }

        return stats
    else:
        print(f'Failed to retrieve player profile page: {response.status_code}')
        return None


def get_player_profiles(team_page_soup):
    player_profiles = {}
    for player_anchor in team_page_soup.select('.bodyshot-team a.col-custom'):
        if 'href' in player_anchor.attrs:
            player_url = prefix + player_anchor['href']
            player_name = player_anchor.text.strip()
            player_profiles[player_name] = player_url

    return player_profiles


def get_team_ranking(team_page_soup):
    ranking_anchor = team_page_soup.select_one('.profile-team-stats-container a.rankingLink')
    if ranking_anchor and 'href' in ranking_anchor.attrs:
        ranking_url = prefix + ranking_anchor['href']
    ranking_text = ranking_anchor.text if ranking_anchor else 'Not found'
    return ranking_text

def get_team_ranking(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    ranking_span = soup.select_one('.profile-team-stats-container .right')
    if ranking_span and ranking_span.text:
        ranking_text = ranking_span.text.strip()
        ranking_number = ranking_text.lstrip('#')
        return ranking_number
    else:
        return None

def get_team_info(team_id, team_name):
    team_url = prefix + "/team/" + str(team_id) + "/" + team_name
    print(f'Getting team stats from {team_url}')
    response = requests.get(team_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        ranking = get_team_ranking(response.text)
        win_rate_stat = soup.select_one('.highlighted-stat .description:-soup-contains("Win rate")')
        if win_rate_stat:
            win_percentage = win_rate_stat.find_previous_sibling(class_="stat").text.strip()[:-1]
        else:
            win_percentage = 'Not found'
        
        player_profiles = get_player_profiles(soup)

        players_stats = {}
        for player_name, player_url in player_profiles.items():
            player_stats = get_player_stats(player_url)
            if player_stats:
                players_stats[player_name] = player_stats
            time.sleep(0.5)

        return {'ranking' : ranking, 'win_percentage': win_percentage, 'players_stats': players_stats}

    else:
        print(f'Failed to retrieve team matches page: {response.status_code}')
        return None

def parse_date_from_text(date_text):
    match = re.search(r'(\w+) (\d+)(st|nd|rd|th) (\d{4})', date_text)
    if match:
        month, day, _, year = match.groups()
        date_object = datetime.strptime(f'{day} {month} {year}', '%d %B %Y')
        return date_object.strftime('%d/%m/%Y')
    else:
        return None

def get_team_results(team_id):
    results_url = prefix + results + str(team_id)
    print(f'Getting team results from {results_url}')
    response = requests.get(results_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        date_text = soup.select_one('.results-sublist .standard-headline').text
        match_date = parse_date_from_text(date_text)

        matches_data = []

        for match in soup.select('.results-holder .a-reset'):
            team1_el = match.select_one('.team-cell .line-align.team1 .team, .team-cell .line-align.team1 .team-won')
            team1_name = team1_el.text.strip() if team1_el else 'N/A'

            score_el = match.select_one('.result-score')
            score = score_el.text.strip() if score_el else 'N/A'

            team2_el = match.select_one('.team-cell .line-align.team2 .team, .team-cell .line-align.team2 .team-won')
            team2_name = team2_el.text.strip() if team2_el else 'N/A'

            event_el = match.select_one('.event-name')
            event_name = event_el.text.strip() if event_el else 'N/A'

            match_info = {
                'date': match_date,
                'team1': team1_name,
                'score': score,
                'team2': team2_name,
                'event': event_name
            }

            matches_data.append(match_info)
        time.sleep(0.5)
        return matches_data
    else:
        print(f'Failed to retrieve results page: {response.status_code}')
        return None

def main():
    
    teams_data = {}
    for team_id, team_name in teams.items():
        teams_data[team_name] = {
            'position': 'Not found',
            'win_percentage': 'Not found',
            'players': {},
            'matches': {}
        }

        team_page = prefix + str(team_id) + '/' + team_name

        team_info = get_team_info(team_id, team_name)
        if team_info:
            teams_data[team_name]['position'] = team_info['ranking']
            teams_data[team_name]['win_percentage'] = team_info['win_percentage']
            teams_data[team_name]['players'] = team_info['players_stats']

        matches = get_team_results(team_id)
        if matches:
            teams_data[team_name]['matches'] = matches

    with open('teams_data.json', 'w') as outfile:
        json.dump(teams_data, outfile, indent=4)                                                                                                                                                                                                                                                                                                                                                                                                                                                                            


if __name__ == '__main__':
    main()