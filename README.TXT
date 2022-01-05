Author: Siddharth Shah

The python files within this directory implement an othello AI to suggest
the subsequent move given a board (string representation with 'x' and 'o')
as sys.argv input. The AI employs a positional weighting heuristic and mid-game
negamax to suggest the most optimal move from the given information. The code
is designed to suggest one move at a time and the code below suggests the first
move for 'x' given a starting othello board ("."*27+"ox......xo"+"."*27).

"python othello9B.py"