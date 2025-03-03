from flask import Flask, jsonify
from flask_cors import CORS
import requests
from dateutil.parser import parse
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://cricsage-frontend.vercel.app"}})

API_KEY = 'b690e822-d7f3-44e8-9935-87db2ce55d96'
BASE_URL = "https://api.cricapi.com/v1"

# Predefined series IDs
SERIES_IDS = {
    'CHAMPIONS_TROPHY': '49fc7a37-da67-435e-bf5f-00da233e9ff4',
    'WPL': 'bedf8bb2-7a5b-4812-bd50-2ce0a468ffb9'
}

@app.route('/api/matches', methods=['GET'])
def get_upcoming_matches():
    try:
        all_matches = []
        
        for series_id in SERIES_IDS.values():
            response = requests.get(f"{BASE_URL}/series_info?apikey={API_KEY}&id={series_id}")
            if response.status_code == 200:
                series_data = response.json().get('data', {})
                matches = series_data.get('matchList', [])
                
                for match in matches:
                    try:
                        # Include matches that are either upcoming or ongoing
                        match_status = match.get('status', '').lower()
                        is_completed = match.get('matchEnded', False)
                        is_live = 'live' in match_status or 'ongoing' in match_status
                        
                        if not is_completed or is_live:
                            all_matches.append({
                                "id": match['id'],
                                "teams": match.get('teams', []),
                                "venue": match.get('venue', 'Unknown Venue'),
                                "date": match.get('date'),
                                "status": match_status,
                                "isLive": is_live
                            })
                    except Exception as e:
                        print(f"Match processing error: {str(e)}")
                        continue

        return jsonify(sorted(all_matches, 
            key=lambda x: (x['isLive'], x['date']), 
            reverse=True))
    except Exception as e:
        print(f"Error in matches endpoint: {str(e)}")
        return jsonify([])

@app.route('/api/predict/<match_id>', methods=['GET'])
def predict_match(match_id):
    try:
        # Get match details for teams and venue
        match_response = requests.get(f"{BASE_URL}/match_info?apikey={API_KEY}&id={match_id}")
        match = match_response.json().get('data', {}) if match_response.status_code == 200 else {}
        teams = match.get('teams', [])
        venue = match.get('venue', 'Unknown Venue')

        # Generate fake predictions based on teams
        if 'India' in teams and 'Australia' in teams:
            # Champions Trophy Semi-Final
            return jsonify({
                'prediction': {
                    'teams': teams,
                    'venue': venue,
                    'status': 'Upcoming',
                    'isLive': False,
                    'scorePrediction': '295-325',
                    'winProbability': {'India': '62%', 'Australia': '38%'},
                    'keyPlayers': [
                        {'name': 'Shreyas Iyer', 'role': 'Batsman', 'performanceScore': 92.5},
                        {'name': 'Varun Chakravarthy', 'role': 'Bowler', 'performanceScore': 88.3},
                        {'name': 'Travis Head', 'role': 'Batsman', 'performanceScore': 85.7}
                    ]
                }
            })
        elif any(team in ['Mumbai Indians', 'Delhi Capitals', 'Royal Challengers Bangalore'] for team in teams):
            # WPL 2025 Match
            return jsonify({
                'prediction': {
                    'teams': teams,
                    'venue': venue,
                    'status': 'Upcoming',
                    'isLive': False,
                    'scorePrediction': '165-190',
                    'winProbability': {teams[0]: '55%', teams[1]: '45%'},
                    'keyPlayers': [
                        {'name': 'Smriti Mandhana', 'role': 'Batsman', 'performanceScore': 89.1},
                        {'name': 'Ellyse Perry', 'role': 'All-rounder', 'performanceScore': 87.4},
                        {'name': 'Shafali Verma', 'role': 'Batsman', 'performanceScore': 84.6}
                    ]
                }
            })
        else:
            # Generic prediction
            return jsonify({
                'prediction': {
                    'teams': teams,
                    'venue': venue,
                    'status': 'Upcoming',
                    'isLive': False,
                    'scorePrediction': '270-310',
                    'winProbability': {teams[0]: '50%', teams[1]: '50%'},
                    'keyPlayers': [
                        {'name': 'Player 1', 'role': 'Batsman', 'performanceScore': 85.0},
                        {'name': 'Player 2', 'role': 'Bowler', 'performanceScore': 82.5}
                    ]
                }
            })

    except Exception as e:
        return jsonify({
            'prediction': {
                'teams': ['Team A', 'Team B'],
                'venue': 'Unknown Venue',
                'status': 'Upcoming',
                'isLive': False,
                'scorePrediction': '250-290',
                'winProbability': {'Team A': '55%', 'Team B': '45%'},
                'keyPlayers': [
                    {'name': 'Sample Player 1', 'role': 'All-rounder', 'performanceScore': 88.0},
                    {'name': 'Sample Player 2', 'role': 'Bowler', 'performanceScore': 84.5}
                ]
            }
        })
@app.route('/health')
def health_check():
    return jsonify({"status": "ok"})
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
