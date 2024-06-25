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
        if answer in facts["questions"][question]["answer"]:
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

def calculate_score(guess):
    name = guess["name"]
    score = 0
    score += groupMatches(guess["groupMatches"])
    #score += questions(guess["questions"])
    #score += leaderGuess(guess["leaderGuess"], name)
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

calculate_table()