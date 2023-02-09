# Importing necessary packages
import pulp
import pandas as pd
import numpy as np

# Question 15.2
# In the videos, we saw the “diet problem”. (The diet problem is one of the first large-scale
# optimization problems to be studied in practice. Back in the 1930’s and 40’s, the Army wanted
# to meet the nutritional requirements of its soldiers while minimizing the cost.) In this
# homework you get to solve a diet problem with real data. The data is given in the file diet.xls.

# 1. Formulate an optimization model (a linear program) to find the cheapest diet that satisfies
# the maximum and minimum daily nutrition constraints, and solve it using PuLP. Turn in your code
# and the solution. (The optimal solution should be a diet of air-popped popcorn, poached eggs,
# oranges, raw iceberg lettuce, raw celery, and frozen broccoli. UGH!)


# We first import our data using pandas read_excel() function.
# After viewing our data we have confirmed all the variables are numerical, except
# for 'Serving Size' which consists of strings.

diet = pd.read_excel(
    r"C:\Users\Owner\Documents\Github\python\class assignments\Introduction to Statistical Modeling\Assignment 7\data\diet.xls",
    nrows=64)

# We then create our constraints.
diet_constraints = pd.read_excel(
    r"C:\Users\Owner\Documents\Github\python\class assignments\Introduction to Statistical Modeling\Assignment 7\data\diet.xls",
    skiprows=66, header=None
    ).iloc[:, 2:]
diet_constraints.columns = diet.columns[2:]

diet_constraints

diet.head(5)

# Using Pulp for optimization

# Since there are many different food variables each with their own set of nutritional values, prices,
# and min/max constraints, the most efficient approach is to build a loop to run through these variables.
# Will consequently create a list comprehension in Python to facilitate creation of this loop.

# Using linear algebra, we can see each row of equations is just a dot product between the nutritional value
# and the food value names.

# Minimize cost
prob = pulp.LpProblem("Army Diet Optimization", pulp.LpMinimize)

food = diet['Foods']
varList = pulp.LpVariable.dicts("Foods", food, lowBound=0)

# Create binary variable
binList = pulp.LpVariable.dicts("Binary", food, lowBound=0, upBound=1, cat="Binary")

# Minimize the following function: (price/servings)*foods
price = list(diet['Price/ Serving'])
prob += pulp.lpSum([price[i] * varList[food[i]] for i in range(len(varList))])

# Our constraints are therefore defined as:
# 1. nutrient*food > min
# 2. nutrients*food < max

# List of nutrients
col = diet_constraints.columns[1:]

# Set min/max constraints for each food type
for c in col:
    prob += pulp.lpSum([diet[c][i] * varList[food[i]] for i in range(len(varList))]) >= diet_constraints[c][0]
    prob += pulp.lpSum([diet[c][i] * varList[food[i]] for i in range(len(varList))]) <= diet_constraints[c][1]

# Solve problem
prob.solve()

# Find optimal solution
print("Status:", pulp.LpStatus[prob.status])

# Print the solution
for v in prob.variables():
    if v.varValue != 0:
        print(v.name, "=", v.varValue)

# Extract variable names and the associated optimal serving.
# Upon review, Pulp replaces spaces with an underscore, which we can rectify in the extraction process.

# Save values to pandas DataFrame and export to Excel.

# We then join the original dataset with the optimal solutions, adding them in an additional column.

# Dataframe of optimal values
var = prob.variables()
df_optimal = pd.DataFrame(
    {'Foods': [v.name.replace("_", " ").replace("Foods ", "") for v in var],
     'Optimal Servings 1': [v.varValue for v in var]},
)

# Join table with optimal solutions, then export to Excel
diet_optimal = diet.merge(df_optimal, on='Foods')

# DataFrame containing just the necessary values
df1 = diet_optimal.loc[diet_optimal['Optimal Servings 1'] > 0][['Foods', 'Price/ Serving',
                                                                'Optimal Servings 1']]

# Solve for cost
sol1 = np.sum(df1['Price/ Serving'] * df1['Optimal Servings 1'])

print('Total cost per day per one member of the army without constraints is $' + str(round(sol1, 2)))

# 2. Please add to your model the following constraints (which might require adding more variables)
# and solve the new model:

# a.) If a food is selected, then a minimum of 1/10 serving must be chosen.
# (Hint: now you will need two variables for each food i: whether it is chosen,
# and how much is part of the diet. You’ll also need to write a constraint to link them.)


