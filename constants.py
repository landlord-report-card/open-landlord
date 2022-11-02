SEARCH_DEFAULT_MAX_RESULTS = 100

GRADE_COLORS = {
  'A': "2cba00",
  'B': "2cba00",
  'C': "ffa700",
  'D': "ffa700",
  'F': "ff0000",
}


LANDLORD_SIZES = [
    (10, {"size": "Very Large (More than 10 properties owned)", "color": "ff0000"}),
    (4, {"size": "Large (Between 5 and 10 properties owned)", "color": "ff0000"}),
    (1, {"size": "Medium (Between 1 and 4 properties owned)", "color": "ffa700"}),
    (0, {"size": "Small (One property owned)", "color": "2cba00"}),
]

GRADE_A = {"grade":"A", "value":4, "color":GRADE_COLORS["A"]}
GRADE_B = {"grade":"B", "value":3, "color":GRADE_COLORS["B"]}
GRADE_C = {"grade":"C", "value":2, "color":GRADE_COLORS["C"]}
GRADE_D = {"grade":"D", "value":1, "color":GRADE_COLORS["D"]}
GRADE_F = {"grade":"F", "value":0, "color":GRADE_COLORS["F"]}


GRADE_COMPONENTS = [
    "tenant_complaints_count",
    "code_violations_count",
    "police_incidents_count",
    "eviction_count",
]

STATS_TO_SCALE = GRADE_COMPONENTS