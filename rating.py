import json
import os
from datetime import datetime
from collections import defaultdict

#time decay for the K-value based on the match date
def date_difference_in_days(match_date):
    """Calculate the number of days since the match based on its date."""
    current_date = datetime.now()
    match_date = datetime.strptime(match_date, "%Y-%m-%d")
    return (current_date - match_date).days

def calculate_k_based_on_time(k_value, match_date):
    """Adjust the K-value based on how many days have passed since the match."""
    days_since_match = date_difference_in_days(match_date)
    #increases the K-value by 20% per 365 days
    decay_factor = 1 - (days_since_match / 365) * 1.20
    return k_value * decay_factor if decay_factor > 0 else k_value

#dominance factor based on rounds won/lost
def calculate_dominance_factor(winner_rounds, loser_rounds):
    """Calculate the dominance factor based on rounds won and lost."""
    if winner_rounds + loser_rounds == 0:
        return 0  
    return 0.5 + 0.5 * (winner_rounds - loser_rounds) / (winner_rounds + loser_rounds)

def load_ratings():
    if os.path.exists("ratings.json"):
        with open("ratings.json", "r") as f:
            return json.load(f)
    return {}

def save_ratings(ratings):
    with open("ratings.json", "w") as f:
        json.dump(ratings, f, indent=2)

def update_ratings(match, ratings, k_value=32):
    winner = match['winner']
    loser = match['loser']
    winner_arm = match['arm']  
    loser_arm = match['arm']  

    winner_rounds = match['winner_rounds']
    loser_rounds = match['loser_rounds']

    if not isinstance(ratings, dict):
        ratings = {}

    #default rating 1500
    winner_rating = ratings.get(winner, {}).get(winner_arm, 1500)
    loser_rating = ratings.get(loser, {}).get(loser_arm, 1500)

    if not isinstance(winner_rating, (int, float)):
        winner_rating = 1500  
    if not isinstance(loser_rating, (int, float)):
        loser_rating = 1500 

    # adjusted K-value based on match date
    adjusted_k = calculate_k_based_on_time(k_value, match['date'])

    #expected score calculation for both players
    expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner_rating - loser_rating) / 400))

    #dominance factor calculation
    dominance_factor = calculate_dominance_factor(winner_rounds, loser_rounds)

    if winner not in ratings:
        ratings[winner] = {"left": 1500, "right": 1500}
    if loser not in ratings:
        ratings[loser] = {"left": 1500, "right": 1500}

    #ratings update
    ratings[winner][winner_arm] = winner_rating + adjusted_k * dominance_factor * (1 - expected_winner)
    ratings[loser][loser_arm] = loser_rating + adjusted_k * dominance_factor * (0 - expected_loser)

    return ratings

def count_supermatches(wrestlers_data):
    """Count the number of supermatches for each wrestler based on how many times they appear in the matches."""
    supermatch_counts = defaultdict(int) 

    for supermatch in wrestlers_data:
        winner = supermatch["winner"]
        loser = supermatch["loser"]
        
        supermatch_counts[winner] += 1
        supermatch_counts[loser] += 1

    return supermatch_counts

def process_matches():
    """Process all the matches and update ratings accordingly."""
    with open("wrestlers.json", "r") as f:
        wrestlers_data = json.load(f)

    supermatch_counts = count_supermatches(wrestlers_data)

    ratings = load_ratings()

    for match in wrestlers_data:
        ratings = update_ratings(match, ratings)

    # Save the updated ratings back to ratings.json
    save_ratings(ratings)

    matches_count = defaultdict(lambda: defaultdict(int))  
    for match in wrestlers_data:
        winner = match['winner']
        loser = match['loser']
        arm = match['arm']
        matches_count[winner][arm] += 1
        matches_count[loser][arm] += 1

    print("Matches count per arm for each wrestler:")
    print(json.dumps(matches_count, indent=2))

def generate_match_counts(wrestlers_file='wrestlers.json', output_file='match_counts.json'):
    match_counts = defaultdict(lambda: {'left': 0, 'right': 0})

    try:
        with open(wrestlers_file, 'r') as f:
            matches = json.load(f)

        for match in matches:
            arm = match.get('arm')
            winner = match.get('winner')
            loser = match.get('loser')

            if arm in ['left', 'right']:
                if winner:
                    match_counts[winner][arm] += 1
                if loser:
                    match_counts[loser][arm] += 1


        match_counts = dict(match_counts)

        with open(output_file, 'w') as f:
            json.dump(match_counts, f, indent=2)

        print(f"Match counts successfully written to {output_file}")

    except FileNotFoundError:
        print(f"Error: {wrestlers_file} not found.")
    except json.JSONDecodeError:
        print(f"Error: {wrestlers_file} contains invalid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

generate_match_counts()

process_matches()
