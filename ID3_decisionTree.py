import sys
import csv
import math	 	## to get the log function
import xml.etree.ElementTree as xml 


def getTheNodeValue(leafNode):
	for targetValues in leafNode:
		if (targetValues != 'Entropy'):
			return targetValues;

## Recursive Function to generate and print the tree in XML file.
def generateTree(parentEle, xmlRoot, nAttr, tIndex, logBase, total, rootNodeAttr, nextNodeName, dataArr, **rootNode):
	nextNode = {};
	param = '';
	currNode = nextNodeName;
	currParentEle = parentEle;
	for vals in rootNode:
		if (vals != "Entropy"):
			if (rootNode[vals]["Entropy"] != 0):
				## Get the next node with the minimum entropy / maximum gain.
				param = rootNodeAttr+','+vals;
				(nextNodeName, nextNodeEntropy, nextNode)= getNextNode(param, nAttr, tIndex, logBase, total, dataArr);
				
				## Print the nodes in the XML file.
				if (currParentEle == ''):
					xmlNode = xml.Element("node", entropy = str(abs(rootNode[vals]["Entropy"])), value=str(vals), feature=str(currNode));
					xmlRoot.append(xmlNode);
				else:
					xmlNode = xml.SubElement(currParentEle, "node", entropy = str(abs(rootNode[vals]["Entropy"])), value=str(vals), feature=str(currNode));
				parentEle = xmlNode;
				
				## Call the function recursively to get a tree. The function stops when entropy is 0.
				param = param + ';' +nextNodeName;
				generateTree(parentEle, xmlRoot, nAttr, tIndex, logBase, total, param, nextNodeName,  dataArr, **nextNode);
			else:
				## This is a leaf node, print in XML
				if (currParentEle == ''):  	## Leaf node of the root node.
					xmlNode = xml.Element("node", entropy = str(abs(rootNode[vals]["Entropy"])), value=str(vals), feature=str(currNode));
					xmlNode.text = str(getTheNodeValue(rootNode[vals]));
					xmlRoot.append(xmlNode);
				else:						## Leaf node of the sub-nodes
					xmlNode = xml.SubElement(currParentEle, "node", entropy = str(abs(rootNode[vals]["Entropy"])), value=str(vals), feature=str(currNode));
					xmlNode.text = str(getTheNodeValue(rootNode[vals]));
## End of function generateTree
				
				
## Function to get the next node in the tree.	
def getNextNode(rootNodeAttr, nAttr, tIndex, logBase, total, dataArr):
	path = {};
	nodeCondition = '';
	attrArr = {};
	nodes = rootNodeAttr.split(';');
	
	## Get the path of the node and form a condition so the same nodes are not selected again.
	for i in range (0,len(nodes)):
		values = nodes[i].split(',');
		path[values[0]] = values[1];
		if (i == 0):
			nodeCondition = "dataArr[j]["+values[0][3:]+"] == '"+values[1]+"'";
		else:
			nodeCondition = nodeCondition + " and " + "dataArr[j]["+values[0][3:]+"] == '"+values[1]+"'";
	
	## Traverse through the data, with the condition and populate entropy details.
	for j in range (0,total):
		if (eval(nodeCondition)):
			for i in range (0,nAttr+1):	
			## Get the data sorted; for eachattr, its val and corresponding target function.
				if ("att{0}".format(i) in attrArr.keys()) and ("att{0}".format(i) not in path.keys()):
					if dataArr[j][i] in attrArr["att{0}".format(i)].keys():
						if dataArr[j][tIndex] in attrArr["att{0}".format(i)][dataArr[j][i]].keys():
							attrArr["att{0}".format(i)][dataArr[j][i]][dataArr[j][tIndex]] = attrArr["att{0}".format(i)][dataArr[j][i]][dataArr[j][tIndex]] +1;
						else:
							attrArr["att{0}".format(i)][dataArr[j][i]][dataArr[j][tIndex]] = 1;
					else:
						attrArr["att{0}".format(i)][dataArr[j][i]] = {};
						attrArr["att{0}".format(i)][dataArr[j][i]][dataArr[j][tIndex]] = 1;
				else:
					if ("att{0}".format(i) not in path.keys()):
						attrArr["att{0}".format(i)] = {};
						attrArr["att{0}".format(i)][dataArr[j][i]] = {};
						attrArr["att{0}".format(i)][dataArr[j][i]][dataArr[j][tIndex]] = 1;
												
	## Calculate the entropy for each node. Select the node which has minimum entropy as root node.
	nextNode = 0;
	nextNodeGain = 0;
	tempIndex = 0;
	for currAttr in attrArr:
		Aentropy = 0;	
		for currAttrVal in attrArr[currAttr]:
			totSet = 0;
			subEntropy = 0;
			for key in attrArr[currAttr][currAttrVal]:
				totSet += attrArr[currAttr][currAttrVal][key];
			for key in attrArr[currAttr][currAttrVal]:
				subEntropy += (attrArr[currAttr][currAttrVal][key]/totSet) * (math.log((attrArr[currAttr][currAttrVal][key]/totSet),logBase));
			subEntropy = subEntropy * -1;
			## Entropy of each branch of a node.
			attrArr[currAttr][currAttrVal]["Entropy"] = subEntropy;
			subEntropy = subEntropy*(totSet/total);
			Aentropy += subEntropy;
		## Entropy of each node.
		attrArr[currAttr]["Entropy"] = Aentropy;
		if (Aentropy < nextNodeGain or tempIndex == 0):
			nextNodeGain = Aentropy;
			nextNode = currAttr;
		tempIndex +=1;
	return (nextNode, nextNodeGain, attrArr[nextNode]);
