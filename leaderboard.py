import json

def load_ratings():
    try:
        with open("ratings.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("ratings.json file not found.")
        return {}

def load_match_counts():
    try:
        with open("match_counts.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("match_counts.json file not found.")
        return {}

def sort_ratings(ratings, match_counts):
    sorted_ratings = {
        "left": [],
        "right": []
    }

    for wrestler, arms in ratings.items():
        for arm, rating in arms.items():
            if arm in ["left", "right"] and isinstance(rating, (int, float)):
                matches = match_counts.get(wrestler, {}).get(arm, 0)

                if matches >= 3 and rating > 1400 and rating != 1500:
                    sorted_ratings[arm].append((wrestler, rating))
                else:
                    print(f"Excluded {wrestler} ({arm}) - Matches: {matches}, Rating: {rating}")
            else:
                print(f"Invalid rating for {wrestler} ({arm}): {rating}")

    sorted_ratings["left"].sort(key=lambda x: x[1], reverse=True)
    sorted_ratings["right"].sort(key=lambda x: x[1], reverse=True)

    return sorted_ratings

def save_sorted_ratings(sorted_ratings, filename="leaderboard.json"):
    try:
        with open(filename, "w") as f:
            json.dump(sorted_ratings, f, indent=2)
        print(f"Sorted ratings saved to {filename}")
    except Exception as e:
        print(f"Error saving file: {e}")

def print_sorted_ratings(sorted_ratings):
    print("Sorted Ratings (Left Arm):")
    for wrestler, rating in sorted_ratings["left"]:
        print(f"{wrestler}: {rating}")

    print("\nSorted Ratings (Right Arm):")
    for wrestler, rating in sorted_ratings["right"]:
        print(f"{wrestler}: {rating}")

def main():
    ratings = load_ratings()
    match_counts = load_match_counts()

    if ratings and match_counts:
        sorted_ratings = sort_ratings(ratings, match_counts)
        save_sorted_ratings(sorted_ratings, filename="leaderboard.json")
        print_sorted_ratings(sorted_ratings)
    else:
        print("Missing data to generate leaderboard.")

if __name__ == "__main__":
    main()
