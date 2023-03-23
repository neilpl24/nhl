import requests
import pandas as pd


def game_scraper(game_id):
    event_list = []
    event_df = pd.DataFrame(
        columns=['season', 'event', 'secondaryType', 'x', 'y', 'period', 'periodType', 'periodTime', 'periodTimeRemaining',
                 'home_goals', 'away_goals', 'shooter', 'goalie', 'team', 'opposing_team', 'strength'])
    shifts = requests.get(
        f"https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId={game_id}").json()
    game = requests.get(
        f"https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live?site=en_nhl").json()
    if True:  # For filtering purposes for the season scraper, too lazy to remove
        plays = game['liveData']['plays']['allPlays']
        home = game['gameData']['teams']['home']['name']
        away = game['gameData']['teams']['away']['name']
        for play in plays:
            # Don't add shootout plays
            if play['about']['period'] > 4:
                break
            period_time = [sum(x * int(t) for x, t in zip([3600, 60, 1],
                               play['about']['periodTime'].split(":")))/60]
            event = play['result']['event']

            # Faulty data (no x and/or y coordinate)
            if len(play['coordinates'].keys()) < 2:
                event_list.append(pd.DataFrame.from_dict({'event': [play['result']['event']], 'period': [play['about']['period']],
                                                          'periodTime': period_time, 'periodTimeRemaining': [sum(x * int(t) for x, t in zip([3600, 60, 1], play['about']['periodTimeRemaining'].split(":")))/60],
                                                          'periodType': [play['about']['periodType']],  'secondaryType': ['NA'], 'team': ['NA'], 'season': ['2021'], 'gameID': [game_id], 'away_goals': [play['about']['goals']['away']],
                                                          'home_goals': [play['about']['goals']['home']], 'shooter': ['NA'], 'x': ['NA'], 'y': ['NA'], 'goalie': ['NA'],
                                                          'opposing_team': ['NA'], 'strength': ['NA'], 'team_skaters': ['NA'], 'opposing_skaters': ['NA'], 'home': [home], 'away': [away], 'isEmpty': ['NA']}))
            # Goal Events
            elif event == 'Goal':
                if len(play['players']) == 1:
                    goalie = 'ENG'
                else:
                    for player in play['players']:
                        goalie = 'NA'
                        if player['playerType'] == 'Goalie':
                            goalie = player['player']['fullName']
                secondaryType = 'NA' if('secondaryType' not in play['result'].keys(
                )) else play['result']['secondaryType']
                play = away if play['team']['name'] == home else home
                isEmpty = play['result']['emptyNet']
                team = play['team']['name']
                team_arr = []
                opposing_arr = []
                team_skaters = 0
                opposing_skaters = 0
                strength = ''

                # Get Shift Data
                for shift in shifts['data']:
                    if period_time >= [sum(x * int(t) for x, t in zip([3600, 60, 1],
                                                                      shift['startTime'].split(":")))/60] and period_time < [sum(x * int(t) for x, t in zip([3600, 60, 1],
                                                                                                                                                            shift['endTime'].split(":")))/60] and play['about']['period'] == shift['period']:
                        if shift['teamName'] == team:
                            team_skaters = team_skaters + 1
                            team_arr.append(
                                shift['firstName'] + ' ' + shift['lastName'])
                        else:
                            opposing_skaters = opposing_skaters + 1
                            opposing_arr.append(
                                shift['firstName'] + ' ' + shift['lastName'])
                if team_skaters == opposing_skaters:
                    strength = 'EV'
                elif team_skaters < opposing_skaters and opposing_skaters < 7:
                    strength = 'Shorthanded'
                elif team_skaters > opposing_skaters and team_skaters < 7:
                    strength = 'Powerplay'
                else:
                    strength = 'Other'
                event_list.append(pd.DataFrame.from_dict({'event': [play['result']['event']], 'secondaryType': [secondaryType], 'x': [play['coordinates']['x']],  'y': [play['coordinates']['y']], 'shooter': [play['players'][0]['player']['fullName']], 'goalie': [goalie], 'period': [play['about']['period']],
                                                          'periodTime': period_time, 'periodTimeRemaining': [sum(x * int(t) for x, t in zip([3600, 60, 1], play['about']['periodTimeRemaining'].split(":")))/60],
                                                          'periodType': [play['about']['periodType']], 'team': team, 'season': ['2021'],
                                                          'gameID': [game_id], 'away_goals': [play['about']['goals']['away']], 'home_goals': [play['about']['goals']['home']], 'opposing_team': [opposing_team],
                                                          'strength': [strength], 'team_skaters': [team_arr], 'opposing_skaters': [opposing_arr], 'home': [home], 'away': [away], 'isEmpty': [isEmpty]}))
            # Shot Events
            elif event == 'Shot':
                if len(play['players']) == 1:
                    goalie = 'ENG'
                else:
                    for player in play['players']:
                        goalie = 'NA'
                        if player['playerType'] == 'Goalie':
                            goalie = player['player']['fullName']
                if('secondaryType' not in play['result'].keys()):
                    secondaryType = 'NA'
                else:
                    secondaryType = play['result']['secondaryType']
                if(play['team']['name'] == home):
                    opposing_team = away
                else:
                    opposing_team = home
                team = play['team']['name']
                team_arr = []
                opposing_arr = []
                team_skaters = 0
                opposing_skaters = 0
                strength = ''

                # Shift Data
                for shift in shifts['data']:
                    if period_time >= [sum(x * int(t) for x, t in zip([3600, 60, 1],
                                                                      shift['startTime'].split(":")))/60] and period_time < [sum(x * int(t) for x, t in zip([3600, 60, 1],
                                                                                                                                                            shift['endTime'].split(":")))/60] and play['about']['period'] == shift['period']:
                        if shift['teamName'] == team:
                            team_skaters = team_skaters + 1
                            team_arr.append(
                                shift['firstName'] + ' ' + shift['lastName'])
                        else:
                            opposing_skaters = opposing_skaters + 1
                            opposing_arr.append(
                                shift['firstName'] + ' ' + shift['lastName'])
                if team_skaters == opposing_skaters:
                    strength = 'EV'
                elif team_skaters < opposing_skaters and opposing_skaters < 7:
                    strength = 'Shorthanded'
                elif team_skaters > opposing_skaters and team_skaters < 7:
                    strength = 'Powerplay'
                else:
                    strength = 'Other'
                event_list.append(pd.DataFrame.from_dict({'event': [play['result']['event']], 'team': team,  'period': [play['about']['period']], 'shooter': [play['players'][0]['player']['fullName']], 'goalie': [goalie],
                                                          'periodTime': period_time, 'periodTimeRemaining': [sum(x * int(t) for x, t in zip([3600, 60, 1], play['about']['periodTimeRemaining'].split(":")))/60],
                                                          'x': [play['coordinates']['x']],  'y': [play['coordinates']['y']], 'periodType': [play['about']['periodType']], 'secondaryType': [secondaryType], 'season': ['2021'],
                                                          'gameID': [game_id], 'away_goals': [play['about']['goals']['away']], 'home_goals': [play['about']['goals']['home']],
                                                          'opposing_team': [opposing_team], 'strength': [strength], 'team_skaters': [team_arr], 'opposing_skaters': [opposing_arr], 'home': [home], 'away': [away], 'isEmpty': ['NA']}))
            # Missed Shot Events
            elif event == 'Missed Shot':
                if(play['team']['name'] == home):
                    opposing_team = away
                else:
                    opposing_team = home
                team_arr = []
                opposing_arr = []
                team = play['team']['name']
                team_skaters = 0
                opposing_skaters = 0
                strength = ''

                # Shift Data
                for shift in shifts['data']:
                    if period_time >= [sum(x * int(t) for x, t in zip([3600, 60, 1],
                                                                      shift['startTime'].split(":")))/60] and period_time < [sum(x * int(t) for x, t in zip([3600, 60, 1],
                                                                                                                                                            shift['endTime'].split(":")))/60] and play['about']['period'] == shift['period']:
                        if shift['teamName'] == team:
                            team_skaters = team_skaters + 1
                            team_arr.append(
                                shift['firstName'] + ' ' + shift['lastName'])
                        else:
                            opposing_skaters = opposing_skaters + 1
                            opposing_arr.append(
                                shift['firstName'] + ' ' + shift['lastName'])
                if team_skaters == opposing_skaters:
                    strength = 'EV'
                elif team_skaters < opposing_skaters and opposing_skaters < 7:
                    strength = 'Shorthanded'
                elif team_skaters > opposing_skaters and team_skaters < 7:
                    strength = 'Powerplay'
                else:
                    strength = 'Other'
                event_list.append(pd.DataFrame.from_dict({'event': [play['result']['event']], 'x': [play['coordinates']['x']],  'y': [play['coordinates']['y']], 'shooter': [play['players'][0]['player']['fullName']], 'period': [play['about']['period']],
                                                          'periodTime': period_time, 'periodTimeRemaining': [sum(x * int(t) for x, t in zip([3600, 60, 1], play['about']['periodTimeRemaining'].split(":")))/60],
                                                          'periodType': [play['about']['periodType']], 'team': team, 'secondaryType': ['NA'], 'season': ['2021'], 'gameID': [game_id],
                                                          'away_goals': [play['about']['goals']['away']], 'home_goals': [play['about']['goals']['home']],
                                                          'opposing_team': [opposing_team], 'goalie': ['NA'], 'strength': [strength], 'team_skaters': [team_arr], 'opposing_skaters': [opposing_arr], 'home': [home], 'away': [away], 'isEmpty': ['NA']}))
            # Everything Else
            else:
                if 'team' not in play.keys():
                    team = 'NA'
                    opposing_team = 'NA'
                else:
                    team = play['team']['name']
                    if(play['team']['name'] == home):
                        opposing_team = away
                    else:
                        opposing_team = home
                team_arr = []
                opposing_arr = []
                team_skaters = 0
                opposing_skaters = 0
                strength = ''

                # Shift Data
                for shift in shifts['data']:
                    if period_time >= [sum(x * int(t) for x, t in zip([3600, 60, 1],
                                                                      shift['startTime'].split(":")))/60] and period_time < [sum(x * int(t) for x, t in zip([3600, 60, 1],
                                                                                                                                                            shift['endTime'].split(":")))/60] and play['about']['period'] == shift['period']:
                        if shift['teamName'] == team:
                            team_skaters = team_skaters + 1
                            team_arr.append(
                                shift['firstName'] + ' ' + shift['lastName'])
                        else:
                            opposing_skaters = opposing_skaters + 1
                            opposing_arr.append(
                                shift['firstName'] + ' ' + shift['lastName'])
                if team_skaters == opposing_skaters:
                    strength = 'EV'
                elif team_skaters < opposing_skaters and opposing_skaters < 7:
                    strength = 'Shorthanded'
                elif team_skaters > opposing_skaters and team_skaters < 7:
                    strength = 'Powerplay'
                else:
                    strength = 'Other'

                event_list.append(pd.DataFrame.from_dict({'event': [play['result']['event']], 'x': [play['coordinates']['x']],  'y': [play['coordinates']['y']], 'period': [play['about']['period']],
                                                          'periodTime': period_time, 'periodTimeRemaining': [sum(x * int(t) for x, t in zip([3600, 60, 1], play['about']['periodTimeRemaining'].split(":")))/60],
                                                          'periodType': [play['about']['periodType']], 'team': team,  'secondaryType': ['NA'], 'season': ['2021'], 'gameID': [game_id], 'away_goals': [play['about']['goals']['away']],
                                                          'home_goals': [play['about']['goals']['home']], 'opposing_team': [opposing_team], 'goalie': ['NA'], 'shooter': ['NA'],
                                                          'strength': [strength], 'team_skaters': [team_arr], 'opposing_skaters': [opposing_arr], 'home': [home], 'away': [away], 'isEmpty': ['NA']}))
    event_df = pd.concat(event_list)
    event_df.to_csv(f'{game_id}.csv', index=False)


game_scraper(2022021012)
