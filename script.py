import random
import math

def main():
    GAME_END_POINTS = 100
    COMPUTER_HOLD = 10
    is_user_turn = True
    user_total = take_turn(True,COMPUTER_HOLD)
    computer_total = take_turn(False,COMPUTER_HOLD)

def print_current_player(is_user_turn):
    if is_user_turn == True:
        print "-----------------------------\n" + "It is now the human's turn"
    elif is_user_turn == False:
        print "-----------------------------\n" + "It is now the computer's turn"

def roll_die():
    number = random.randint(1,6)
    return number

def take_turn(is_user_turn, COMPUTER_HOLD):
    human_score = 0
    computer_score = 0
    if is_user_turn == True:
        human_rand = roll_die()
        while human_rand != 1:
            human_score = human_score + human_rand
            if human_score != 0:
                human_score = str(human_score)
                print("Current Score: " + human_score)
                human_score = int(human_score)
                again = raw_input("roll again? [yn]")
                if again == 'y':
                    human_rand = roll_die()
                    continue
                elif again == 'n':
                    is_user_turn == False
                    break
            else:
                human_score = 1
                print("You rolled a 1. Turn over.")
                return human_score
        if human_rand == 1:
            print("You rolled a 1. Turn over.")
            human_score = 1
            human_score = str(human_score)
            print("Current Score: " + human_score)
            human_score = int(human_score)
            return human_score
        else:
            return human_score
    elif is_user_turn == False:
        computer_rand = roll_die()
        while computer_rand != 1:
            computer_score = computer_score + computer_rand
            if computer_score != 0:
                if computer_score <= COMPUTER_HOLD:
                    computer_rand = roll_die()
                    continue
                else:
                    computer_score = str(computer_score)
                    print("*computer hold on " + computer_score + "*")
                    computer_score = int(computer_score)
                    is_user_turn == True
                    break
            else:
                computer_score = 1
                print("The computer rolled a 1. Turn over.")
                return computer_score
        if computer_rand == 1:
            print("The computer rolled a 1. Turn over.")
            computer_score = 1
            return computer_score
        else:
            return computer_score

def report_points(user_total,computer_total):
    '''How can I call the take_turn function and continuously add up
             turn totals until the 100 points mark is reached'''


#print_current_player(False)
#take_turn(False,10)

if __name__ == '__main__':
    main()