# Will add all constraints once. Per the question, the value must be greater than 1/10 if used at all.
# Food value must be less than the multiple of the binary value; however, if the binary value is 0 then
# the food value is also 0. This creates a ceiling for the food value if the binary is 1.

# This means that we are always losing out on any potential solutions for which the serving amount is
# greater than the coefficient placed with the binary value. Consequently, the binary value should
# be large enough to accommodate a reasonable solution for the optimization problem.

# Will therefore put an large coefficient to the binary expression so that we can have at least
# that many servings.


for i in food:
    # Sets minimum to 1/10
    prob += varList[i] >= 0.1 * binList[i]

    # Ties food value with binary value
    prob += varList[i] <= 9001 * binList[i]

# b.) Many people dislike celery and frozen broccoli. So at most one, but not both, can be selected.

# Will set value to 1 so at least one must be selected.
prob += binList['Frozen Broccoli'] + binList['Celery, Raw'] == 1

# c.) To get day-to-day variety in protein, at least 3 kinds of meat/poultry/fish/eggs must be selected.
# [If something is ambiguous (e.g., should bean-and-bacon soup be considered meat?), just call it whatever 
# you think is appropriate – I want you to learn how to write this type of constraint, but I don’t really 
# care whether we agree on how to classify foods!]

# The constraits for this variable are the same as part b. However, we will need to do manual sorting for 
# this section as there isn't a categorical variable indicating whether food is a meat or egg. 

np.sort(food)

# Create list of proteins
proteinList = [
    'Bologna,Turkey', 'Frankfurter, Beef', 'Ham,Sliced,Extralean',
    'Hamburger W/Toppings', 'Hotdog, Plain', 'Kielbasa,Prk',
    'Pizza W/Pepperoni', 'Poached Eggs',
    'Pork', 'Roasted Chicken', 'Sardines in Oil',
    'Scrambled Eggs',
    'Splt Pea&Hamsoup', 'Vegetbeef Soup',
    'White Tuna in Water']

# Build constraints of at least 3
prob += pulp.lpSum([binList[p] for p in proteinList]) >= 3

prob.solve()

# Dataframe of optimal values
var = prob.variables()
df_optimal2 = pd.DataFrame(
    {'Foods': [v.name.replace("_", " ").replace("Foods ", "") for v in var],
     'Optimal Servings 2': [v.varValue for v in var]},
)

# Join table with optimal solution and export to Excel
diet_optimal = diet_optimal.merge(df_optimal2, on='Foods')

# DataFrame containing just the necessary values
df2 = diet_optimal.loc[diet_optimal['Optimal Servings 2'] > 0][['Foods',
                                                                'Price/ Serving', 'Optimal Servings 2']]

# Solve for cost
sol2 = np.sum(df2['Price/ Serving'] * df2['Optimal Servings 2'])

print('Total cost per day per one member of the army with constraints is $' + str(round(sol2, 2)))

# With more constraints the cost goes up from $3.78 to $3.98 per day for each army personnel member. 
# As more restrictions (constraints) are added to the optimization, it decreases its efficiency.


