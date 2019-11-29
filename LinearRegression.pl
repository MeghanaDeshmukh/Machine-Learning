#!/perl/bin/perl

sub GetErrorAndGradient 
{
	my $arg = shift;
	my $y1 = shift;
	my $file = shift;
	my $ipLen = shift;
	my @weights = @{$arg};
	my @gradient;
	my $data;
	my $error, $sqErr = 0, $errSum =0, $tot=0;
	my $data;
	
	## Open the file
	if (!($file)) {
		print "Please enter the Input file Name along with path\n";
		exit;
	}
	open($data, '<', $file) or die "Could not open '$file' $!\n";
	
	## While the training examples are present.
	while (my $line = <$data>) {
		$tot++;
		chomp($line);
		my @fields = split("," , $line);
		if ($ipLen != $#fields+1) {
			print "Error in data at line '$tot'. Aborting\n";
			close $file;
			exit;
		}
		
		## Last field in the input is actual y.
		my $y = $fields[$#fields];
		
		
		## CAlculate the predicted y for the given weights.
		$y1 = $weights[0]; ## $weight[0] is a intercept and is always constant.
		for (my $i =0; $i < $ipLen -1; $i++) {
			$y1 += $weights[$i+1] * $fields[$i];
		}
		
		# Calculate the error for the 
		# given weights and for each training example.
		$error = $y - $y1;
		$sqErr += ($error * $error);
		
		## Get the gradient for the each xi gradient = sum of xi*error
		## for i = 0 to N; N being the size of the data.(training examples)
		for (my $i =0; $i < $ipLen; $i++) {
			$gradient[$i+1] += $error * $fields[$i];
		}
		$errSum += $error;
	}
	$gradient[0] = $errSum; ## Gradient for constant will be sum of errors
	return ($sqErr, @gradient);
}

int main 
{
	my $file = $ARGV[0];
	my $thre = $ARGV[1];
	my $eta = $ARGV[2];
	my $data;
	
	## Open the file and read the first line.
	if (!($file)) {
		print "Please enter the Input file Name along with path\n";
		exit;
	}
	open($data, '<', $file) or die "Could not open '$file' $!\n";
	my $line = <$data>;
	close $file;
	

	if ($thre == '' || $eta == '') {
		print "Please provide all the inputs and run the program in the form\n";
		print "perl PA1.pl <IP_fileName> <Threshold> <learning rate>\n";
		exit;
 	}
	
	my $ipLen, $errSum =0 ,$itr = 0;
	my $y =0, $y1 = 0, $error = 0, $i = 0;
	my @weightArray = 0, @gA;
	my $sqError = 0, $prevSqErr=0;
	
	## Open the output file to print the output.
	my $OPfile = 'solution.csv';
	open(my $fh, '>', $OPfile) or die "Please close the Output file $OPfile or copy to another file to proceed \n";
	
	
	#get the input into array
	chomp($line);
	my @fields = split("," , $line);
	
	#Get the lenght of the function.
	$ipLen = $#fields+1;
	
	##Initialize the weights to 0
	for ($i = 0; $i < $ipLen; $i++) {
		$weightArray[$i] =0;
	}
	
	while (1) {
		## Prepare the output.
		my $output = $itr;
		$i = 0;
		for ($i = 0; $i < $ipLen; $i++) {
			$output = $output . ",".$weightArray[$i];
		}	
		$itr ++;
		
		## To compare the prev and the curr errors.
		$prevSqErr = $sqError;
		($sqError, @gA) = GetErrorAndGradient(\@weightArray, $y1, $file, $ipLen);
	
		## Calculate weights
		for ($i = 0; $i < $ipLen; $i++) {
			$weightArray[$i] = $weightArray[$i] + ($eta * $gA[$i]);
		}
		
		## Print the output.
		$output = $output . ",".$sqError;
		print $output."\n";
		print $fh $output."\n";
		
		my $diff = $prevSqErr - $sqError;
		if ( ($itr > 1) && ($thre > abs($prevSqErr - $sqError)) ) {
			#print "threshold reached\n";
			close $fh;
			exit;
		}	
		if (($itr > 1) && ($sqError > $prevSqErr)) {
			print "The error is increasing. Previous error: $prevSqErr  Current error: $sqError\n";
			print "Restart the program with the reduced learning rate to converge \n";
			exit;
		}
	}
	close $fh;
	exit;
}

main();