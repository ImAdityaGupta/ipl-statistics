import yaml
import pickle
import os
import xlsxwriter
import json
import re
import argparse

all_fields = []

team_converter = {
    'Royal Challengers Bangalore': 'RCB',
    'Pune Warriors': 'Pune',
    'Gujarat Titans': 'GL',
    'Deccan Chargers': 'SRH',
    'Sunrisers Hyderabad': 'SRH',
    'Chennai Super Kings': 'CSK',
    'Rising Pune Supergiants': 'Pune',
    'Delhi Capitals': 'Delhi',
    'Kochi Tuskers Kerala': 'KTK',
    'Lucknow Super Giants': 'LSG',
    'Mumbai Indians': 'MI',
    'Kings XI Punjab': 'KXIP',
    'Punjab Kings': 'KXIP',
    'Kolkata Knight Riders': 'KKR',
    'Rising Pune Supergiant': 'Pune',
    'Rajasthan Royals': 'RR',
    'Delhi Daredevils': 'Delhi',
    'Gujarat Lions': 'GL',
    'Royal Challengers Bengaluru': 'RCB',
}

## For adding to data from a single match
class Temp_Player:
    def __init__(self, name):
        self.every_relevant_ball = []
        self.name = name
        self.relevant_meta_info = []

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        to_print = []
        for field in all_fields:
            to_print.append(getattr(self,field.name))
        return ''.join(str(to_print))




    def __str__(self):
        to_print = []
        for field in all_fields:
            to_print.append(getattr(self,field.name))
        return ''.join(str(to_print))

## For adding different stats
class Field:

    ## Basic info needed for each field. Each field is then added as an attribute to Temp_Player class
    def __init__(self, name, how_to_calculate, default_val, core, big_equals_good=True):
        self.calculator = how_to_calculate
        self.core = core
        self.name = name
        self.default_val = default_val
        self.big_equals_good = big_equals_good

        setattr(Temp_Player, name, default_val)

        all_fields.append(self)


def from_json(position_in_list, document):

    pass


## Checks if player in relevant list, returns player object in list. Helper function for one_game
def add_player(name, relevant_list):
    if '(sub)' in name:
        raise ValueError
        # check_existence = Temp_Player(name)
        # return check_existence


    in_list = False

    check_existence = Temp_Player(name)
    if check_existence in relevant_list:
        in_list = True
        check_existence = relevant_list[relevant_list.index(check_existence)]
    if not in_list:
        relevant_list.append(check_existence)

    return check_existence

## Does core values for temp players from one_match. Helper function for one_game
def parse_data(all_relevant_players):
    for player in all_relevant_players:
        for field in all_fields:
            #if not field.core:
            #    continue
            current_val = getattr(player, field.name)


            setattr(player, field.name, field.calculator(player))


## Returns a list of players relevant to a match with every ball relevant to every player
## Takes in special ID as input
def one_game(unique_id):
    all_relevant_players = []

    all_entries = set()

    with open(f"C:/Users/adidh/Downloads/IPL 2021-20220415T153635Z-001/IPL 2022/ipl/{unique_id}.yaml") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        # data = json.load(f)

        if 'player_of_match' not in data['info']:
            data['info']['player_of_match'] = [""]

        #name_team_1 = data['innings'][0]['1st innings']['team']
        #name_team_2 = data['innings'][1]['2nd innings']['team']

        ## Iterating over both innings
        for index, innings in enumerate(data['innings']):
            if index >= 2:
                continue

            ## Used to get around weird single item dictionary thing
            for key, actual_innings in innings.items():

                ## Iterating over each ball in innings
                for ball_index, ball in enumerate(actual_innings['deliveries']):


                    ## Represents ball of innings, eg 4.6
                    ball_notation = list(ball.keys())[0]

                    ## What actually happened in this ball, could contain any of:
                    ## {'bowler', 'batsman', 'extras', 'non_striker', 'wicket', 'runs'}
                    what_happened = ball[ball_notation]



                    ## We add the missing data of which innings the ball has come from
                    what_happened['which_innings'] = index
                    what_happened['teams_playing'] = data['info']['teams']
                    what_happened['unique_id'] = unique_id
                    what_happened['man_of_match'] = data['info']['player_of_match']


                    not_searchable = {'runs',"extras" ,"which_innings" ,"replacements","teams_playing",
                                      "unique_id",'man_of_match'}

                    ## Basically if a ball involves a person we add that ball to that person's relevant balls
                    for entry in what_happened:
                        if entry not in {'bowler', 'batsman', 'extras', 'non_striker', 'wicket', 'runs',
                                         'which_innings', 'replacements','teams_playing','unique_id','man_of_match'}:
                            raise ValueError(f"{entry}")

                        ## In some cases the data fields contain no people
                        if entry in not_searchable:
                            continue
                        if entry == "wicket":
                            if 'fielders' in what_happened[entry]:
                                for fielder in what_happened[entry]['fielders']:
                                    check_existence = add_player(fielder, all_relevant_players)
                                    check_existence.every_relevant_ball.append(ball)
                            continue


                        check_existence = add_player(what_happened[entry], all_relevant_players)

                        check_existence.every_relevant_ball.append(ball)

                        #print(f"{entry} {what_happened[entry]}")


                        all_entries.add(entry)




                #print(actual_innings)
    parse_data(all_relevant_players)
    return all_relevant_players

    # print(all_entries)
    # for player in all_relevant_players:
    #     print(player.every_relevant_ball)


