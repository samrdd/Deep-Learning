import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import requests
import re
import itertools

# # Ensure these NLTK resources are downloaded
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('stopwords')

# Function for text analysis
def analyze_text(sentence):
    tokens = word_tokenize(sentence)
    tagged_tokens = nltk.pos_tag(tokens)
    stop_words = set(stopwords.words('english'))
    keywords = [word for word, tag in tagged_tokens if tag.startswith('NN') and word.lower() not in stop_words]
    return keywords

# Function to fetch match details for soccer or football, basketball, tennis, hockey
def fetch_general_sport_match_details(game):
    # Fetch match details
    url = "https://livescore6.p.rapidapi.com/matches/v2/list-live"
    querystring = {"Category": game, "Timezone": "-7"}
    headers = {
        "X-RapidAPI-Key": "4ea381b0c5msh7bb9401b76de8efp16bc49jsn7976f053a79b",
        "X-RapidAPI-Host": "livescore6.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    json_data = response.json()

    matches = []
    for stage in json_data['Stages']:
        for event in stage.get('Events', []):
            match_info = {
                'League': stage['Snm'],
                'Match': f"{event['T1'][0]['Nm']} vs. {event['T2'][0]['Nm']}"
            }
            matches.append(match_info)

    # Format matches with hashtags
    formatted_matches = []
    for match in matches:
        # Format the match and league hashtag
        match_hashtag = f"{match['Match'].replace(' ', '').replace('vs.', 'Vs')}"
        league_hashtag = f"#{match['League'].replace(' ', '')}"
        
        # Combine match details with hashtags
        formatted_match = f"{match_hashtag} {league_hashtag}"
        formatted_matches.append(formatted_match)

    return formatted_matches

# Function to fetch match details for cricket
def fetch_cricket_match_details():
    # Fetch cricket match details
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
    headers = {
        "X-RapidAPI-Key": "4ea381b0c5msh7bb9401b76de8efp16bc49jsn7976f053a79b",
        "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    json_data = response.json()

    # Extract specific type matches
    allowed_types = ['International', 'League']
    matches = [
        {
            'SeriesName': match['matchInfo']['seriesName'],
            'STeams': f"{match['matchInfo']['team1']['teamSName']}Vs{match['matchInfo']['team2']['teamSName']}",
            'StateTitle': match['matchInfo']['stateTitle'],
            'Status': match['matchInfo']['status'],
            'Teams': f"{match['matchInfo']['team1']['teamName']}Vs{match['matchInfo']['team2']['teamName']}",
            'MatchDesc': match['matchInfo']['matchDesc'],
            'MatchFormat': match['matchInfo']['matchFormat'],
            'Ground': match['matchInfo']['venueInfo']['ground']
        }
        for type_match in json_data['typeMatches']
        if type_match.get('matchType') in allowed_types
        for series_match in type_match.get('seriesMatches', [])
        for match in series_match.get('seriesAdWrapper', {}).get('matches', [])
    ]

    # Format values and match details
    formatted_match_lists = [format_values(match) for match in matches]
    #formatted_matches = [' '.join(f"#{value}" for value in match.values()) for match in formatted_match_lists]

    return format_match_details(formatted_match_lists)

def format_match_details(matches):
    formatted_matches = []
    for match in matches:
        match_values = list(match.values())
        formatted_match = ' '.join([f"#{value}" if i != 0 else value for i, value in enumerate(match_values)])
        formatted_matches.append(formatted_match)
    return formatted_matches

def format_values(data):
    return {
        key: re.sub(r"[ ,.-]", "", value).title() if key != 'STeams' else value
        for key, value in data.items()
    }


def process_sentence_and_get_hashtags(hashtags, sentence):
    sports_keywords = ["soccer", "basketball", "tennis", "hockey", "cricket", 'cricketer', 'wicket', 'batting', 'football']
    found_sports = analyze_text(sentence)
    hashtags = [tag.lower() for tag in hashtags]
    found_sports.extend(hashtags)
    # Check for each sport and call the respective function
    for sport in sports_keywords:
        if sport in found_sports:
            if sport in ["cricket", 'cricketer', 'wicket', 'batting']:
                return fetch_cricket_match_details()
            if sport in sports_keywords and sport not in ["cricket", 'cricketer', 'wicket', 'batting']:
              if sport == 'football':
                sport = 'soccer'
                return fetch_general_sport_match_details(sport)
              return fetch_general_sport_match_details(sport)

# Example usage
# sentence = "soccer"
# hashtags = process_sentence_and_get_hashtags(sentence)

# def getHastags(sentence):
#    process_sentence_and_get_hashtags(sentence)
