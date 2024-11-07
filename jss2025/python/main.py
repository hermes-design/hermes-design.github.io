from itertools import product


def all_combinations(arr1, arr2, arr3):
  """
  This function takes three arrays of strings and returns a list of all possible combinations.

  Args:
      arr1: The first array of On ground actions.
      arr2: The second array of OnOrbit actions.
      arr3: The third array of failures modes.

  Returns:
      A list of all possible combinations of the three arrays.
  """
  # Use product from itertools to get all combinations
  combinations = product(arr1, arr2, arr3)
  # Return the combinations as a list
  return list(combinations)


def custom_print(combination):
  print(f"[{','.join(combination)}] true -> true;")  # f-string formatting


# Example usage
arr1 = [
    "OnGroundStandby",
    "CheckOnGroundSatelliteToBuild",
    "CheckOnGroundSatelliteToManufecture",
    "BuildOnGroundSatellite",
    "ResetOnGroundManoeuvers",
]
arr2 = [
    "OnOrbitStandby", "RepairOnOrbitSoftwareUpdate",
    "CheckOnOrbitRedundantSatellite", "MoveReplaceRedundantSatellite",
    "ResetOnOrbitManoeuvers"
]
arr3 = ["Scheduled", "Unscheduled", "Failure", "Normal"]

combinations = all_combinations(arr1, arr2, arr3)

# Print the combinations
for combination in combinations:
  custom_print(combination)

