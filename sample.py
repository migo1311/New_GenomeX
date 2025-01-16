_G dose Result; 

act Add(dose Num1, dose Num2) {
    _L dose Sum = Num1 + Num2;
    prod Sum; 
}

act Subtract(dose Num1, dose Num2) {
    _L dose Difference = Num1 - Num2;
    prod Difference; 
}


act gene() {
    seq Input = stimuli("Enter a string: ");
    dose Length = 0;
    allele IsPalindrome = dom ;

    # Calculate the length of the string manually
    while (Input[Length] != " ") {
        Length++ ;
    }

    # Check if the string is a palindrome
    for (dose I = 0; I < Length / 2; I++ ) {
        if (Input[I] != Input[Length - I - 1]) {
            IsPalindrome = rec ;
            contig;
        }
    }

    if (IsPalindrome == dom) {
        express("The string " + Input + "is a palindrome.");
    } else {
        express("The string " + Input + "is not a palindrome.");
    }

}


##################################################################################

act gene() {
    dose Num1 = stimuli("Enter the first number: ");
    dose Num2 = stimuli("Enter the second number: ");
    dose Sum = Num1 + Num2;
    express("The sum is: " + seq(Sum));
    prod 0;
}
##################################################################################


act gene() {
    clust dose Numbers[2][3] = {
        {1, 2, 3},
        {4, 5, 6}
    }; # Initialize a 2x3 2D array

    dose Sum = 0;

    for (dose Row = 0; Row < 2; Row++) {
        for (dose Col = 0; Col < 3; Col++) {
            Sum += Numbers[Row][Col]; # Add each element to Sum
        }
    }

    express("The sum of all elements in the 2D array is: " + seq(Sum));
    prod 0;
}


##################################################################################

act gene() {
    perms dose SecretNumber = 7; # Constant value for the number to guess
    dose Guess;
    dose Attempts = 0;

    express("Welcome to the Number Guessing Game!");

    while (dom) { # Infinite loop, will break when guessed correctly
        Guess = stimuli("Enter your guess (1-10): ");
        Attempts++;

        if (Guess == SecretNumber) {
            express("Congratulations! You guessed the correct number in " + seq(Attempts) + " attempts.");
            destroy; # Exit the loop
        } elif (Guess < SecretNumber) {
            express("Too low! Try again.");
        } else {
            express("Too high! Try again.");
        }
    }

    prod 0;
}

##################################################################################

act gene() {
    perms dose TotalUnits = 18; # Total number of units
    dose Grade1 = stimuli("Enter grade for Subject 1: ");
    dose Units1 = stimuli("Enter units for Subject 1: ");
    
    dose Grade2 = stimuli("Enter grade for Subject 2: ");
    dose Units2 = stimuli("Enter units for Subject 2: ");
    
    dose Grade3 = stimuli("Enter grade for Subject 3: ");
    dose Units3 = stimuli("Enter units for Subject 3: ");
    
    dose WeightedSum = (Grade1 * Units1) + (Grade2 * Units2) + (Grade3 * Units3);
    dose TotalUnits = Units1 + Units2 + Units3;
    
    quant GWA = WeightedSum / TotalUnits;
    express("Your Grade Weighted Average (GWA) is: " + seq(GWA));
    
    prod 0;
}


# sdsadassdsadasdsadsadsadsadasdasdasdasdasdas
# sdsadassdsadasdsadsadsadsadasdasdasdasdasdas
# sdsadassdsadasdsadsadsadsadasdasdasdasdasdas
#even
act gene() {
    dose Number = stimuli("Enter a number: ");
    
    if (Number % 2 == 0) {
        express(seq(Number) + " is even.");
    } else {
        express(seq(Number) + " is odd.");
    }

    prod 0;
}

# max

act gene() {
    dose Num1 = stimuli("Enter the first number: ");
    dose Num2 = stimuli("Enter the second number: ");
    
    if (Num1 > Num2) {
        express(seq(Num1) + " is greater.");
    } else {
        express(seq(Num2) + " is greater.");
    }

    prod 0;
}

# natural
act gene() {
    dose N = stimuli("Enter a number N: ");
    dose Sum = 0;

    for (dose i = 1; i <= N; i++) {
        Sum += i;
    }

    express("The sum of the first " + seq(N) + " natural numbers is: " + seq(Sum));
    prod 0;
}

# basic cal``
act gene() {
    dose Num1 = stimuli("Enter the first number: ");
    dose Num2 = stimuli("Enter the second number: ");
    
    dose Sum = Num1 + Num2;
    express("The sum of " + seq(Num1) + " and " + seq(Num2) + " is: " + seq(Sum));

    prod 0;
}



# check number is prime 
act gene() {
    dose Number = stimuli("Enter a number: ");
    dose IsPrime = dom;

    for (dose i = 2; i <= Number / 2; i++) {
        if (Number % i == 0) {
            IsPrime = rec;
            break;
        }
    }

    if (IsPrime == dom) {
        express(seq(Number) + " is a prime number.");
    } else {
        express(seq(Number) + " is not a prime number.");
    }

    prod 0;
}


act Is_palindrome (text):
    
    cleaned_text=
    ''.join(text.lower().split())
    return cleaned_text ==
cleaned_text[::-1]

string = input("Enter a String: ")
if Is_palindrome(string):
    print ("The string is a palindrome!")
else:
    ("The string is not a palindrome.")
    