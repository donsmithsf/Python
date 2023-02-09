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

# Output
### To view output, see [Don Smith: Introduction to Statistical Modeling - Output for Assignment 7](https://docs.google.com/spreadsheets/d/1DGON7YnkGloxX6BoiZYTZGeddXUaAxyT3fG-iJ8WRps/edit?usp=sharing).