### End of function getNextNode	


	
## Main Function - Reads csv, copies the data to a array, gets the entropy to choose the root node.
def main():
	dataArr = [[None]]; ## Array containing the data read from the csv file. ## We can even choose to not store it.
	nAttr = 0;			## Contains the number of attributes (STARTING FROM 0) in the given csv file. Excluding the class col.
	tIndex = 0;			## Contains the index to access the target value from the data/csv file.
	logBase = 0;		## Base of the log, to compute entropy. This should be same as the unique values of the target function.
	total = 0;			## Total number of training samples in the csv through which we iterate.
	dataFile = sys.argv[1];
	opFile = sys.argv[2];
	values = 0;
	classes= {};
	attrArr = {};
	
	## Open the file in read mode and with the delimiter ','
	with open(dataFile, 'r') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',');
		## Iterate through the csv for each line
		for row in spamreader:
			if (len(row) > 0):
				nAttr= len(row)-2; ## Index from 0
				tIndex = len(row)-1;  ## Index of the target function.
	
				## Get the possible values for the target function. 			
				if row[tIndex] in classes.keys():
					classes[row[tIndex]] = classes[row[tIndex]] + 1;
				else:
					classes[row[tIndex]] = 1;
				
				## To compute Etropy.
				logBase = len(classes.keys());
			
				## Get the data sorted; for eachattr, its val and corresponding target function.
				for i in range (0,nAttr+1):
					if "att{0}".format(i) in attrArr.keys():
						if row[i] in attrArr["att{0}".format(i)].keys():
							if row[tIndex] in attrArr["att{0}".format(i)][row[i]].keys():
								attrArr["att{0}".format(i)][row[i]][row[tIndex]] = attrArr["att{0}".format(i)][row[i]][row[tIndex]] +1;
							else:
								attrArr["att{0}".format(i)][row[i]][row[tIndex]] = 1;
						else:
							attrArr["att{0}".format(i)][row[i]] = {};
							attrArr["att{0}".format(i)][row[i]][row[tIndex]] = 1;
					else:
						attrArr["att{0}".format(i)] = {};
						attrArr["att{0}".format(i)][row[i]] = {};
						attrArr["att{0}".format(i)][row[i]][row[tIndex]] = 1;
				
				## Copy the data into the array.
				i = 0;
				if (values > 0):
					dataArr.append([]);
					while (i < len(row)):
						dataArr[values].append(row[i]);
						i+=1;
				else:
					while (i < len(row)):
						if(i==0):
							dataArr[values][i]=row[i];
						else:
							dataArr[values].append(row[i]);
						i+=1;
					
				values+=1;
		## End of reading the file.
		total = values;
	
		## Calculate entropy:
		Sentropy = 0;
		for key in classes:
			Sentropy += (classes[key]/values)*(math.log((classes[key]/values),logBase));
		Sentropy = Sentropy * -1;
		
		## Calculate the entropy for each node. Select the node which has minimum entropy as root node.
		rootNode = 0;
		rootNodeGain = 0;
		tempIndex = 0;
		for currAttr in attrArr:
			#print("The unique values for attr",currAttr," are:",attrArr[currAttr].keys());
			Aentropy = 0;	
			for currAttrVal in attrArr[currAttr]:
				
				totSet = 0;
				subEntropy = 0;
				for key in attrArr[currAttr][currAttrVal]:
					totSet += attrArr[currAttr][currAttrVal][key];
				for key in attrArr[currAttr][currAttrVal]:
					subEntropy += (attrArr[currAttr][currAttrVal][key]/totSet) * (math.log((attrArr[currAttr][currAttrVal][key]/totSet),logBase));
				subEntropy = subEntropy * -1;
				## Entropy of each branch of the node.
				attrArr[currAttr][currAttrVal]["Entropy"] = subEntropy;
				subEntropy = subEntropy*(totSet/total);
				Aentropy += subEntropy;
			## Entropy of the node.
			attrArr[currAttr]["Entropy"] = Aentropy;
			if (Aentropy < rootNodeGain or tempIndex == 0):
				rootNodeGain = Aentropy;
				rootNode = currAttr;
			tempIndex +=1;
	
	print ("Entropy of training data: ",Sentropy);
	print ("Root node and it's entropy: ",rootNode,", ",rootNodeGain);
	
	## Form the XML file.
	root = xml.Element("tree", entropy=str(Sentropy));
	tree = xml.ElementTree(root);
	
	print ("\nPlease wait while further tree is formed.");
	## Here call the recursive function with the root node and its branch.
	generateTree('', root, nAttr, tIndex, logBase, total, rootNode, rootNode, dataArr, **attrArr[rootNode]);
	
	print("Decision Tree generation using the algorithm ID3 is complete.");
	### Write the XML into the file 
	with open(opFile, "wb") as fh:
		tree.write(fh)
		
	print("XML file of the decision tree is: ",opFile);
	
	## End of Main function. 
	
	
main();