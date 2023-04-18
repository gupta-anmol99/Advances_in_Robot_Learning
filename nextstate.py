from state_info import get_state,take_random_action

def get_reward_next_state(action):

    #get reward value for the current action

    get_reward()

    #move the gun to a new position and get the information of the new position 
    newstate = get_state()
    goal_achieved = True #get it also from reward
    return newstate, reward, goal_achieved
