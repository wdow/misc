

import random, time, math, sys, os, argparse, itertools

def binary_to_decimal(bin):
    '''simple converter from base 2 to base 10'''
    if type(bin) == int:
        bin_list = [int(x) for x in str(bin)][::-1]
    else:
        bin_list = list(bin)
    dec = 0
    for x in range(len(bin_list)):
        dec += bin_list[x] * 2**x
    return dec

def check_bit_input(bit_input):
    '''quick check to see that the input won't
    produce products too big for the system architecture'''

    bit_input = int(bit_input)

    is_64bits = sys.maxsize > 2**32

    if is_64bits and (bit_input <= 64):
        return bit_input 
    elif bit_input <= 32:
        return bit_input
    else:
        raise argparse.ArgumentTypeError('{} is too big for the architecture!'.format(bit_input))

def main(args):
    '''Tests the computer multiplier by comparing a multiplication 
    of A * B to (A - p)(B - q) + pB + Aq - pq, where A, B, p, and 
    q are random numbers.  The results are certain to be equal 
    unless there is an error in the multiplier in one of the 
    circuit paths used to generate a side of the equation.'''

    #use built-in product method to generate list of all possible combinations
    #of 0 and 1 out to the specified bit number
    combinations = itertools.product([0,1],[0,1], repeat=args.bits)
    current_combination = None
    error_list = [] #keep track of var combos that fail the test
    start = time.time() #initialize timer
    ellipses = ''
    timer_flag = 'Done!'
    counter = 0

    while True:

        try:
            current_combination = next(combinations)
        except(StopIteration):
            break

        #print combinations[cycle][0:args.variables]
        A = binary_to_decimal(current_combination[0:args.bits])
        B = binary_to_decimal(current_combination[args.bits:])

        #create new values for p, q
        p = random.randint(0, 1000)
        q = random.randint(0, 1000)

        #are the sides equal? If not, track the error
        if (A * B)!=(A - p)*(B - q)+(p * B)+(A * q)-(p * q):
            error_list.append((A, B, p, q))

        #display a little cycle of '...' to show 
        #the machine working
        #(combinatorial testing is so fast that this is more or less
        #unnecessary now)
        counter += 1
        if not args.suppress and counter % 100000 == 0: #update every second or so
            ellipses += '.'
            if len(ellipses) > 3:
                ellipses = ''
            #wipe and replace the current message
            if sys.platform == 'win32':
                os.system('cls')
            else:
                os.system('clear')
            print 'current vars: A = {!s} B = {!s}\nerrors: {!s}'.format(A, B,
                                                                         len(error_list))
            print 'testing' + ellipses

        #make sure the prog hasn't run over the timer, if there is one
        if args.timer and (time.time() - start) > args.timer * 60:
            timer_flag = 'Timed out!'
            break

    if not args.suppress:

        #get final time
        final_time = time.time() - start

        if not error_list: #the multiplier is apparently not busted; who would've thought?
            error_list = 'No errors found.'

        print timer_flag + '\n' + 'error_list = {}'.format(error_list[:100])

        if 1 < final_time < 2:
            print 'time = {} second'.format(final_time)
        elif final_time < 60:
            print 'time = {} seconds'.format(final_time)
        else:
            print 'time = {} minutes, {} seconds'.format(final_time / 60,
                                                         final_time % 60)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()  
    parser.add_argument('--timer',
                        '-t',
                        type=float,
                        default=0,
                        help='''Set a maximum number of minutes for which 
                             a prog can run.  Decimals allowed. Default is no
                             timer at all.''')
    parser.add_argument('--bits',
                        '-b',
                        type=check_bit_input,
                        default=10,
                        help='''Number of bits to test, i.e. bits=4 will test
                                all combinations up to 2**4.''')
    parser.add_argument('--suppress',
                        '-s',
                        action='store_true',
                        help='''Suppress console output.''')
    args = parser.parse_args()
    main(args)