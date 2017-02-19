

import random, time, math, sys, os, itertools, argparse

def main(args):
    '''Tests the computer multiplier by comparing a multiplication 
    of A * B to (A - p)(B - q) + pB + Aq - pq, where A, B, p, and 
    q are random numbers.  The results are certain to be equal 
    unless there is an error in the multiplier in one of the 
    circuit paths used to generate a side of the equation.'''

    error_list = [] #keep track of var combos that failed the test
                    #in tuples in a list
    start = old_time = time.time() #initialize timer

    ellipses = overflow_str = ''

    prime = 1000000 #large near-prime to step by in the loop
    
    try:
        counter = 0
        for cycle in range(args.cycles):

            #create new values for B, p, q
            B = random.randint(0, sys.maxsize / prime)
            p = random.randint(0, 1000)
            q = random.randint(0, 1000)

            #keep generating numbers by increments of original prime
            #until the system cap is reached
            for A in itertools.count(prime, prime):
                #are the sides equal? If not, track the error
                if (A * B) != (A - p)*(B - q)+(p * B)+(A * q)-(p * q):
                    error_list.append((A, B, p, q))

                #display a little cycle of '...' to show 
                #the machine working
                counter += 1
                if not args.suppress and counter % 100000 == 0: #update every second or so
                    ellipses += '.'
                    if len(ellipses) > 3:
                        ellipses = ''
                        #wipe and replace the current message
                        if sys.platform == 'win32' || sys.platform == 'win64':
                        os.system('cls')
                else:
                    os.system('clear')
                    print 'cycle: {!s} errors: {!s}'.format(cycle,
                                                        len(error_list))
                    print 'testing' + ellipses
            #make sure the prog hasn't run over the timer, if there is one
            if args.timer and (time.time() - start) > args.timer * 60:
                break

    #catch and flag overflows
    except(OverflowError):
        overflow_str = 'Overflowed! '
        

    if not args.suppress:
        final_time = time.time() - start

        if not error_list:
            error_list = 'No errors found.'

        print overflow_str + 'error_list = {}'.format(error_list[:100])
        print 'cycle = {!s}'.format(cycle)

        if 1 < final_time < 2:
            print 'time = {} second'.format(final_time)
        else:
            print 'time = {} seconds'.format(final_time)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()  
    parser.add_argument('--cycles',
                        '-c',
                        type=int,
                        default=10000,
                        help='''Enter the number of of repititions -- 
                        each repitition represents a new set 
                        of initial values for B, p, and q. A is an
                        iterating large prime number constant.
                        Each set of B, p, and q will be tested against 
                        increasing multiples of A until the system can\'t 
                        compute any more. Default is 10,000 cycles.''')
    parser.add_argument('--timer',
                        '-t',
                        type=float,
                        default=0,
                        help='''Set a maximum number of minutes for which 
                             a prog can run.  Decimals allowed.''')
    parser.add_argument('--suppress',
                        '-s',
                        action='store_true',
                        help='''Supress console output.''')
    args = parser.parse_args()
    main(args)