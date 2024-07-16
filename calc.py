import json
from tabulate import tabulate

# Load the JSON data
with open('facts.json', 'r') as file:
    facts = json.load(file)

with open('guesses.json', 'r') as file:
    guesses = json.load(file)

guesses = guesses["guesses"]

def groupMatches(matches):
    gMFacts = facts["groupMatches"]
    gMPoints = 0
    for match in matches:
        name = match["name"]
        matchFact = gMFacts[name]
        if match["res"] == matchFact["res"]:
            gMPoints += 10
        if (match["score"]["h"] == matchFact["score"]["h"]) and (match["score"]["a"] == matchFact["score"]["a"]):
            gMPoints += 5
    return gMPoints

def questions(questions):
    qPoints = 0
    for question, answer in questions.items():
        if answer["answer"] in facts["questions"][question]["answer"]:
            qPoints += facts["questions"][question]["points"]
    return qPoints

def leaderGuess(guess, guesser):
    if guess == guesser:
        if guess in facts["leaderGuess"]:
            return 30
        else:
            return -10
    elif guess in facts["leaderGuess"]:
        return 15
    return 0

def advancing(advancing):
    aPoints = 0
    for round, teams in advancing.items():
        for team in teams:
            if team in facts["advancing"][round]["teams"]:
                aPoints += facts["advancing"][round]["points"]
    return aPoints

def team(teamGuess):
    tPoints = 0
    for player in teamGuess:
        if player in facts["team"]:
            tPoints += 20
    return tPoints

def calculate_score(guess):
    name = guess["name"]
    score = 0
    score += groupMatches(guess["groupMatches"])
    score += questions(guess["questions"])
    score += leaderGuess(guess["leaderGuess"], name)
    score += advancing(guess["advancing"])
    score += team(guess["team"])
    return (name, score)

def calculate_table():
    table = []
    gpt_entry = None
    for guess in guesses:
        name, score = calculate_score(guess)
        if name == "GPT":
            gpt_entry = (name, score)
        else:
            table.append((name, score))
    
    # Sort the table by score in descending order
    sorted_table = sorted(table, key=lambda x: x[1], reverse=True)

    # Create a list to hold the formatted table with placements
    formatted_table = []
    current_rank = 1
    for i, (name, score) in enumerate(sorted_table):
        if i > 0 and score == sorted_table[i - 1][1]:
            # If the score is the same as the previous, use the same rank
            rank = current_rank
        else:
            # Otherwise, update the rank to the current position + 1
            rank = i + 1
            current_rank = rank
        formatted_table.append((rank, name, score))
    
    # Insert the GPT entry if it exists
    if gpt_entry:
        gpt_rank = next((rank for rank, name, score in formatted_table if score <= gpt_entry[1]), current_rank)
        gpt_entry_formatted = ("-", f"\033[90m{gpt_entry[0]}\033[0m", gpt_entry[1])
        formatted_table.insert(gpt_rank - 1, gpt_entry_formatted)

    # Print the table
    print(tabulate(formatted_table, headers=["Placement", "Name", "Points"], tablefmt="pretty"))


def winner_guesses_table_sorted():
    # Calculate the current standings
    standings = []
    for guess in guesses:
        name, score = calculate_score(guess)
        standings.append((name, score))
    
    # Sort the standings by score in descending order
    sorted_standings = sorted(standings, key=lambda x: x[1], reverse=True)
    
    # Create a dictionary to map names to their rank
    rank_map = {name: rank + 1 for rank, (name, score) in enumerate(sorted_standings)}
    
    # Create a list to hold the formatted table data
    table_data = []
    
    for guess in guesses:
        name = guess["name"]
        finalist_guess = guess["advancing"]["final"]
        winner_guess = guess["advancing"]["winner"][0]
        table_data.append((rank_map[name], name, finalist_guess[0] + " - " + finalist_guess[1], winner_guess))
    
    # Sort the table data by rank
    sorted_table_data = sorted(table_data, key=lambda x: x[0])
    
    # Prepare the final table without the rank
    final_table_data = [(name, finalists, winner) for _, name, finalists, winner in sorted_table_data]
    
    # Print the table
    print(tabulate(final_table_data, headers=["Player", "Finalists Guess", "Winner Guess"], tablefmt="pretty"))




# Tests

# Test that a theoretical perfect guess gets max score
def test_perfect():
    with open('perfect.json', 'r') as file:
        perfect = json.load(file)
    #return perfect
    return (calculate_score(perfect)[0], calculate_score(perfect)[1] + 15)

# Test that all advancing teams in guess are unique
def test_advancing_unique():
    for guess in guesses:
        for round, teams in guess["advancing"].items():
            if len(teams) != len(set(teams)):
                return False
    return True

# Test that all guesses for advancing teams are at most of correct length
def test_advancing_length():
    for guess in guesses:
        for round, teams in guess["advancing"].items():
            if len(teams) > len(facts["advancing"][round]["teams"]):
                return (False, guess["name"], round, teams)
    return True


calculate_table()
#winner_guesses_table_sorted()

print("test perfect:", test_perfect())
#print("test advancing unique:", test_advancing_unique())
#print("test advancing length:", test_advancing_length())