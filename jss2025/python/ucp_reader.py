import json
import sys
import csv # Import the csv module

def read_ucp_data(file_path):
    """
    Reads Use Case Points (UCP) data from a specified JSON file.

    Args:
        file_path (str): The path to the JSON file containing UCP data.

    Returns:
        dict: A dictionary containing the parsed UCP data, or None if an error occurs.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            ucp_data = json.load(f)
        return ucp_data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{file_path}'. Please check the file's format.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def display_ucp_summary(ucp_data):
    """
    Displays a summary of the UCP data.

    Args:
        ucp_data (dict): The dictionary containing the parsed UCP data.
    """
    if not ucp_data:
        print("No UCP data to display.")
        return

    print("\n--- Use Case Points Data Summary ---")

    print("\nUse Cases:")
    if 'use_cases' in ucp_data and ucp_data['use_cases']:
        for uc in ucp_data['use_cases']:
            print(f"  - Name: {uc.get('name', 'N/A')}, Description: {uc.get('description', 'N/A')}, Complexity: {uc.get('complexity', 'N/A')}")
    else:
        print("  No use cases defined.")

    print("\nActors:")
    if 'actors' in ucp_data and ucp_data['actors']:
        for actor in ucp_data['actors']:
            print(f"  - Name: {actor.get('name', 'N/A')}, Description: {actor.get('description', 'N/A')}, Complexity: {actor.get('complexity', 'N/A')}")
    else:
        print("  No actors defined.")

    print("\nEnvironmental Factors:")
    if 'environmental_factors' in ucp_data and ucp_data['environmental_factors']:
        for ef in ucp_data['environmental_factors']:
            print(f"  - Name: {ef.get('name', 'N/A')}, Weight: {ef.get('weight', 'N/A')}")
    else:
        print("  No environmental factors defined.")

    print("\nTechnical Factors:")
    if 'technical_factors' in ucp_data and ucp_data['technical_factors']:
        for tf in ucp_data['technical_factors']:
            print(f"  - Name: {tf.get('name', 'N/A')}, Weight: {tf.get('weight', 'N/A')}")
    else:
        print("  No technical factors defined.")

    print("\nWeights:")
    print(f"  Unadjusted Use Case Weights: {ucp_data.get('unadjusted_use_case_weights', 'N/A')}")
    print(f"  Unadjusted Actor Weights: {ucp_data.get('unadjusted_actor_weights', 'N/A')}")

def calculate_uucw(use_cases, weights):
    """
    Calculates Unadjusted Use Case Weight (UUCW).

    Args:
        use_cases (list): A list of use case dictionaries.
        weights (dict): A dictionary of use case complexity weights (simple, average, complex).

    Returns:
        float: The calculated UUCW.
    """
    uucw = 0
    if not use_cases or not weights:
        return 0

    for uc in use_cases:
        complexity = uc.get('complexity', 'unknown').lower()
        uucw += weights.get(complexity, 0) # Default to 0 if complexity not found
    return uucw

def calculate_uaw(actors, weights):
    """
    Calculates Unadjusted Actor Weight (UAW).

    Args:
        actors (list): A list of actor dictionaries.
        weights (dict): A dictionary of actor complexity weights (simple, average, complex).

    Returns:
        float: The calculated UAW.
    """
    uaw = 0
    if not actors or not weights:
        return 0

    for actor in actors:
        complexity = actor.get('complexity', 'unknown').lower()
        uaw += weights.get(complexity, 0) # Default to 0 if complexity not found
    return uaw

def calculate_tcf(technical_factors):
    """
    Calculates Technical Complexity Factor (TCF).
    Formula: TCF = 0.6 + (0.01 * sum(technical_factor_weights))

    Args:
        technical_factors (list): A list of technical factor dictionaries, each with a 'weight'.

    Returns:
        float: The calculated TCF.
    """
    if not technical_factors:
        return 1.0 # Default TCF if no factors

    sum_tf_weights = sum(tf.get('weight', 0) for tf in technical_factors)
    tcf = 0.6 + (0.01 * sum_tf_weights)
    return tcf

def calculate_ecf(environmental_factors):
    """
    Calculates Environmental Complexity Factor (ECF).
    Formula: ECF = 1.4 + (-0.03 * sum(environmental_factor_weights))

    Args:
        environmental_factors (list): A list of environmental factor dictionaries, each with a 'weight'.

    Returns:
        float: The calculated ECF.
    """
    if not environmental_factors:
        return 1.0 # Default ECF if no factors

    sum_ef_weights = sum(ef.get('weight', 0) for ef in environmental_factors)
    ecf = 1.4 + (-0.03 * sum_ef_weights)
    return ecf

def calculate_ucp(uucw, uaw, tcf, ecf):
    """
    Calculates the final Use Case Points (UCP).
    Formula: UCP = (UUCW + UAW) * TCF * ECF

    Args:
        uucw (float): Unadjusted Use Case Weight.
        uaw (float): Unadjusted Actor Weight.
        tcf (float): Technical Complexity Factor.
        ecf (float): Environmental Complexity Factor.

    Returns:
        float: The calculated UCP.
    """
    return (uucw + uaw) * tcf * ecf

def calculate_estimated_effort(ucp, hours_per_ucp):
    """
    Calculates the Estimated Effort.
    Formula: Estimated Effort = UCP x Hours/UCP

    Args:
        ucp (float): Calculated Use Case Points.
        hours_per_ucp (float): The number of hours estimated per Use Case Point.

    Returns:
        float: The calculated Estimated Effort.
    """
    return ucp * hours_per_ucp


# --- Main execution ---
if __name__ == "__main__":
    # Check if a file path is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python your_script_name.py <path_to_json_file>")
        print("Example: python ucp_reader.py ucp_data.json")
        sys.exit(1) # Exit with an error code

    json_file_name = sys.argv[1] # The first argument after the script name is the file path
    output_csv_file = "ucp_estimated_effort.csv" # Define the output CSV file name

    # Read the data from the specified JSON file
    ucp_data = read_ucp_data(json_file_name)

    if ucp_data:
        print(f"\nSuccessfully read UCP data from '{json_file_name}'.")
        print(f"Project Name: {ucp_data.get('project_name', 'N/A')}")

        # Display a summary
        display_ucp_summary(ucp_data)

        # --- UCP Calculations ---
        use_cases = ucp_data.get('use_cases', [])
        actors = ucp_data.get('actors', [])
        unadjusted_uc_weights = ucp_data.get('unadjusted_use_case_weights', {})
        unadjusted_actor_weights = ucp_data.get('unadjusted_actor_weights', {})
        technical_factors = ucp_data.get('technical_factors', [])
        environmental_factors = ucp_data.get('environmental_factors', [])

        # Calculate UUCW
        uucw = calculate_uucw(use_cases, unadjusted_uc_weights)
        print(f"\nCalculated Unadjusted Use Case Weight (UUCW): {uucw:.2f}")

        # Calculate UAW
        uaw = calculate_uaw(actors, unadjusted_actor_weights)
        print(f"Calculated Unadjusted Actor Weight (UAW): {uaw:.2f}")

        # Calculate TCF
        tcf = calculate_tcf(technical_factors)
        print(f"Calculated Technical Complexity Factor (TCF): {tcf:.2f}")

        # Calculate ECF
        ecf = calculate_ecf(environmental_factors)
        print(f"Calculated Environmental Complexity Factor (ECF): {ecf:.2f}")

        # Calculate final UCP
        ucp = calculate_ucp(uucw, uaw, tcf, ecf)
        print(f"Calculated Use Case Points (UCP): {ucp:.2f}")

        # --- Generate Estimated Effort and write to CSV ---
        print(f"\nGenerating Estimated Effort data and saving to '{output_csv_file}'...")
        effort_data = []
        # Add header row
        effort_data.append(["Hours per UCP", "Estimated Effort (hours)"])

        for hours_per_ucp in range(1, 501): # Loop from 1 to 500
            estimated_effort = calculate_estimated_effort(ucp, float(hours_per_ucp))
            effort_data.append([hours_per_ucp, f"{estimated_effort:.2f}"])

        try:
            with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerows(effort_data)
            print(f"Successfully saved estimated effort data to '{output_csv_file}'.")
        except Exception as e:
            print(f"Error writing to CSV file: {e}")

        # Example of accessing a specific use case (kept for reference)
        if use_cases:
            print(f"\nFirst Use Case Name: {use_cases[0].get('name', 'N/A')}")

