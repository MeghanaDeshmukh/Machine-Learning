import sys
import csv

def getError(dataFile, weights, weights1, dataLen):
	totErr = 0;
	totErr1 =0;
	sum = 0;
	asum = 0;
	gradients = [0 for x in range (dataLen+1)]
	gradients1 = [0 for x in range (dataLen+1)]
	with open(dataFile, 'r') as csvfile:
			spamreader = csv.reader(csvfile, delimiter='	');
			for row in spamreader:
				if (row.count('') > 0):
					row.remove('');
				if (row[0] is 'A'):
					y=1;
				else:
					y=0;
				
				## Calculate error for the trainig sample for normal
				sum = weights[0];
				for x in range (1,len(row)):
					sum += weights[x] * float(row[x]);
				if (sum > 0):
					y1 = 1;
				else:
					y1 = 0;
				
				if (y != y1):
					totErr = totErr+1;
				## Calculate gradients.
				for x in range (0,len(row)):
					if (x==0):
						gradients[x] += (y-y1);
					else:
						gradients[x] += (y-y1)*float(row[x])
		
				## Calculations for annealing
				asum = weights1[0];
				for x in range (1,len(row)):
					asum += weights1[x] * float(row[x]);
				if (asum > 0):
					ay1 = 1;
				else:
					ay1 = 0;
				
				if (y != ay1):
					totErr1 += 1;
				## Calculate gradients.
				for x in range (0,len(row)):
					if (x==0):
						gradients1[x] += (y-ay1);		
					else:
						gradients1[x] += (y-ay1)*float(row[x]);
						
	return (totErr, totErr1, gradients, gradients1);
		

def main():
	dataFile = sys.argv[1];
	opFile = sys.argv[2];
	dataLen = 0;
	
	totErr =0;
	totErr1 = 0;
	
	## Eta for normal and annealing
	eta = 1;
	annEta = 1;
	## threshold is 100 iterations
	thre = 100;
	
	## output for both normal and annealing
	output = '';
	output1 = '';
	winout = '';
	winout1 = '';
	
	## Open the file in read mode and with the delimiter ','
	with open(dataFile, 'r') as csvfile:
		spamreader = csv.reader(csvfile, delimiter='	');
		for row in spamreader:
			if (row.count('') > 0):
				row.remove('');
			dataLen = len(row)-1;
			
	## Declare the weights after getting the length		
	weights = [0 for x in range (dataLen+1)]
	gradients = [0 for x in range (dataLen+1)]
	## For Annealing
	weights1 = [0 for x in range (dataLen+1)]
	gradients1 = [0 for x in range (dataLen+1)]
	
	for i in range (0,101):
		(totErr, totErr1, gradients, gradients1)=getError(dataFile, weights, weights1, dataLen);
		
		if (i==0):
			output = str(totErr);
			output1 = str(totErr1);
		else:
			output = output + "\t" +str(totErr); 
			output1 = output1 + "\t" +str(totErr1); 
			annEta = eta/(i+1);
			
		winout = str(i);
		winout1 = str(i);
		for x in range (0,dataLen+1):
			winout = winout+","+str(weights[x]);
			winout1 = winout1+","+str(weights1[x]);
			weights[x] = weights[x] + (gradients[x] * eta);
			weights1[x] = weights1[x] + (gradients1[x] * annEta);
			
		
		winout = winout+","+str(totErr);
		winout1 = winout1+","+str(totErr1);
		print(winout);
		print(winout1);
	output = output+"\n"+output1;
	## Writing to a file.
	fh = open(opFile, "w");
	fh.write(output);
		
	

main();