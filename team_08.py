def strategy(my_history, opponent_history):
    if len(my_history) == 0:
        return 'C'
    
    last_my = my_history[-1]
    last_op = opponent_history[-1]
    
    # If opponent cooperated, reset and cooperate
    if last_op == 'C':
        return 'C'
    
    # Opponent defected
    # If we also defected last round -> our fault -> be contrite
    if last_my == 'D':
        return 'C'
    
    # Otherwise punish
    return 'D'