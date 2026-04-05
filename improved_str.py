def strategy(my_history, opponent_history):
    if len(my_history) == 0:
        return 'C'
    
    last_my = my_history[-1]
    last_op = opponent_history[-1]
    
    if last_op == 'C':
        return 'C'
    
    if last_my == 'D':
        return 'C'
    
    # If opponent defects repeatedly → stop forgiving
    if len(opponent_history) >= 2 and opponent_history[-2] == 'D':
        return 'D'
    
    return 'D'