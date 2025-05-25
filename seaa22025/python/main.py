

def players_declaration(players):
    """Generates player declaration strings for a list of player names.

    Args:
        players: A list of player names.

    Returns:
        A list of player declaration strings in the format "player p<number> <name> endplayer".
    """

    transition_list = []
    for index, player in enumerate(players, start=1):
        transition_list.append(f"player p{index} {player} endplayer")
    return transition_list

def generate_module(name, tasks_number, task_id):
    """Generates a module definition with specified variables and transitions.

    Args:
        name: The name of the module.
        tasks_number: The number of tasks in the module.
        task_id: A unique identifier for the module.

    Returns:
        A tuple containing the module name, variable list, position, and transition list.
    """

    var_list = []
    position = f"{task_id}_P"  # Use f-string for better readability
    transition_list = []

    for nb in range(1, tasks_number + 1):  # Include the last task
        resultat = f"{task_id}_{nb}"
        var_list.append(resultat)

    for nb in range(len(var_list) - 1):
        resultat = (
            f"  [a_{var_list[nb]}] {var_list[nb]} = true & {task_id}_P = "
            f"-> (1 - Prob{var_list[nb]}):("
            f"{var_list[nb]}' = false) & ({var_list[nb + 1]}' = true) & ({task_id}_P' = )"
            f"+ Prob{var_list[nb]}:("
            f"{var_list[nb]}' = true);"
        )
        transition_list.append(resultat)

    resultat = (
        f"  [a_{var_list[len(var_list)-1]}] {var_list[len(var_list)-1]} = true & {task_id}_P = "
        f"-> (1 - Prob{var_list[len(var_list)-1]}):("
        f"{var_list[len(var_list)-1]}' = false) & ({var_list[0]}' = true) & ({task_id}_P' = )"
        f"+ Prob{var_list[len(var_list)-1]}:("
        f"{var_list[len(var_list)-1]}' = true);"
    )
    transition_list.append(resultat)

    return name, var_list, position, transition_list

# Example usage:

def generate_global_variables(task_id, nb_tasks):
    """Generates global variable declarations for probabilities.

    Args:
        task_id: The ID of the task.
        nb_tasks: The number of tasks.

    Returns:
        A list of global variable declarations.
    """

    probabilities_list = [
        f"const double Prob{task_id}_{i+1};" for i in range(nb_tasks)
    ]
    return probabilities_list

def clear_file(file_path, text_to_append):
    """Appends text to a file.

    Args:
        file_path: The path to the file.
        text_to_append: The text to append.
    """

    try:
        with open(file_path, 'w') as file:
            file.write(text_to_append)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")



def append_text_to_file(file_path, text_to_append):
    """Appends text to a file.

    Args:
        file_path: The path to the file.
        text_to_append: The text to append.
    """

    try:
        with open(file_path, 'a') as file:
            file.write(text_to_append)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")



def generate_system( ):
    players= ["Watchkeeping_Officer", "Duty_Officer", "Captain", "Crew_A", "Crew_B", "Crew_C", "Crew_D", "Chief_Officer","Display_screen","Alarm","Phone","Radio","Davit_Winch"]
    positions = ["Wing_Bridge", "Navigation_Bridge", "Cabin_Room",  "Boat_Deck", "Rescue_Boat"]
    num_tasks =         [3,  5,    4,   15,    5,    4,  5,   2,1,1,1,1,1]
    task_identifier = ["W", "D", "A", "CA", "CB", "CC", "CD", "C","DS","AL","PH","RA","DW"]

    players_definition= players_declaration(players)
    file_name = "ECSA25.nm"
    clear_file(file_name,"")
    #generate model
    append_text_to_file(file_name, "csg" + "\n\n")
    #generate players
    for item in range(0,len(players_definition)):
        append_text_to_file(file_name, players_definition[item]+"\n\n")


    #global variables
    for index in range(0, len(players)):
        global_system_data = generate_global_variables(task_identifier[index], num_tasks[index])
        append_text_to_file(file_name, "//Global variables for player " + players[index]+ "\n")
        for var_item in range(0, len(global_system_data)):
            append_text_to_file(file_name, global_system_data[var_item] + "\n")
    # global positions variables
    for index in range(0, len(positions)):
        append_text_to_file(file_name, "const int " + positions[index] + "="+str(index)+";\n")
    append_text_to_file(file_name, "const int MAX_POSITION = " + str(len(positions)) + ";\n\n")
    append_text_to_file(file_name, "const int NOT_DEFINED = -1;\n\n")

    for index in range(0, len(players)):
        module_data = generate_module(players[index], num_tasks[index], task_identifier[index])
        append_text_to_file(file_name, "module "+module_data[0]+ "\n")
        append_text_to_file(file_name, "    "+ module_data[2] + ": [0..MAX_POSITION] init 0; \n")
        for var_index in range(0, len(module_data[1])):
            append_text_to_file(file_name, "    "+module_data[1][var_index] + ": bool init false; \n")
        for transition_index in range(0, len(module_data[3])):
            append_text_to_file(file_name, module_data[3][transition_index]+"\n")
        append_text_to_file(file_name, "endmodule " + "\n\n")


generate_system( )

