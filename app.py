import streamlit as st
import pandas as pd
import statsapi

# I did not find a good endpoint for the abbreviations so I include this dictionary here. 

TEAM_ABBREVIATIONS = {
    108: 'LAA',
    109: 'ARI',
    110: 'BAL',
    111: 'BOS',  
    112: 'CHC', 
    113: 'CIN', 
    114: 'CLE', 
    115: 'COL', 
    116: 'DET', 
    117: 'HOU', 
    118: 'KC',  
    119: 'LAD', 
    120: 'WSH', 
    121: 'NYM', 
    133: 'OAK', 
    134: 'PIT', 
    135: 'SD',  
    136: 'SEA', 
    137: 'SF',  
    138: 'STL', 
    139: 'TBR', 
    140: 'TEX', 
    141: 'TOR', 
    142: 'MIN', 
    143: 'PHI', 
    144: 'ATL', 
    146: 'MIA', 
    147: 'NYY', 
    158: 'MIL', 
}

## This function looks up team abbreviation by team id number. 

def get_abbreviation(id):
    return TEAM_ABBREVIATIONS[id]

@st.cache_data(show_spinner=False)
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


@st.cache_data(show_spinner=False)
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


st.title("MLB Postseason Hitting Stats Dashboard")
year = st.selectbox("Select Year", options = list(range(2015, 2025)), index = 5)

if st.button("Load Data"):
    df = get_postseason_hitting_by_year(year)
    st.subheader(f"Postseason Hitting Stats - {year}")
    st.dataframe(df)

    st.subheader("Team Averages")
    team_summary = df.groupby('team').mean(numeric_only = True)
    st.dataframe(team_summary)

    csv = df.to_csv(index = False).encode("utf-8")
    st.download_button("Download Post-Season Hitting Stats CSV", csv, file_name = f"postseason_hitting_{year}.csv", mime = "text/csv")
    
        