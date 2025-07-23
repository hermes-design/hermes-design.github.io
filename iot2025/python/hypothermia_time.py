# Import necessary libraries
import math

def estimate_hypothermia_time(initial_core_temp, water_temp, drop_rate_per_min):
    """
    Estimates the mean time between different stages of hypothermia,
    including a specific initial drop time from 37°C to 35°C,
    and calculates Lambda (1/time) for each transition.
    Also calculates "Mu" (arm usage rate) from Stage i to Stage 5
    based on given probabilities and Lambda values.

    Args:
        initial_core_temp (float): The initial core body temperature in Celsius.
        water_temp (float): The water temperature in Celsius.
        drop_rate_per_min (float): The rate of core temperature drop per minute in °C/min.
                                   This rate is used for temperatures below 35°C.

    Returns:
        dict: A dictionary containing the estimated time for each transition between stages,
              their corresponding Lambda values, and the calculated Mu values.
              Returns None if the initial temperature is already at or below the lowest stage.
    """

    # Define key temperature points for transitions between stages
    # These represent the *start* of the subsequent stage or the *end* of the preceding one.
    temp_normal_body = 37.0 # Normal body temperature
    temp_normal_to_s1 = 35.0 # Start of Stage 1
    temp_s1_to_s2 = 32.0     # End of Stage 1 / Start of Stage 2
    temp_s2_to_s3 = 28.0     # End of Stage 2 / Start of Stage 3
    temp_s3_to_s4 = 24.0     # End of Stage 3 / Start of Stage 4

    # Specific information provided by the user
    fixed_time_37_to_35 = 25.0 # minutes

    print(f"--- Hypothermia Time Estimation ---")
    print(f"Initial Core Temperature: {initial_core_temp}°C")
    print(f"Water Temperature: {water_temp}°C")
    print(f"Core Temperature Drop Rate (below 35°C): {drop_rate_per_min}°C/min\n")

    results = {}
    current_temp_for_calculation = initial_core_temp
    cumulative_time = 0.0

    # Helper function to calculate time to drop from a start_temp to a target_temp
    # Ensures that if start_temp is already at or below target_temp, time is 0.
    def get_time_for_drop(start_temp, target_temp, rate):
        if start_temp <= target_temp:
            return 0.0
        return (start_temp - target_temp) / rate

    # 1. Mean time from Normal state (37°C) to Stage 1 (35°C)
    time_key_37_to_35 = "Mean time from Normal state (37°C) to Stage 1 (35°C)"
    if initial_core_temp >= temp_normal_body:
        # If starting at or above 37C, use the fixed time to reach 35C
        results[time_key_37_to_35] = f"{fixed_time_37_to_35:.2f} minutes (fixed)"
        cumulative_time += fixed_time_37_to_35
        current_temp_for_calculation = temp_normal_to_s1 # Now at 35C for subsequent calculations
    elif initial_core_temp > temp_normal_to_s1 and initial_core_temp < temp_normal_body:
        # If starting between 35C and 37C, calculate time based on the general drop rate
        time_to_s1_start = get_time_for_drop(initial_core_temp, temp_normal_to_s1, drop_rate_per_min)
        results[time_key_37_to_35] = f"{time_to_s1_start:.2f} minutes"
        cumulative_time += time_to_s1_start
        current_temp_for_calculation = temp_normal_to_s1
    else:
        results[time_key_37_to_35] = "Already at or below 35°C"
        current_temp_for_calculation = initial_core_temp # Use initial temp if already below 35C

    # Ensure current_temp_for_calculation is capped at 35.0 for the next stages if it started higher
    if current_temp_for_calculation > temp_normal_to_s1:
        current_temp_for_calculation = temp_normal_to_s1

    # 2. Mean time from Stage 1 (35°C) to Stage 2 (32°C)
    time_key_s1_to_s2 = "Mean time from Stage 1 (35°C) to Stage 2 (32°C)"
    if current_temp_for_calculation > temp_s1_to_s2:
        time_s1_to_s2 = get_time_for_drop(current_temp_for_calculation, temp_s1_to_s2, drop_rate_per_min)
        results[time_key_s1_to_s2] = f"{time_s1_to_s2:.2f} minutes"
        cumulative_time += time_s1_to_s2
        current_temp_for_calculation = temp_s1_to_s2
    else:
        results[time_key_s1_to_s2] = "Already at or below 32°C"
        # If already below, current_temp_for_calculation remains as is for the next stage's start.

    # 3. Mean time from Stage 2 (32°C) to Stage 3 (28°C)
    time_key_s2_to_s3 = "Mean time from Stage 2 (32°C) to Stage 3 (28°C)"
    if current_temp_for_calculation > temp_s2_to_s3:
        time_s2_to_s3 = get_time_for_drop(current_temp_for_calculation, temp_s2_to_s3, drop_rate_per_min)
        results[time_key_s2_to_s3] = f"{time_s2_to_s3:.2f} minutes"
        cumulative_time += time_s2_to_s3
        current_temp_for_calculation = temp_s2_to_s3
    else:
        results[time_key_s2_to_s3] = "Already at or below 28°C"

    # 4. Mean time from Stage 3 (28°C) to Stage 4 (24°C)
    time_key_s3_to_s4 = "Mean time from Stage 3 (28°C) to Stage 4 (24°C)"
    if current_temp_for_calculation > temp_s3_to_s4:
        time_s3_to_s4 = get_time_for_drop(current_temp_for_calculation, temp_s3_to_s4, drop_rate_per_min)
        results[time_key_s3_to_s4] = f"{time_s3_to_s4:.2f} minutes"
        cumulative_time += time_s3_to_s4
        current_temp_for_calculation = temp_s3_to_s4
    else:
        results[time_key_s3_to_s4] = "Already at or below 24°C"

    # Calculate Lambda for each transition
    lambda_values_calculated = {} # Store numerical lambda values for mu calculation

    # For 37 to 35
    time_val_37_to_35 = None
    if "minutes (fixed)" in results.get(time_key_37_to_35, ""):
        time_val_37_to_35 = fixed_time_37_to_35
    elif "minutes" in results.get(time_key_37_to_35, ""):
        try:
            time_val_37_to_35 = float(results[time_key_37_to_35].split(" ")[0])
        except ValueError:
            pass
    if time_val_37_to_35 is not None and time_val_37_to_35 > 0:
        lambda_val = 1 / time_val_37_to_35
        lambda_values_calculated[time_key_37_to_35] = lambda_val
        results[f"Lambda for {time_key_37_to_35}"] = f"{lambda_val:.4f} (1/minute)"
    else:
        results[f"Lambda for {time_key_37_to_35}"] = "N/A (Time is 0 or not applicable)"


    # For other stages
    transition_keys = {
        "Stage 1": time_key_s1_to_s2,
        "Stage 2": time_key_s2_to_s3,
        "Stage 3": time_key_s3_to_s4
    }

    for stage_name_short, key in transition_keys.items():
        time_val = None
        if "minutes" in results.get(key, ""):
            try:
                time_val = float(results[key].split(" ")[0])
            except ValueError:
                pass
        if time_val is not None and time_val > 0:
            lambda_val = 1 / time_val
            lambda_values_calculated[key] = lambda_val
            results[f"Lambda for {key}"] = f"{lambda_val:.4f} (1/minute)"
        else:
            results[f"Lambda for {key}"] = "N/A (Time is 0 or not applicable)"


    # Now calculate mu values (Arm Usage)
    mu_results = {}
    probabilities_moving_arms = {
        "Stage 1": 0.93, # Probability of moving arms at Stage 1
        "Stage 2": 0.75, # Probability of moving arms at Stage 2
        "Stage 3": 0.07  # Probability of moving arms at Stage 3
    }

    # Map stage names to their corresponding lambda keys for temperature drop
    # This lambda represents the rate of leaving the stage due to temperature drop.
    lambda_key_map_for_mu = {
        "Stage 1": time_key_s1_to_s2,
        "Stage 2": time_key_s2_to_s3,
        "Stage 3": time_key_s3_to_s4
    }

    print("\n--- Mu (Arm Usage) Calculations ---")
    for stage_name, prob_moving_arms in probabilities_moving_arms.items():
        lambda_key = lambda_key_map_for_mu.get(stage_name)
        if lambda_key and lambda_key in lambda_values_calculated:
            lambda_val = lambda_values_calculated[lambda_key]

            if prob_moving_arms >= 1.0: # Probability is 100% or more, mu approaches infinity
                mu_results[f"Mu (Arm Usage) from {stage_name} to Stage 5"] = "Probability is 100%, mu approaches infinity"
            elif prob_moving_arms < 0 or prob_moving_arms > 1: # Invalid probability
                 mu_results[f"Mu (Arm Usage) from {stage_name} to Stage 5"] = "Invalid probability (must be between 0 and 1)"
            else:
                # Formula: P = mu / (lambda + mu)  =>  mu = (P * lambda) / (1 - P)
                # This mu represents the rate of cessation of arm movement.
                denominator = (1 - prob_moving_arms)
                if denominator == 0: # Should be caught by prob_moving_arms >= 1.0, but for safety
                    mu_value = float('inf')
                else:
                    mu_value = (prob_moving_arms * lambda_val) / denominator
                mu_results[f"Mu (Arm Usage) from {stage_name} to Stage 5"] = f"{mu_value:.4f} (1/minute)"
        else:
            mu_results[f"Mu (Arm Usage) from {stage_name} to Stage 5"] = "Lambda value not available for calculation"

    results.update(mu_results) # Add mu results to the main results dictionary


    print("\nEstimated Times for Transitions, Lambda Values, and Mu Values:")
    for key, value in results.items():
        print(f"- {key}: {value}")

    print(f"\nTotal estimated cumulative time to reach 24°C (start of Stage 4): {cumulative_time:.2f} minutes")

    return results

# --- Example Usage ---
# Based on the hypothesis:
# In very cold water (2°C), the core temperature is expected to drop at a rate of 0.35°C/min.
# Let's assume a normal initial core temperature of 37°C.
initial_temp = 37.0
water_temp_example = 2.0
drop_rate_example = 0.35

estimate_hypothermia_time(initial_temp, water_temp_example, drop_rate_example)



