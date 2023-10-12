# flaskgame

1. **Start the Game**:

   - For an aggressive opponent:
     ```bash
     curl -c cookies.txt -X POST -H "Content-Type: application/json" -d '{"opponent_type": "A"}' http://localhost:5000/start | jq .
     ```
   - For an acquisitive opponent:
     ```bash
     curl -c cookies.txt -X POST -H "Content-Type: application/json" -d '{"opponent_type": "Q"}' http://localhost:5000/start | jq .
     ```

2. **Play a Turn**:

   - Play all cards:
     ```bash
     curl -b cookies.txt -X POST -H "Content-Type: application/json" -d '{"action": "play_all"}' http://localhost:5000/play_turn | jq .
     ```
   - Play a specific card (e.g., the card at index 1):
     ```bash
     curl -b cookies.txt -X POST -H "Content-Type: application/json" -d '{"action": "play_that_card", "card_index": 1}' http://localhost:5000/play_turn | jq .
     ```
   - Buy a card from the central active cards (e.g., the card at index 2):
     ```bash
     curl -b cookies.txt -X POST -H "Content-Type: application/json" -d '{"action": "buy_card", "card_index": 2}' http://localhost:5000/play_turn | jq .
     ```
   - Attack the computer:
     ```bash
     curl -b cookies.txt -X POST -H "Content-Type: application/json" -d '{"action": "attack"}' http://localhost:5000/play_turn | jq .
     ```
   - End the turn:
     ```bash
     curl -b cookies.txt -X POST -H "Content-Type: application/json" -d '{"action": "end_turn"}' http://localhost:5000/play_turn | jq .
     ```

3. **Get the Game Status**:
   ```bash
   curl -b cookies.txt -X GET http://localhost:5000/status | jq .
   ```
