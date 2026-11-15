# parcial4-logica

![diagrama de la máquina de turing](image.png)

Para ver la máquina en funcionamiento utilicen la página [turingmachine.io](https://turingmachine.io/)  y peguen esto :)

input: '0011' 
blank: ' '
start state: q1

table:

  q1:
    0: {write: x, R: q2}
    1: {R: q5}
    x: {R: qreject}
    y: {R: q4}
    ' ': {R: qreject}

  q2:
    [0,y]: R
    1: {write: y, L: q3}
    [x,' ']: {R: qreject}

  q3:
    [0,y]: L
    x: {R: q1}
    [1,' ']: {R: qreject}

  q4:
    y: R
    ' ': {R: qaccept}
    [0,1,x]: {R: qreject}

  q5:
    [0,1,x,y,' ']: {L: q6}

  q6:
    [0,1,x,y,' ']: {R: q5}

  qaccept:
  
  qreject:
