# FlaskGame - Card Duel

FlaskGame is a card-based duel game where you can challenge a computer opponent in an aggressive or acquisitive mode. The game is built using Flask and provides a RESTful API for game interactions.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Running the Game](#running-the-game)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

- Python 3.9
- Docker (optional for containerized deployment)
- `curl` and `jq` for API interactions

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/kpachhai/flaskgame.git
   cd flaskgame
   ```

2. Set up the environment and dependencies:

   ```bash
   ./setup.sh
   ```

## Running the Game

You can run the game in two modes: using a virtual environment or using Docker.

- **Virtual Environment**:

  ```bash
  ./run.sh venv
  ```

- **Docker**:

  ```bash
  ./run.sh docker
  ```

Once the game is running, you can interact with it using the API endpoints described below.

## API Endpoints

You can interact with FlaskGame's API using various methods. Below are examples using `curl` commands, as well as integration guides for frontend and backend applications.

### Using `curl`

#### Start the Game

- **Aggressive Opponent**:

  ```bash
  curl -c cookies.txt -X POST -H "Content-Type: application/json" -d '{"opponent_type": "A"}' http://localhost:5000/start | jq .
  ```

  or

  ```bash
  curl -c cookies.txt -X POST -H "Content-Type: application/json" -d '{"opponent_type": "aggressive"}' http://localhost:5000/start | jq .
  ```

- **Acquisitive Opponent**:

  ```bash
  curl -c cookies.txt -X POST -H "Content-Type: application/json" -d '{"opponent_type": "Q"}' http://localhost:5000/start | jq .
  ```

  **NOTE**: If you pass in any other option other than "A" or "Aggressive" for "opponent_type", it'll default to an acquisative opponent.

#### Play a Turn

- **Play All Cards**:

  ```bash
  curl -b cookies.txt -X POST -H "Content-Type: application/json" -d '{"action": "play_all"}' http://localhost:5000/play_turn | jq .
  ```

  or

  ```bash
  curl -b cookies.txt -X POST -H "Content-Type: application/json" -d '{"action": "P"}' http://localhost:5000/play_turn | jq .
  ```

- **Play a Specific Card** (e.g., card at index 1):

  ```bash
  curl -b cookies.txt -X POST -H "Content-Type: application/json" -d '{"action": "play_that_card", "card_index": 1}' http://localhost:5000/play_turn | jq .
  ```

  or

  ```bash
  curl -b cookies.txt -X POST -H "Content-Type: application/json" -d '{"action": "C", "card_index": 1}' http://localhost:5000/play_turn | jq .
  ```

- **Buy a Card** from the central active cards (e.g., card at index 2):

  ```bash
  curl -b cookies.txt -X POST -H "Content-Type: application/json" -d '{"action": "buy_card", "card_index": 2}' http://localhost:5000/play_turn | jq .
  ```

  or

  ```bash
  curl -b cookies.txt -X POST -H "Content-Type: application/json" -d '{"action": "B", "card_index": 2}' http://localhost:5000/play_turn | jq .
  ```

- **Attack the Computer**:

  ```bash
  curl -b cookies.txt -X POST -H "Content-Type: application/json" -d '{"action": "attack"}' http://localhost:5000/play_turn | jq .
  ```

  or

  ```bash
  curl -b cookies.txt -X POST -H "Content-Type: application/json" -d '{"action": "A"}' http://localhost:5000/play_turn | jq .
  ```

- **End the Turn**:

  ```bash
  curl -b cookies.txt -X POST -H "Content-Type: application/json" -d '{"action": "end_turn"}' http://localhost:5000/play_turn | jq .
  ```

  or

  ```bash
  curl -b cookies.txt -X POST -H "Content-Type: application/json" -d '{"action": "E"}' http://localhost:5000/play_turn | jq .
  ```

#### Get the Game Status

```bash
curl -b cookies.txt -X GET http://localhost:5000/status | jq .
```

### Frontend Integration

#### Using JavaScript Fetch API

The Fetch API provides a JavaScript interface for accessing and manipulating parts of the HTTP pipeline.

Example to start a game with an aggressive opponent:

```javascript
const startGame = async (opponentType) => {
  const response = await fetch('http://localhost:5000/start', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ opponent_type: opponentType })
  })

  const data = await response.json()
  return data
}

// Usage
startGame('aggressive').then((data) => console.log(data))
```

#### Using Axios

Axios is a popular JavaScript library for making HTTP requests.

Example to start a game with an aggressive opponent:

```javascript
const axios = require('axios')

const startGame = async (opponentType) => {
  const response = await axios.post('http://localhost:5000/start', {
    opponent_type: opponentType
  })

  return response.data
}

// Usage
startGame('A').then((data) => console.log(data))
```

### Backend Integration

#### Using Python's Requests Library

Python's Requests library is a popular choice for making HTTP requests.

Example to start a game with an acquisative opponent:

```python
import requests

def start_game(opponent_type):
    response = requests.post('http://localhost:5000/start', json={
        'opponent_type': opponent_type
    })

    return response.json()

# Usage
data = start_game('acquisative')
print(data)
```

#### Using Node.js with Axios

If your backend is written in Node.js, you can use Axios.

Example to start a game with an acquisative opponent:

```javascript
const axios = require('axios')

const startGame = async (opponentType) => {
  const response = await axios.post('http://localhost:5000/start', {
    opponent_type: opponentType
  })

  return response.data
}

// Usage
startGame('Q').then((data) => console.log(data))
```

### Handling Cookies

The FlaskGame API uses cookies to maintain game state. When integrating, ensure that you handle cookies appropriately. For instance, with Axios, you can use the `withCredentials` option to send and receive cookies:

```javascript
axios.post(
  'http://localhost:5000/start',
  {
    opponent_type: 'A'
  },
  {
    withCredentials: true
  }
)
```

## Testing

To run tests:

```bash
./run.sh test
```

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) to get started.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
