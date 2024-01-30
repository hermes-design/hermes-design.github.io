import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics
from sklearn.tree import export_graphviz
from sklearn import tree
import graphviz
from sklearn.tree import export_text
from sklearn.model_selection import train_test_split
import dtreeviz.trees
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import LabelEncoder

target = 'PP'
variable = ['PH', 'TM', 'WL']

# Read the CSV dataset
df = pd.read_csv("dataset.csv")

# Define the cutoff values for each level
level1_threshold = 5.0
level2_threshold = 7.0

# Categorize the PH column
df['PH'] = pd.cut(df['PH'], bins=[0, 6, 8, float('inf')], labels=[1, 2, 3])

# Categorize the TM column
df['TM'] = pd.cut(df['TM'], bins=[0, 30, 50, float('inf')], labels=[1, 2, 3])

# Categorize the WL column
df['WL'] = pd.cut(df['WL'], bins=[0, 30, 50, float('inf')], labels=[1, 2, 3])

# Save the categorized dataset to a file
df.to_csv('categorized_dataset.csv', index=False)

# Encode the categorical target variable into numerical labels
label_encoder = LabelEncoder()
df[target] = label_encoder.fit_transform(df[target])

# Split the dataset into features (variable) and target (target)
X = df[['PH', 'TM', 'WL']]
y = df[target]

# Initialize the decision tree classifier with balanced class weights
clf = DecisionTreeClassifier(criterion='entropy')

# Train the classifier on the dataset
clf.fit(X, y)

# Visualize the decision tree
dot_data = tree.export_graphviz(clf,
                               out_file=None,
                               feature_names=X.columns,
                               filled=True,
                               rounded=True,
                               special_characters=True)
graph = graphviz.Source(dot_data)
graph.render("decision_tree", format="png", cleanup=True)

# Convert the decision tree to text format
tree_text = export_text(clf, feature_names=X.columns, show_weights=True)

print(tree_text)


tree = clf.tree_

ruleId = 0


def learn_prism_commands(class_probabilities, at):
    global ruleId  # Declare 'ruleId' as a global variable to modify its value

    at = at.rsplit("&", 1)[0].strip()
    print(at)
    propb = class_probabilities[0]
    LEFT = []
    merged_left = at
    RIGHT = []
    UPDOWN = ["DOWN", "UP"]

    for elt in range(0, len(propb)):
        if propb[elt] != 0:
            RIGHT.append(str(propb[elt]) + ':(' + target + "'=" + str(UPDOWN[elt]) + ") ")

    separator = " + "  # Specify the separator you want to use
    merged_right = separator.join(RIGHT)

    ruleId += 1  # Increment the value of 'ruleId'

    return f"[rule{ruleId}] {merged_left} -> {merged_right};"


def learn_const_prism_module_variable( ):
    list_of_variable=[]
    list_of_variable.append('const double UP =1;')
    list_of_variable.append('const double DOWN =-1;')
    for elt in range(0, len(variable)):
            list_of_variable.append('const double '+ variable[elt] +';')
    return list_of_variable

def learn_prism_module_variable( ):
    list_of_variable=[]
    list_of_variable.append(target + ' : [-1..1] init 0 ;')
    return list_of_variable
listOfCommands=[]
# Define a function to recursively traverse the decision tree and calculate weighted probability
def traverse_tree(node_id=0, depth=0, parent_probability=1.0, at=""):
    indent = "  " * depth
    if tree.feature[node_id] != -2:  # If not a leaf node
        feature = tree.feature[node_id]
        threshold = tree.threshold[node_id]
        #print(tree.feature[node_id])
        at_left = at + variable[feature] + "<=" + str(threshold) +" & "
        traverse_tree(tree.children_left[node_id], depth + 1, parent_probability * tree.weighted_n_node_samples[node_id] / tree.weighted_n_node_samples[0], at_left)

        at_right = at + variable[feature]+ ">"+ str(threshold) +" & "
        traverse_tree(tree.children_right[node_id], depth + 1,  parent_probability * tree.weighted_n_node_samples[node_id] / tree.weighted_n_node_samples[0], at_right)
    else:  # If a leaf node
        class_probabilities = tree.value[node_id] / np.sum(tree.value[node_id])

        listOfCommands.append(learn_prism_commands(class_probabilities,at))


MODELNAME ="mdp "
#CONST ="const int " + variable+ ";"
MODULE ="module GeneratedDecisiontree"
ENDMODULE="endmodule"
list_of_variable=learn_prism_module_variable ()
list_of_const_variable=learn_const_prism_module_variable()
traverse_tree( )






file = open("tree.nm", "w")

file.write(MODELNAME + '\n \n')

for elt in list_of_const_variable:
    file.write(elt + '\n')



file.write(MODULE + '\n')
for elt in list_of_variable:
    file.write(elt + '\n')

for elt in listOfCommands:
    file.write(elt + '\n')
file.write(ENDMODULE + '\n')




# Close the file
file.close()