#Output
     ### command line - C:\Users\Owner\Miniconda3\lib\site-packages\pulp\solverdir\cbc\win\64\cbc.exe C:\Users\Owner\AppData\Local\Temp\e39d283a6e09460b96823d0b100ad925-pulp.mps timeMode elapsed branch printingOptions all solution C:\Users\Owner\AppData\Local\Temp\e39d283a6e09460b96823d0b100ad925-pulp.sol (default strategy 1)
     ### At line 2 NAME          MODEL
     ### At line 3 ROWS
     ### At line 27 COLUMNS
     ### At line 1286 RHS
     ### At line 1309 BOUNDS
     ### At line 1310 ENDATA
     ### Problem MODEL has 22 rows, 64 columns and 1194 elements
     ### Coin0008I MODEL read with 0 errors
     ### Option for timeMode changed from cpu to elapsed
     ### Presolve 22 (0) rows, 64 (0) columns and 1194 (0) elements
     ### 0  Obj 0 Primal inf 21.63092 (11)
     ### 9  Obj 4.3371168
     ### Optimal - objective value 4.3371168
     ### Optimal objective 4.33711681 - 9 iterations time 0.012
     ### Option for printingOptions changed from normal to all
     ### Total time (CPU seconds):       0.04   (Wallclock seconds):       0.04     ### 

     ### Status: Optimal
     ### Foods_Celery,_Raw = 52.64371
     ### Foods_Frozen_Broccoli = 0.25960653
     ### Foods_Lettuce,Iceberg,Raw = 63.988506
     ### Foods_Oranges = 2.2929389
     ### Foods_Poached_Eggs = 0.14184397
     ### Foods_Popcorn,Air_Popped = 13.869322
     ### Total cost per day per one member of the army without constraints is $3.78
     ### Welcome to the CBC MILP Solver 
     ### Version: 2.10.3 
     ### Build Date: Dec 15 2019      ### 

     ### command line - C:\Users\Owner\Miniconda3\lib\site-packages\pulp\solverdir\cbc\win\64\cbc.exe C:\Users\Owner\AppData\Local\Temp\4b8f3e1d596f4f28951b69cdbbf65946-pulp.mps timeMode elapsed branch printingOptions all solution C:\Users\Owner\AppData\Local\Temp\4b8f3e1d596f4f28951b69cdbbf65946-pulp.sol (default strategy 1)
     ### At line 2 NAME          MODEL
     ### At line 3 ROWS
     ### At line 157 COLUMNS
     ### At line 1817 RHS
     ### At line 1970 BOUNDS
     ### At line 2035 ENDATA
     ### Problem MODEL has 152 rows, 128 columns and 1467 elements
     ### Coin0008I MODEL read with 0 errors
     ### Option for timeMode changed from cpu to elapsed
     ### Continuous objective value is 4.38006 - 0.00 seconds
     ### Cgl0003I 0 fixed, 0 tightened bounds, 64 strengthened rows, 0 substitutions
     ### Cgl0004I processed model has 140 rows, 127 columns (63 integer (63 of which binary)) and 868 elements
     ### Cbc0038I Initial state - 7 integers unsatisfied sum - 1.5009
     ### Cbc0038I Pass   1: suminf.    0.52935 (2) obj. 5.37039 iterations 51
     ### Cbc0038I Solution found of 5.37039
     ### Cbc0038I Relaxing continuous gives 5.37039
     ### Cbc0038I Before mini branch and bound, 55 integers at bound fixed and 53 continuous
     ### Cbc0038I Full problem 140 rows 127 columns, reduced to 30 rows 19 columns
     ### Cbc0038I Mini branch and bound improved solution from 5.37039 to 4.51296 (0.03 seconds)
     ### Cbc0038I Round again with cutoff of 4.50011
     ### Cbc0038I Pass   2: suminf.    0.59518 (3) obj. 4.50011 iterations 7
     ### Cbc0038I Pass   3: suminf.    0.27805 (1) obj. 4.50011 iterations 70
     ### Cbc0038I Pass   4: suminf.    0.02107 (1) obj. 4.50011 iterations 2
     ### Cbc0038I Pass   5: suminf.    0.28238 (2) obj. 4.50011 iterations 18
     ### Cbc0038I Pass   6: suminf.    0.28238 (2) obj. 4.50011 iterations 4
     ### Cbc0038I Pass   7: suminf.    0.16506 (1) obj. 4.50011 iterations 50
     ### Cbc0038I Pass   8: suminf.    0.06902 (1) obj. 4.50011 iterations 2
     ### Cbc0038I Pass   9: suminf.    0.67065 (3) obj. 4.50011 iterations 21
     ### Cbc0038I Pass  10: suminf.    0.17875 (2) obj. 4.50011 iterations 11
     ### Cbc0038I Pass  11: suminf.    0.15029 (1) obj. 4.50011 iterations 17
     ### Cbc0038I Pass  12: suminf.    0.09452 (1) obj. 4.50011 iterations 2
     ### Cbc0038I Pass  13: suminf.    0.63556 (5) obj. 4.50011 iterations 27
     ### Cbc0038I Pass  14: suminf.    0.18320 (2) obj. 4.50011 iterations 19
     ### Cbc0038I Pass  15: suminf.    0.19253 (1) obj. 4.50011 iterations 19
     ### Cbc0038I Pass  16: suminf.    0.09332 (1) obj. 4.50011 iterations 1
     ### Cbc0038I Pass  17: suminf.    0.84185 (4) obj. 4.50011 iterations 23
     ### Cbc0038I Pass  18: suminf.    0.84185 (4) obj. 4.50011 iterations 8
     ### Cbc0038I Pass  19: suminf.    0.29349 (1) obj. 4.50011 iterations 35
     ### Cbc0038I Pass  20: suminf.    0.06462 (1) obj. 4.50011 iterations 3
     ### Cbc0038I Pass  21: suminf.    0.38400 (2) obj. 4.50011 iterations 17
     ### Cbc0038I Pass  22: suminf.    0.38400 (2) obj. 4.50011 iterations 6
     ### Cbc0038I Pass  23: suminf.    0.15222 (1) obj. 4.50011 iterations 4
     ### Cbc0038I Pass  24: suminf.    0.09042 (1) obj. 4.50011 iterations 2
     ### Cbc0038I Pass  25: suminf.    0.20169 (2) obj. 4.50011 iterations 16
     ### Cbc0038I Pass  26: suminf.    0.20169 (2) obj. 4.50011 iterations 5
     ### Cbc0038I Pass  27: suminf.    0.16517 (1) obj. 4.50011 iterations 10
     ### Cbc0038I Pass  28: suminf.    0.08913 (1) obj. 4.50011 iterations 2
     ### Cbc0038I Pass  29: suminf.    0.60233 (2) obj. 4.50011 iterations 18
     ### Cbc0038I Pass  30: suminf.    0.08811 (1) obj. 4.50011 iterations 11
     ### Cbc0038I Pass  31: suminf.    0.23323 (1) obj. 4.50011 iterations 1
     ### Cbc0038I No solution found this major pass
     ### Cbc0038I Before mini branch and bound, 41 integers at bound fixed and 41 continuous
     ### Cbc0038I Full problem 140 rows 127 columns, reduced to 58 rows 45 columns
     ### Cbc0038I Mini branch and bound improved solution from 4.51296 to 4.51254 (0.06 seconds)
     ### Cbc0038I Round again with cutoff of 4.477
     ### Cbc0038I Pass  31: suminf.    0.60900 (3) obj. 4.477 iterations 0
     ### Cbc0038I Pass  32: suminf.    0.24490 (1) obj. 4.477 iterations 70
     ### Cbc0038I Pass  33: suminf.    0.04369 (1) obj. 4.477 iterations 2
     ### Cbc0038I Pass  34: suminf.    0.33642 (3) obj. 4.477 iterations 14
     ### Cbc0038I Pass  35: suminf.    0.19545 (2) obj. 4.477 iterations 4
     ### Cbc0038I Pass  36: suminf.    0.13269 (1) obj. 4.477 iterations 40
     ### Cbc0038I Pass  37: suminf.    0.11004 (1) obj. 4.477 iterations 2
     ### Cbc0038I Pass  38: suminf.    0.30627 (3) obj. 4.477 iterations 15
     ### Cbc0038I Pass  39: suminf.    0.19457 (2) obj. 4.477 iterations 9
     ### Cbc0038I Pass  40: suminf.    0.12205 (1) obj. 4.477 iterations 26
     ### Cbc0038I Pass  41: suminf.    0.10859 (1) obj. 4.477 iterations 2
     ### Cbc0038I Pass  42: suminf.    1.10012 (3) obj. 4.477 iterations 23
     ### Cbc0038I Pass  43: suminf.    0.07787 (1) obj. 4.477 iterations 18
     ### Cbc0038I Pass  44: suminf.    0.27724 (1) obj. 4.477 iterations 35
     ### Cbc0038I Pass  45: suminf.    0.85902 (5) obj. 4.477 iterations 19
     ### Cbc0038I Pass  46: suminf.    0.85902 (5) obj. 4.477 iterations 4
     ### Cbc0038I Pass  47: suminf.    0.31111 (1) obj. 4.477 iterations 29
     ### Cbc0038I Pass  48: suminf.    0.05630 (1) obj. 4.477 iterations 2
     ### Cbc0038I Pass  49: suminf.    0.28619 (3) obj. 4.477 iterations 13
     ### Cbc0038I Pass  50: suminf.    0.28619 (3) obj. 4.477 iterations 9
     ### Cbc0038I Pass  51: suminf.    0.28707 (1) obj. 4.477 iterations 30
     ### Cbc0038I Pass  52: suminf.    0.07133 (1) obj. 4.477 iterations 2
     ### Cbc0038I Pass  53: suminf.    0.59605 (3) obj. 4.477 iterations 16
     ### Cbc0038I Pass  54: suminf.    0.18702 (2) obj. 4.477 iterations 11
     ### Cbc0038I Pass  55: suminf.    0.19341 (1) obj. 4.477 iterations 25
     ### Cbc0038I Pass  56: suminf.    0.09837 (1) obj. 4.477 iterations 1
     ### Cbc0038I Pass  57: suminf.    0.46631 (3) obj. 4.477 iterations 12
     ### Cbc0038I Pass  58: suminf.    0.11138 (1) obj. 4.477 iterations 9
     ### Cbc0038I Pass  59: suminf.    0.14123 (1) obj. 4.477 iterations 1
     ### Cbc0038I Pass  60: suminf.    0.15540 (2) obj. 4.477 iterations 7
     ### Cbc0038I No solution found this major pass
     ### Cbc0038I Before mini branch and bound, 40 integers at bound fixed and 40 continuous
     ### Cbc0038I Full problem 140 rows 127 columns, reduced to 60 rows 47 columns
     ### Cbc0038I Mini branch and bound did not improve solution (0.08 seconds)
     ### Cbc0038I After 0.08 seconds - Feasibility pump exiting with objective of 4.51254 - took 0.06 seconds
     ### Cbc0012I Integer solution of 4.5125434 found by feasibility pump after 0 iterations and 0 nodes (0.08 seconds)
     ### Cbc0038I Full problem 140 rows 127 columns, reduced to 30 rows 18 columns
     ### Cbc0031I 4 added rows had average density of 32.5
     ### Cbc0013I At root node, 25 cuts changed objective from 4.3845733 to 4.5125434 in 1 passes
     ### Cbc0014I Cut generator 0 (Probing) - 0 row cuts average 0.0 elements, 9 column cuts (9 active)  in 0.000 seconds - new frequency is 1
     ### Cbc0014I Cut generator 1 (Gomory) - 6 row cuts average 32.7 elements, 0 column cuts (0 active)  in 0.000 seconds - new frequency is 1
     ### Cbc0014I Cut generator 2 (Knapsack) - 2 row cuts average 21.5 elements, 0 column cuts (0 active)  in 0.001 seconds - new frequency is 1
     ### Cbc0014I Cut generator 3 (Clique) - 0 row cuts average 0.0 elements, 0 column cuts (0 active)  in 0.000 seconds - new frequency is -100
     ### Cbc0014I Cut generator 4 (MixedIntegerRounding2) - 9 row cuts average 72.3 elements, 0 column cuts (0 active)  in 0.001 seconds - new frequency is 1
     ### Cbc0014I Cut generator 5 (FlowCover) - 0 row cuts average 0.0 elements, 0 column cuts (0 active)  in 0.000 seconds - new frequency is -100
     ### Cbc0014I Cut generator 6 (TwoMirCuts) - 8 row cuts average 32.4 elements, 0 column cuts (0 active)  in 0.000 seconds - new frequency is -100
     ### Cbc0001I Search completed - best objective 4.512543398463754, took 0 iterations and 0 nodes (0.09 seconds)
     ### Cbc0035I Maximum depth 0, 0 variables fixed on reduced cost
     ### Cuts at root node changed objective from 4.38457 to 4.51254
     ### Probing was tried 1 times and created 9 cuts of which 0 were active after adding rounds of cuts (0.000 seconds)
     ### Gomory was tried 1 times and created 6 cuts of which 0 were active after adding rounds of cuts (0.000 seconds)
     ### Knapsack was tried 1 times and created 2 cuts of which 0 were active after adding rounds of cuts (0.001 seconds)
     ### Clique was tried 1 times and created 0 cuts of which 0 were active after adding rounds of cuts (0.000 seconds)
     ### MixedIntegerRounding2 was tried 1 times and created 9 cuts of which 0 were active after adding rounds of cuts (0.001 seconds)
     ### FlowCover was tried 1 times and created 0 cuts of which 0 were active after adding rounds of cuts (0.000 seconds)
     ### TwoMirCuts was tried 1 times and created 8 cuts of which 0 were active after adding rounds of cuts (0.000 seconds)
     ### ZeroHalf was tried 1 times and created 0 cuts of which 0 were active after adding rounds of cuts (0.000 seconds)     ### 

     ### Result - Optimal solution found     ### 

     ### Objective value:                4.51254340
     ### Enumerated nodes:               0
     ### Total iterations:               0
     ### Time (CPU seconds):             0.10
     ### Time (Wallclock seconds):       0.10     ### 

     ### Option for printingOptions changed from normal to all
     ### Total time (CPU seconds):       0.11   (Wallclock seconds):       0.11     ### 

     ### Total cost per day per one member of the army with constraints is $3.98     ### 

     ### Process finished with exit code 0