## Returns a list of players relevant to a match with every ball relevant to every player
## Takes in special ID as input
def one_game_json(unique_id):
    all_relevant_players = []

    all_entries = set()

    json_path = os.path.join(os.path.dirname(__file__), "ipl_json", f"{unique_id}.json")

    with open(json_path) as f:
        data = json.load(f)

        if 'player_of_match' not in data['info']:
            data['info']['player_of_match'] = [""]

        for team in data['info']['players']:
            for player in data['info']['players'][team]:
                check_existence = add_player(player, all_relevant_players)
                check_existence.relevant_meta_info.append(data['info'])

        #name_team_1 = data['innings'][0]['1st innings']['team']
        #name_team_2 = data['innings'][1]['2nd innings']['team']

        ## Iterating over both innings
        for index, innings in enumerate(data['innings']):
            if index >= 2:
                continue


            for over_index, over in enumerate(innings['overs']):

                for delivery_index, delivery in enumerate(over['deliveries']):


                    what_happened = over['deliveries'][delivery_index]
                    what_happened['which_innings'] = index
                    what_happened['teams_playing'] = data['info']['teams']
                    what_happened['unique_id'] = unique_id
                    what_happened['man_of_match'] = data['info']['player_of_match']


                    not_searchable = {'runs',"extras" ,"which_innings" ,"replacements","teams_playing",
                                      "unique_id",'man_of_match'}

                    ## Basically if a ball involves a person we add that ball to that person's relevant balls
                    for entry in what_happened:
                        if entry not in {'bowler', 'batter', 'extras', 'non_striker', 'wickets', 'runs', 'review',
                                         'which_innings', 'replacements','teams_playing','unique_id','man_of_match'}:
                            raise ValueError(f"{entry}")

                        ## In some cases the data fields contain no people
                        if entry in not_searchable:
                            continue
                        if entry == "wickets":
                            for wicket in what_happened[entry]:
                                if 'fielders' in wicket:
                                    for fielder in wicket['fielders']:
                                        if fielder['name'] != what_happened['bowler']:
                                            if ('substitute' in fielder and not fielder['substitute']) or ('substitute' not in fielder):
                                                check_existence = add_player(fielder['name'], all_relevant_players)
                                                check_existence.every_relevant_ball.append(delivery)
                            continue

                        if entry == 'review':
                            continue



                        check_existence = add_player(what_happened[entry], all_relevant_players)

                        check_existence.every_relevant_ball.append(delivery)

                        #print(f"{entry} {what_happened[entry]}")


                        all_entries.add(entry)



                #print(actual_innings)
    parse_data(all_relevant_players)
    return all_relevant_players

    # print(all_entries)
    # for player in all_relevant_players:
    #     print(player.every_relevant_ball)




all_dismissals = set()

all_ids = set()

all_teams = set()

