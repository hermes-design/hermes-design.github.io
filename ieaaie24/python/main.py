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
import BayesianNetwork
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
# Read the CSV file into a pandas DataFrame

from sklearn.preprocessing import LabelEncoder
data = pd.read_csv('attack_dataset.csv')


target ='success'
variable ='type'

# Read the CSV dataset
df = pd.read_csv("attack_dataset.csv")
# Convert the dataset to a pandas DataFrame
#df = pd.DataFrame(dataset[1:], columns=dataset[0])
# Convert boolean features to integer (0 or 1)
#df[variable] = df[variable].astype(int)


df[variable] = df[variable].replace('Mirai attacks', 0)
df[variable] = df[variable].replace('MITM ARP spoofing', 1)
df[variable] = df[variable].replace('DDoS', 2)
# Convert boolean features to integer (0 or 1)
df[[variable, target]] = df[[variable, target]].astype(int)

# Map the variable column to a categorical variable
#df[variable] = pd.Categorical(df[variable])

# Encode the categorical target variable into numerical labels
label_encoder = LabelEncoder()
df[target] = label_encoder.fit_transform(df[target])

# Split the dataset into features (variable) and target (target)
X = df[[variable]]
y = df[target]

# Initialize the decision tree classifier with balanced class weights
clf = DecisionTreeClassifier(criterion='entropy')


# Train the classifier on the dataset
clf.fit(X, y)

# Calculate the rate of the target variable
# = df['S4'].value_counts(normalize=True)

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

#print(tree_text)
#print(tree_text)


tree = clf.tree_


def learn_prism_commands(node_id, class_probabilities,at):
    propb = class_probabilities[0]
    LEFT = []
    for elt in range(0, len(X.columns)):
        if variable == X.columns[elt]:
            LEFT.append(X.columns[elt] + '=' + str(at))
        else:
            LEFT.append(X.columns[elt] + '=1')
    separator = " & "  # Specify the separator you want to use
    merged_left = separator.join(LEFT)
    RIGHT = []
    for elt in range(0, len(propb)):
        if propb[elt] != 0:
            RIGHT.append(str(propb[elt]) + ':(' + target + "'=" + str(elt) + ")  & (done'=0)")
    separator = " + "  # Specify the separator you want to use
    merged_right = separator.join(RIGHT)
    return f"[rule{node_id}] {merged_left} & (done=1)-> {merged_right};"

def learn_prism_module_variable( ):
    list_of_variable=[]
    for elt in range(0, len(X.columns)):
        if variable != X.columns[elt]:
            list_of_variable.append(X.columns[elt] +' : [0..1] init 1 ;')
    list_of_variable.append(target + ' : [-1..1] init -1 ;')
    list_of_variable.append('done : [0..1] init 1 ;')
    return list_of_variable
listOfCommands=[]
# Define a function to recursively traverse the decision tree and calculate weighted probability
def traverse_tree(node_id=0, depth=0, parent_probability=1.0, at=0):

    indent = "  " * depth
    if tree.feature[node_id] != -2:  # If not a leaf node
        feature = tree.feature[node_id]
        threshold = tree.threshold[node_id]
        #print(f" if no AT:")
        traverse_tree(tree.children_left[node_id], depth + 1, parent_probability * tree.weighted_n_node_samples[node_id] / tree.weighted_n_node_samples[0], at)
        #print(f"{indent}else:")
        traverse_tree(tree.children_right[node_id], depth + 1,  parent_probability * tree.weighted_n_node_samples[node_id] / tree.weighted_n_node_samples[0], at+1)
    else:  # If a leaf node
        class_probabilities = tree.value[node_id] / np.sum(tree.value[node_id])
        listOfCommands.append(learn_prism_commands(node_id,class_probabilities,at))


MODELNAME ="mdp "
CONST ="const int " + variable+ ";"
MODULE ="module GeneratedDecisiontree"
ENDMODULE="endmodule"
list_of_variable=learn_prism_module_variable ()
traverse_tree( )





file = open("tree.nm", "w")


file.write(MODELNAME + '\n \n')
file.write(CONST + '\n')
file.write(MODULE + '\n')
for elt in list_of_variable:
    file.write(elt + '\n')

for elt in listOfCommands:
    file.write(elt + '\n')
file.write(ENDMODULE + '\n')

# Close the file
file.close()