#!pip install MLB-StatsAPI pandas
import pandas as pd
import statsapi

# I did not find a good endpoint for the abbreviations so I include this dictionary here. 

TEAM_ABBREVIATIONS = {
    108: 'LAA',  # Angels
    109: 'ARI',  # Diamondbacks
    110: 'BAL',  # Orioles
    111: 'BOS',  # Red Sox
    112: 'CHC',  # Cubs
    113: 'CIN',  # Reds
    114: 'CLE',  # Guardians
    115: 'COL',  # Rockies
    116: 'DET',  # Tigers
    117: 'HOU',  # Astros
    118: 'KC',   # Royals
    119: 'LAD',  # Dodgers
    120: 'WSH',  # Nationals
    121: 'NYM',  # Mets
    133: 'OAK',  # Athletics
    134: 'PIT',  # Pirates
    135: 'SD',   # Padres
    136: 'SEA',  # Mariners
    137: 'SF',   # Giants
    138: 'STL',  # Cardinals
    139: 'TBR',  # Rays
    140: 'TEX',  # Rangers
    141: 'TOR',  # Blue Jays
    142: 'MIN',  # Twins
    143: 'PHI',  # Phillies
    144: 'ATL',  # Braves
    146: 'MIA',  # Marlins
    147: 'NYY',  # Yankees
    158: 'MIL',  # Brewers
}

## This function looks up team abbreviation by team id number. 

def get_abbreviation(id):
    return TEAM_ABBREVIATIONS[id]

def get_postseason_teams_by_year(year):
    post_season_teams = {}
    # The postseason roughly starts in October and ends by November 5th (for the last 5 years) 
    start_date = f'{year}-9-30'
    end_date = f'{year}-11-05'
    
    # Fetch all games in that window
    schedule = statsapi.schedule(start_date=start_date, end_date=end_date)

    for game in schedule:
        if game['game_type'] != 'R':
            for side in ['home', 'away']:
                team_id = game.get(f'{side}_id')
                if team_id in TEAM_ABBREVIATIONS:
                    abbrev = TEAM_ABBREVIATIONS[team_id]
                    post_season_teams[abbrev] = team_id
                else:
                    # Skip team_id not in mapping
                    continue
        else:
            continue 
    return dict(sorted(post_season_teams.items()))    


def get_postseason_hitting_by_year(year):
    all_data = []

    start_date = f'{year}-9-30'
    end_date = f'{year}-11-05'
    team_ids = get_postseason_teams_by_year(year)   
    for team_name, team_id in team_ids.items():
        # Fetch all games in that window
        schedule = statsapi.schedule(start_date=start_date, end_date=end_date, team = team_id)
        for game in schedule:
            if game['game_type'] != 'R':
                gid = game['game_id']
                box = statsapi.boxscore_data(gid)
            
                if 'teamInfo' not in box:
                    continue
        
                try:
                    team_stats = (
                        box['away']
                        if box['teamInfo']['away']['id'] == team_id
                        else box['home']
                    )
                    hitting = team_stats['teamStats']['batting']
        
                    all_data.append({
                        'team': team_name,
                        'game_id': gid,
                        'runs': hitting['runs'],
                        'hits': hitting['hits'],
                        'doubles': hitting['doubles'],
                        'triples': hitting['triples'],
                        'home_runs': hitting['homeRuns'],
                        'strike_outs': hitting['strikeOuts'],
                        'walks': hitting['baseOnBalls'],
                        'stolen_bases': hitting['stolenBases'],
                        'left_on_base': hitting['leftOnBase'],
                        'slug': hitting['slg'],
                        'ops': hitting['ops'],
                        'obp': hitting['obp'],
                    })
                except KeyError:
                    continue
        
    return pd.DataFrame(all_data)

def get_postseason_hitting_by_year(year):
    all_data = []

    start_date = f'{year}-9-30'
    end_date = f'{year}-11-05'
    team_ids = get_postseason_teams_by_year(year)   
    for team_name, team_id in team_ids.items():
        # Fetch all games in that window
        schedule = statsapi.schedule(start_date=start_date, end_date=end_date, team = team_id)
        for game in schedule:
            if game['game_type'] != 'R':
                gid = game['game_id']
                box = statsapi.boxscore_data(gid)
            
                if 'teamInfo' not in box:
                    continue
        
                try:
                    team_stats = (
                        box['away']
                        if box['teamInfo']['away']['id'] == team_id
                        else box['home']
                    )
                    hitting = team_stats['teamStats']['batting']
        
                    all_data.append({
                        'team': team_name,
                        'game_id': gid,
                        'runs': hitting['runs'],
                        'hits': hitting['hits'],
                        'doubles': hitting['doubles'],
                        'triples': hitting['triples'],
                        'home_runs': hitting['homeRuns'],
                        'strike_outs': hitting['strikeOuts'],
                        'walks': hitting['baseOnBalls'],
                        'stolen_bases': hitting['stolenBases'],
                        'left_on_base': hitting['leftOnBase'],
                        'slug': hitting['slg'],
                        'ops': hitting['ops'],
                        'obp': hitting['obp'],
                    })
                except KeyError:
                    continue
    df = pd.DataFrame(all_data)
    df['extra_base_hits'] = df['doubles'] + df['triples'] + df['home_runs']
    df['xbh_rate'] = df['extra_base_hits'] / df['hits'].replace(0, 1)   
    return df