## Setting up all fields
## Each mini-function has access to every ball a particular player has been involved in
def set_up_fields():

    def basic_name(player:Temp_Player, all_other_games=""):
        return player.name
    Name = Field("Name",basic_name,"",False)

    def find_runs(player:Temp_Player):
        total_runs = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['batsman'] == player.name:
                total_runs += ball[ball_notation]['runs']['batsman']

        return total_runs
    runs = Field('Runs',find_runs,0,True)

    def high_score_func(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            return find_runs(player)
        return max(find_runs(player),getattr(all_other_games,"High Score"))
    high_score = Field("High Score", high_score_func, 0, False)

    def balls_faced_func(player:Temp_Player):
        balls_faced = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['batsman'] == player.name:
                balls_faced += 1
        return balls_faced
    balls_faced = Field('Balls Faced', balls_faced_func,0,True)

    def balls_nonstriker_func(player:Temp_Player):
        balls_faced = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['non_striker'] == player.name:
                balls_faced += 1
        return balls_faced
    balls_nonstriker = Field('NonStriker Balls', balls_nonstriker_func,0,True)

    def innings_batted_func(player:Temp_Player):
        unique_ids = set()
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if player.name == ball[ball_notation]['batsman'] or player.name == ball[ball_notation]['non_striker']:
                unique_ids.add(ball[ball_notation]['unique_id'])
        return len(unique_ids)
    innings_batted = Field("Innings", innings_batted_func,0,True)

    def times_got_out_func(player:Temp_Player):
        times_out = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if 'wicket' in ball[ball_notation]:
                if ball[ball_notation]['wicket']['player_out'] == player.name:
                    times_out += 1
                    if ball[ball_notation]['wicket']['kind'] == "retired hurt":
                        times_out -= 1
        return times_out
    times_got_out = Field('Outs', times_got_out_func,0,True,False)

    def average_batting_score(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            temp_outs = times_got_out_func(player)
            if temp_outs == 0:
                return 0
            return round(find_runs(player) / temp_outs,2)


        all_outs = getattr(all_other_games,"Outs")
        if all_outs == 0:
            return 0
        return round(getattr(all_other_games,"Runs") / all_outs,2)
    batting_average = Field("Average", average_batting_score, 0, False)

    def ducks_func(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            if find_runs(player) == 0:
                got_out = False

                for ball in player.every_relevant_ball:
                    ball_notation = list(ball.keys())[0]

                    if 'wicket' in ball[ball_notation]:
                        if ball[ball_notation]['wicket']['player_out'] == player.name:
                            got_out = True
                            break
                if got_out:
                    return 1
            return 0

        this_duck = 0
        if find_runs(player) == 0:
            got_out = False

            for ball in player.every_relevant_ball:
                ball_notation = list(ball.keys())[0]
                if 'wicket' in ball[ball_notation]:
                    if ball[ball_notation]['wicket']['player_out'] == player.name:
                        got_out = True
                        break
            if got_out:
                this_duck += 1
        return getattr(all_other_games,"Ducks") + this_duck
    ducks = Field("Ducks", ducks_func, 0, False, False)

    def number_50s_func(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            if find_runs(player) >= 50:
                return 1
            return 0
        this_fifty = 0
        if find_runs(player) >= 50:
            this_fifty += 1
        return getattr(all_other_games,"50s") + this_fifty
    num_50s = Field("50s", number_50s_func, 0, False)

    def number_100s_func(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            if find_runs(player) >= 100:
                return 1
            return 0
        this_hundred = 0
        if find_runs(player) >= 100:
            this_hundred += 1
        return getattr(all_other_games,"100s") + this_hundred
    num_100s = Field("100s", number_100s_func, 0, False)

    def find_dots(player:Temp_Player):
        total_singles = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['batsman'] == player.name:
                if ball[ball_notation]['runs']['batsman'] == 0:
                    total_singles += 1

        return total_singles
    dots_played = Field("0s", find_dots,0,True)

    def find_singles(player:Temp_Player):
        total_singles = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['batsman'] == player.name:
                if ball[ball_notation]['runs']['batsman'] == 1:
                    total_singles += 1

        return total_singles
    single_runs = Field("1s", find_singles,0,True)

    def find_doubles(player:Temp_Player):
        total_singles = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['batsman'] == player.name:
                if ball[ball_notation]['runs']['batsman'] == 2:
                    total_singles += 1

        return total_singles
    double_runs = Field("2s", find_doubles,0,True)

    def find_triples(player:Temp_Player):
        total_singles = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['batsman'] == player.name:
                if ball[ball_notation]['runs']['batsman'] == 3:
                    total_singles += 1

        return total_singles
    triple_runs = Field("3s", find_triples,0,True)

    def find_fours(player:Temp_Player):
        total_singles = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['batsman'] == player.name:
                if ball[ball_notation]['runs']['batsman'] == 4:
                    total_singles += 1

        return total_singles
    fours = Field("4s", find_fours,0,True)

    def find_fives(player:Temp_Player):
        total_singles = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['batsman'] == player.name:
                if ball[ball_notation]['runs']['batsman'] == 5:
                    total_singles += 1

        return total_singles
    fives = Field("5s", find_fives,0,True)

    def find_sixes(player:Temp_Player):
        total_singles = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['batsman'] == player.name:
                if ball[ball_notation]['runs']['batsman'] == 6:
                    total_singles += 1

        return total_singles
    sixes = Field("6s", find_sixes,0,True)

    def boundary_percentage_func(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            boundaries = 4*find_fours(player) + 6*find_sixes(player)
            temp_runs = find_runs(player)
            if temp_runs == 0:
                return 0
            return 100*round(boundaries / temp_runs,2)

        boundaries = 4*getattr(all_other_games,"4s") + 6*getattr(all_other_games,"6s")
        temp_runs = getattr(all_other_games,"Runs")
        if temp_runs == 0:
            return 0
        return 100*round(boundaries / temp_runs,2)
    bound_percent = Field("Boundary", boundary_percentage_func, 0, False)

    def find_wickets(player:Temp_Player):
        credited_dismissals = ('stumped', 'hit wicket', 'bowled', 'lbw', 'caught and bowled', 'caught')
        total_wickets = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['bowler'] == player.name:
                if 'wicket' in ball[ball_notation]:
                    if ball[ball_notation]['wicket']['kind'] in credited_dismissals:
                        total_wickets += 1
                    all_dismissals.add(ball[ball_notation]['wicket']['kind'])

        return total_wickets
    wickets = Field('Wickets', find_wickets, 0, True)

    def three_wickets_func(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            if find_wickets(player) >= 3:
                return 1
            return 0
        how_many = 0
        if find_wickets(player) >= 3:
            how_many += 1
        return getattr(all_other_games,"3ws") + how_many
    three_wickets = Field("3ws", three_wickets_func, 0, False)

    def five_wickets_func(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            if find_wickets(player) >= 5:
                return 1
            return 0
        how_many = 0
        if find_wickets(player) >= 5:
            how_many += 1
        return getattr(all_other_games,"5ws") + how_many
    five_wickets = Field("5ws", five_wickets_func, 0, False)


    def balls_bowled_func(player:Temp_Player):
        ball_counted = ('legbyes','byes')
        ball_not_counted = ('wides','noballs')

        all_bowled = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['bowler'] == player.name:
                if 'extras' not in ball[ball_notation]:
                    all_bowled += 1
                else:
                    if 'wides' not in ball[ball_notation]['extras'] and 'noballs' not in ball[ball_notation]['extras']:
                        all_bowled += 1
        return all_bowled
    balls_bowled = Field("Balls Bowled", balls_bowled_func, 0, True)

    def dots_bowled_func(player:Temp_Player):
        dots_bowled = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['bowler'] == player.name:
                bowler_runs_given = ball[ball_notation]['runs']['batsman']
                if 'extras' in ball[ball_notation]:
                    if 'wides' in ball[ball_notation]['extras'] or 'noballs' in ball[ball_notation]['extras']:
                        bowler_runs_given += ball[ball_notation]['runs']['extras']
                if bowler_runs_given == 0:
                    dots_bowled += 1
        return dots_bowled
    dots_bowled = Field("Dots Bowled", dots_bowled_func, 0, True)

    def fours_given_func(player:Temp_Player):
        fours_given_cnt = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['bowler'] == player.name:
                bowler_runs_given = ball[ball_notation]['runs']['batsman']
                if bowler_runs_given == 4:
                    fours_given_cnt += 1
        return fours_given_cnt
    fours_given = Field("4s Given", fours_given_func, 0, True, False)

    def sixes_given_func(player:Temp_Player):
        sixes_given_cnt = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['bowler'] == player.name:
                bowler_runs_given = ball[ball_notation]['runs']['batsman']
                if bowler_runs_given == 6:
                    sixes_given_cnt += 1
        return sixes_given_cnt
    sixes_given = Field("6s Given", sixes_given_func, 0, True, False)


    def runs_given_func(player:Temp_Player):
        runs_given_total = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['bowler'] == player.name:
                runs_given_total += ball[ball_notation]['runs']['batsman']
                if 'extras' in ball[ball_notation]:
                    if 'wides' in ball[ball_notation]['extras'] or 'noballs' in ball[ball_notation]['extras']:
                        runs_given_total += ball[ball_notation]['runs']['extras']
        return runs_given_total
    runs_given = Field("Runs Given", runs_given_func, 0, True, False)

    def economy_func(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            temp_balls = balls_bowled_func(player)
            temp_runs_given = runs_given_func(player)
            if temp_balls == 0:
                return 100
            return round(6*temp_runs_given / temp_balls,2)

        temp_balls = getattr(all_other_games,"Balls Bowled")
        temp_runs_given = getattr(all_other_games,"Runs Given")
        if temp_balls == 0:
            return 100
        return round(6*temp_runs_given / temp_balls,2)
    economy = Field("Econ", economy_func, 0, False, False)

    def bowling_average_func(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            temp_wickets = find_wickets(player)
            temp_runs_given = runs_given_func(player)
            if temp_wickets == 0:
                return 1000
            return round(temp_runs_given / temp_wickets,2)

        temp_wickets = getattr(all_other_games,"Wickets")
        temp_runs_given = getattr(all_other_games,"Runs Given")
        if temp_wickets == 0:
            return 1000
        return round(temp_runs_given / temp_wickets,2)
    bowling_average = Field("Bowling Av", bowling_average_func, 0, False, False)

    def extras_bowled_func(player:Temp_Player):
        extras_bowled_total = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['bowler'] == player.name:
                if 'extras' in ball[ball_notation]:
                    if 'wides' in ball[ball_notation]['extras'] or 'noballs' in ball[ball_notation]['extras']:
                        extras_bowled_total += ball[ball_notation]['runs']['extras']
        return extras_bowled_total
    extras_bowled = Field("Extras Bowled", extras_bowled_func, 0, True, False)

    def catches_func(player:Temp_Player):
        all_catches = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if ball[ball_notation]['bowler'] == player.name:
                if 'wicket' in ball[ball_notation]:
                    if ball[ball_notation]['wicket']['kind'] == "caught and bowled":
                        all_catches += 1
                        continue
            if 'wicket' in ball[ball_notation]:
                if ball[ball_notation]['wicket']['kind'] == 'caught':
                    if player.name in ball[ball_notation]['wicket']['fielders']:
                        all_catches += 1

        return all_catches
    catches = Field("Catches", catches_func,0,True)

    def stumpings_func(player:Temp_Player):
        all_stumpings = 0
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            if 'wicket' in ball[ball_notation]:
                if ball[ball_notation]['wicket']['kind'] == 'stumped':
                    if player.name in ball[ball_notation]['wicket']['fielders']:
                        all_stumpings += 1

        return all_stumpings
    stumpings = Field("Stumpings", stumpings_func,0,True)

    def man_of_matches_func(player:Temp_Player):
        won_matches = set()
        for ball in player.every_relevant_ball:
            ball_notation = list(ball.keys())[0]
            all_ids.add(len(ball[ball_notation]['man_of_match']))
            if ball[ball_notation]['man_of_match'][0] == player.name:
                won_matches.add(ball[ball_notation]['unique_id'])

        return len(won_matches)
    man_of_matches = Field("MotM", man_of_matches_func,0,True)

## Setting up all fields
## Each mini-function has access to every ball a particular player has been involved in
def set_up_fields_json():

    def basic_name(player:Temp_Player, all_other_games=""):
        return player.name
    Name = Field("Name",basic_name,"",False)

    def latest_team_func(player:Temp_Player, all_other_games=""):
        last_match = player.relevant_meta_info[-1]
        for team in last_match['players']:
            if player.name in last_match['players'][team]:
                all_teams.add(team)
                return team_converter[team]
    which_team = Field("Team",latest_team_func,"",False)

    def number_teams_func(player:Temp_Player, all_other_games=Temp_Player("")):
        if all_other_games == Temp_Player(""):
            return 1



        all_teams_this_player = set()
        for match in all_other_games.relevant_meta_info:
            for team in match['players']:
                if player.name in match['players'][team]:
                    all_teams_this_player.add(team_converter[team])

        all_teams_this_player.add(latest_team_func(player))
        return len(all_teams_this_player)
    num_teams = Field("No_Teams",number_teams_func,0,False)

    def num_matches(player: Temp_Player):
        return len(player.relevant_meta_info)
    matches = Field("Matches",num_matches,1,True)

    def points_func(player: Temp_Player):
        return find_runs(player) + (25 * find_wickets(player)) + (5 * (catches_func(player) + stumpings_func(player))) + run_out_points_func(player)
    points = Field("Points",points_func,0,True)


    def highest_points_func(player: Temp_Player, all_other_games=Temp_Player("")):
        if all_other_games == Temp_Player(""):
            return points_func(player)
        return max(points_func(player), getattr(all_other_games, "Highest Points"))

    high_score = Field("Highest Points", highest_points_func, 0, False)



    def points_per_match_func(player: Temp_Player, all_other_games=Temp_Player("")):
        if all_other_games == Temp_Player(""):
            return round(points_func(player) / num_matches(player),2)

        return round(getattr(all_other_games,"Points") / getattr(all_other_games,"Matches"),2)
    points_per_match = Field("PPM",points_per_match_func,0,False)

    def find_runs(player:Temp_Player):
        total_runs = 0
        for ball in player.every_relevant_ball:
            if ball['batter'] == player.name:
                total_runs += ball['runs']['batter']

        return total_runs
    runs = Field('Runs',find_runs,0,True)

    def high_score_func(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            return find_runs(player)
        return max(find_runs(player),getattr(all_other_games,"High Score"))
    high_score = Field("High Score", high_score_func, 0, False)

    def balls_faced_func(player:Temp_Player):
        balls_faced = 0
        for ball in player.every_relevant_ball:
            if ball['batter'] == player.name:
                balls_faced += 1
        return balls_faced
    balls_faced = Field('Balls Faced', balls_faced_func,0,True)

    def balls_nonstriker_func(player:Temp_Player):
        balls_faced = 0
        for ball in player.every_relevant_ball:
            if ball['non_striker'] == player.name:
                balls_faced += 1
        return balls_faced
    balls_nonstriker = Field('NonStriker Balls', balls_nonstriker_func,0,True)

    def innings_batted_func(player:Temp_Player):
        unique_ids = set()
        for ball in player.every_relevant_ball:
            if player.name == ball['batter'] or player.name == ball['non_striker']:
                unique_ids.add(ball['unique_id'])
        return len(unique_ids)
    innings_batted = Field("Innings", innings_batted_func,0,True)

    def times_got_out_func(player:Temp_Player):
        times_out = 0
        for ball in player.every_relevant_ball:
            if 'wickets' in ball:
                for wicket in ball['wickets']:


                    if wicket['player_out'] == player.name:
                        times_out += 1
                        if wicket['kind'] == "retired hurt":
                            times_out -= 1
                        if wicket['kind'] == "retired out":
                            times_out -= 1
        return times_out
    times_got_out = Field('Outs', times_got_out_func,0,True,False)

    def average_batting_score(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            temp_outs = times_got_out_func(player)
            if temp_outs == 0:
                return ""
            return round(find_runs(player) / temp_outs,2)


        all_outs = getattr(all_other_games,"Outs")
        if all_outs == 0:
            return ""
        return round(getattr(all_other_games,"Runs") / all_outs,2)
    batting_average = Field("Average", average_batting_score, 0, False)

    def ducks_func(player: Temp_Player, all_other_games = Temp_Player("")):


        if all_other_games == Temp_Player(""):
            if find_runs(player) == 0:
                got_out = False

                for ball in player.every_relevant_ball:


                    if 'wickets' in ball:
                        for wicket in ball['wickets']:
                            if wicket['player_out'] == player.name:
                                got_out = True

                if got_out:
                    return 1
            return 0

        this_duck = 0
        if find_runs(player) == 0:
            got_out = False

            for ball in player.every_relevant_ball:

                if 'wickets' in ball:
                    for wicket in ball['wickets']:
                        if wicket['player_out'] == player.name:
                            got_out = True
            if got_out:
                this_duck += 1
        return getattr(all_other_games,"Ducks") + this_duck
    ducks = Field("Ducks", ducks_func, 0, False, False)

    def number_50s_func(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            if 50 <= find_runs(player) < 100:
                return 1
            return 0
        this_fifty = 0
        if 50 <= find_runs(player) < 100:
            this_fifty += 1
        return getattr(all_other_games,"50s") + this_fifty
    num_50s = Field("50s", number_50s_func, 0, False)

    def number_100s_func(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            if find_runs(player) >= 100:
                return 1
            return 0
        this_hundred = 0
        if find_runs(player) >= 100:
            this_hundred += 1
        return getattr(all_other_games,"100s") + this_hundred
    num_100s = Field("100s", number_100s_func, 0, False)

    def find_dots(player:Temp_Player):
        total_singles = 0
        for ball in player.every_relevant_ball:
            if ball['batter'] == player.name:
                if ball['runs']['batter'] == 0:
                    total_singles += 1

        return total_singles
    dots_played = Field("0s", find_dots,0,True)

    def find_singles(player:Temp_Player):
        total_singles = 0
        for ball in player.every_relevant_ball:
            if ball['batter'] == player.name:
                if ball['runs']['batter'] == 1:
                    total_singles += 1

        return total_singles
    single_runs = Field("1s", find_singles,0,True)

    def find_doubles(player:Temp_Player):
        total_singles = 0
        for ball in player.every_relevant_ball:
            if ball['batter'] == player.name:
                if ball['runs']['batter'] == 2:
                    total_singles += 1

        return total_singles
    double_runs = Field("2s", find_doubles,0,True)

    def find_triples(player:Temp_Player):
        total_singles = 0
        for ball in player.every_relevant_ball:
            if ball['batter'] == player.name:
                if ball['runs']['batter'] == 3:
                    total_singles += 1

        return total_singles
    triple_runs = Field("3s", find_triples,0,True)

    def find_fours(player:Temp_Player):
        total_singles = 0
        for ball in player.every_relevant_ball:
            if ball['batter'] == player.name:
                if ball['runs']['batter'] == 4:
                    total_singles += 1

        return total_singles
    fours = Field("4s", find_fours,0,True)

    def find_fives(player:Temp_Player):
        total_singles = 0
        for ball in player.every_relevant_ball:
            if ball['batter'] == player.name:
                if ball['runs']['batter'] == 5:
                    total_singles += 1

        return total_singles
    fives = Field("5s", find_fives,0,True)

    def find_sixes(player:Temp_Player):
        total_singles = 0
        for ball in player.every_relevant_ball:
            if ball['batter'] == player.name:
                if ball['runs']['batter'] == 6:
                    total_singles += 1

        return total_singles
    sixes = Field("6s", find_sixes,0,True)

    def boundary_percentage_func(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            boundaries = 4*find_fours(player) + 6*find_sixes(player)
            temp_runs = find_runs(player)
            if temp_runs == 0:
                return ""
            return int(100*round(boundaries / temp_runs,2))

        boundaries = 4*getattr(all_other_games,"4s") + 6*getattr(all_other_games,"6s")
        temp_runs = getattr(all_other_games,"Runs")
        if temp_runs == 0:
            return ""
        return int(100*round(boundaries / temp_runs,2))
    bound_percent = Field("Boundary", boundary_percentage_func, 0, False)

    def find_wickets(player:Temp_Player):
        credited_dismissals = ('stumped', 'hit wicket', 'bowled', 'lbw', 'caught and bowled', 'caught')
        total_wickets = 0
        for ball in player.every_relevant_ball:
            if ball['bowler'] == player.name:
                if 'wickets' in ball:
                    for wicket in ball['wickets']:
                        if wicket['kind'] in credited_dismissals:
                            total_wickets += 1
                        all_dismissals.add(wicket['kind'])

        return total_wickets
    wickets = Field('Wickets', find_wickets, 0, True)

    def three_wickets_func(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            if find_wickets(player) >= 3:
                return 1
            return 0
        how_many = 0
        if find_wickets(player) >= 3:
            how_many += 1
        return getattr(all_other_games,"3ws") + how_many
    three_wickets = Field("3ws", three_wickets_func, 0, False)

    def five_wickets_func(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            if find_wickets(player) >= 5:
                return 1
            return 0
        how_many = 0
        if find_wickets(player) >= 5:
            how_many += 1
        return getattr(all_other_games,"5ws") + how_many
    five_wickets = Field("5ws", five_wickets_func, 0, False)

    def balls_bowled_func(player:Temp_Player):
        ball_counted = ('legbyes','byes')
        ball_not_counted = ('wides','noballs')

        all_bowled = 0
        for ball in player.every_relevant_ball:
            if ball['bowler'] == player.name:
                if 'extras' not in ball:
                    all_bowled += 1
                else:
                    if 'wides' not in ball['extras'] and 'noballs' not in ball['extras']:
                        all_bowled += 1
        return all_bowled
    balls_bowled = Field("Balls Bowled", balls_bowled_func, 0, True)

    def dots_bowled_func(player:Temp_Player):
        dots_bowled = 0
        for ball in player.every_relevant_ball:
            if ball['bowler'] == player.name:
                bowler_runs_given = ball['runs']['batter']
                if 'extras' in ball:
                    if 'wides' in ball['extras'] or 'noballs' in ball['extras']:
                        bowler_runs_given += ball['runs']['extras']
                if bowler_runs_given == 0:
                    dots_bowled += 1
        return dots_bowled
    dots_bowled = Field("Dots Bowled", dots_bowled_func, 0, True)

    def fours_given_func(player:Temp_Player):
        fours_given_cnt = 0
        for ball in player.every_relevant_ball:
            if ball['bowler'] == player.name:
                bowler_runs_given = ball['runs']['batter']
                if bowler_runs_given == 4:
                    fours_given_cnt += 1
        return fours_given_cnt
    fours_given = Field("4s Given", fours_given_func, 0, True, False)

    def sixes_given_func(player:Temp_Player):
        sixes_given_cnt = 0
        for ball in player.every_relevant_ball:
            if ball['bowler'] == player.name:
                bowler_runs_given = ball['runs']['batter']
                if bowler_runs_given == 6:
                    sixes_given_cnt += 1
        return sixes_given_cnt
    sixes_given = Field("6s Given", sixes_given_func, 0, True, False)

    def runs_given_func(player:Temp_Player):
        runs_given_total = 0
        for ball in player.every_relevant_ball:
            if ball['bowler'] == player.name:
                runs_given_total += ball['runs']['batter']
                if 'extras' in ball:
                    if 'wides' in ball['extras'] or 'noballs' in ball['extras']:
                        runs_given_total += ball['runs']['extras']
        return runs_given_total
    runs_given = Field("Runs Given", runs_given_func, 0, True, False)

    def economy_func(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            temp_balls = balls_bowled_func(player)
            temp_runs_given = runs_given_func(player)
            if temp_balls == 0:
                return ""
            return round(6*temp_runs_given / temp_balls,2)

        temp_balls = getattr(all_other_games,"Balls Bowled")
        temp_runs_given = getattr(all_other_games,"Runs Given")
        if temp_balls == 0:
            return ""
        return round(6*temp_runs_given / temp_balls,2)
    economy = Field("Econ", economy_func, 0, False, False)

    def bowling_average_func(player: Temp_Player, all_other_games = Temp_Player("")):
        if all_other_games == Temp_Player(""):
            temp_wickets = find_wickets(player)
            temp_runs_given = runs_given_func(player)
            if temp_wickets == 0:
                return ""
            return round(temp_runs_given / temp_wickets,2)

        temp_wickets = getattr(all_other_games,"Wickets")
        temp_runs_given = getattr(all_other_games,"Runs Given")
        if temp_wickets == 0:
            return ""
        return round(temp_runs_given / temp_wickets,2)
    bowling_average = Field("Bowling Av", bowling_average_func, 0, False, False)

    def extras_bowled_func(player:Temp_Player):
        extras_bowled_total = 0
        for ball in player.every_relevant_ball:
            if ball['bowler'] == player.name:
                if 'extras' in ball:
                    if 'wides' in ball['extras'] or 'noballs' in ball['extras']:
                        extras_bowled_total += ball['runs']['extras']
        return extras_bowled_total
    extras_bowled = Field("Extras Bowled", extras_bowled_func, 0, True, False)

    def catches_func(player:Temp_Player):
        all_catches = 0
        for ball in player.every_relevant_ball:
            if ball['bowler'] == player.name:
                if 'wickets' in ball:
                    for wicket in ball['wickets']:
                        if wicket['kind'] == "caught and bowled":
                            all_catches += 1
                    continue
            if 'wickets' in ball:
                for wicket in ball['wickets']:
                    if wicket['kind'] == 'caught':
                        if player.name in [player['name'] for player in wicket['fielders']]:
                            all_catches += 1

        return all_catches
    catches = Field("Catches", catches_func,0,True)

    def run_outs_func(player:Temp_Player):
        all_run_outs = 0
        for ball in player.every_relevant_ball:
            if 'wickets' in ball:
                for wicket in ball['wickets']:
                    if wicket['kind'] == 'run out':
                        if 'fielders' in wicket:
                            if player.name in [player['name'] for player in wicket['fielders']]:
                                all_run_outs += 1

        return all_run_outs
    run_outs = Field("Run_Outs",run_outs_func,0,True)

    def run_out_points_func(player:Temp_Player):
        runout_pts = 0
        for ball in player.every_relevant_ball:
            if 'wickets' in ball:
                for wicket in ball['wickets']:
                    if wicket['kind'] == 'run out':
                        if 'fielders' in wicket:
                            if player.name in [player['name'] for player in wicket['fielders']]:
                                runout_pts += (10 / len(wicket['fielders']))

        return int(runout_pts)
    run_out_pts = Field("Runout_pts",run_out_points_func,0,True)

    def stumpings_func(player:Temp_Player):
        all_stumpings = 0
        for ball in player.every_relevant_ball:
            if 'wickets' in ball:
                for wicket in ball['wickets']:
                    if wicket['kind'] == 'stumped':
                        if player.name in [player['name'] for player in wicket['fielders']]:
                            all_stumpings += 1

        return all_stumpings
    stumpings = Field("Stumpings", stumpings_func,0,True)

    def reviews_as_batsman(player:Temp_Player):
        all_reviews = 0
        for ball in player.every_relevant_ball:
            if 'review' in ball:
                if ball['review']['batter'] == player.name:
                    all_reviews += 1

        return all_reviews
    reviews = Field("Reviews_Bat", reviews_as_batsman, 0, True)

    def matches_won(player:Temp_Player):
        player_team = latest_team_func(player, Temp_Player(""))
        if 'result' in player.relevant_meta_info[-1]['outcome'] and player.relevant_meta_info[-1]['outcome']['result'] == 'no result':
            return 0

        if 'winner' not in player.relevant_meta_info[-1]['outcome']:
            if 'eliminator' in player.relevant_meta_info[-1]['outcome']:
                won_team = player.relevant_meta_info[-1]['outcome']['eliminator']
                if team_converter[won_team] == player_team:
                    return 1
            else:

                print("NO WINNER")
        elif team_converter[player.relevant_meta_info[-1]['outcome']['winner']] == player_team:
            return 1
        return 0
    num_matches_won = Field("Won", matches_won, 0, True)

    def man_of_matches_func(player:Temp_Player):
        won_matches = set()
        for ball in player.every_relevant_ball:
            all_ids.add(len(ball['man_of_match']))
            if ball['man_of_match'][0] == player.name:
                won_matches.add(ball['unique_id'])

        return len(won_matches)
    man_of_matches = Field("MotM", man_of_matches_func,0,True)


def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def write_to_file(all_relevant_players):
    save_object(all_relevant_players,"Statistics.pkl")

def read_from_file():
    try:

        with open("Statistics.pkl", 'rb') as input:
            all_players = pickle.load(input)
            return all_players
    except:
        return False


## Adding new data to database
def combine_stats(players_from_this_match, all_players):

    for current_player in players_from_this_match:
        if current_player.name not in all_players:
            all_players[current_player.name] = current_player
            continue

        to_change: Temp_Player = all_players[current_player.name]
        for field in all_fields:
            if field.core:
                to_add = getattr(current_player, field.name)
                original = getattr(to_change, field.name)

                setattr(to_change, field.name, to_add + original)
        for field in all_fields:
            if not field.core:
                setattr(to_change,field.name,field.calculator(current_player, to_change))

        all_players[current_player.name].relevant_meta_info += current_player.relevant_meta_info

    return all_players


def actually_one_game(unique_id):
    all_players = one_game_json(unique_id)
    #write_to_file(all_players)


    if read_from_file() is not False:

        all_players = combine_stats(all_players,read_from_file())
    else:
        all_players = {player.name:player for player in all_players}

    write_to_file(all_players)

    #print(all_players)


    return all_players

def erase_sheet():
    os.remove("Statistics.pkl")


def temp_view():
    set_up_fields()
    x = read_from_file()
    for player in x:
        print(f'{player} {x[player]}')

def write_to_excel(sheet_name):
    workbook = xlsxwriter.Workbook(sheet_name)
    worksheet = workbook.add_worksheet()
    cell_format = workbook.add_format()
    cell_format.set_align('center')
    cell_format.set_align('vcenter')

    for n, field in enumerate(all_fields):
        worksheet.write(0, n, field.name, cell_format)

    start_row = 1

    all_stats = read_from_file()
    all_stats = [all_stats[player] for player in all_stats]

    for m, field in enumerate(all_fields):
        column_length = max(5, len(str(field.name)))
        for n, player in enumerate(all_stats):
            column_length = max(column_length, len(str(getattr(player,field.name))))
            worksheet.write(start_row + n, m, getattr(player,field.name), cell_format)
        worksheet.set_column(m, m, column_length)

    worksheet.set_default_row(30)
    worksheet.autofilter(0, 0, len(all_stats), len(all_fields) - 1)
    worksheet.freeze_panes(1,1)

    # max_len_names = max([len(player['name']) for player in all_stats])
    # worksheet.set_column(0,0,max_len_names)

    for m, field in enumerate(all_fields):
        if field.big_equals_good == -1:
            continue
        elif field.big_equals_good == 1:
            worksheet.conditional_format(1, m, len(all_stats), m,
                                         {'type': '3_color_scale',
                                          'min_color': "#F8696B",
                                          'mid_color': "#FFEB84",
                                          'max_color': "#63BE7B"
                                          })
        elif field.big_equals_good == 0:
            worksheet.conditional_format(1, m, len(all_stats), m,
                                         {'type': '3_color_scale',
                                          'max_color': "#F8696B",
                                          'mid_color': "#FFEB84",
                                          'min_color': "#63BE7B"
                                          })
        else:
            raise ValueError

    workbook.close()




def extract_match_ids(txt_file_path, years=None):
    match_ids = []
    date_line_pattern = re.compile(r"^\d{4}-\d{2}-\d{2} - ")

    with open(txt_file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()

            # Only proceed if line starts with a valid date
            if not date_line_pattern.match(line):
                continue

            parts = line.split(' - ')
            if len(parts) < 5:
                raise ValueError(f"Line {line_num} has fewer than 5 parts: {line}")

            year = int(parts[0][:4])
            match_id = int(parts[4])

            if years is not None and year not in years:
                continue

            match_ids.append(match_id)

    return match_ids


def main(output_file, years):
    try:
        erase_sheet()
    except:
        pass

    set_up_fields_json()

    all_games = extract_match_ids("ipl_json/README.txt", years=years)

    #all_games = [1359523,1359520]


    for game in all_games:
        print(game)
        actually_one_game(str(game))
    write_to_excel(output_file)


# 'BallByBall_2024.xlsx'

# main()
# print(all_dismissals)
# print(all_ids)
# print(all_teams)
#temp_view()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process IPL match files and output a color-coded Excel sheet."
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default="BallByBall.xlsx",
        help="Name of the Excel file to save the output (default: BallByBall.xlsx). Will overwrite if file exists."
    )

    parser.add_argument(
        "-y", "--years",
        type=str,
        default="2024",
        help=("Comma-separated list of years to process (e.g., '2024,2023'). "
              "If not provided, all years will be processed.")
    )

    args = parser.parse_args()

    # Process the years argument into a list of ints, or use None if empty.
    if args.years:
        years = [int(year.strip()) for year in args.years.split(",")]
    else:
        years = None

    main(output_file=args.output, years=years)



