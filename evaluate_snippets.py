import json
import signal
from contextlib import contextmanager

from flasgger import Swagger
from flask import Flask, request

from pymaze import Maze

app = Flask(__name__)
Swagger(app)


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise (TimeoutException("Timed out!"))

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


@app.route('/evaluate', methods=['POST'])
def evaluate():
    """
    Micro Service Based Maze Evaluator
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: data
          properties:
            maze:
              type: array
              items:
                type: array
                items: int
            snippet:
              type: string
        
    responses:
      200:
        description: Evaluated step count
    """
    with time_limit(5):
        # Run snippet code against maze
        maze = Maze(request.json.get('maze'))

        try:
            exec request.json.get('snippet')
        except Exception as e:
            print(e.message)  # Catch all exceptions

        # Get step count
        steps = len(maze.get_history()) - 1 if maze.is_maze_solved() else 0
        return json.dumps({'steps': steps}), 200


app.run(host='0.0.0.0', debug=False)
