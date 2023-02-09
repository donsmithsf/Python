### This is an answer written in Python that is part of a larger assignment written in R. To view that assignment, see separate file entitled [Introduction to Statistical Modeling - Assignment 6](https://link-url-here.org).


# Question 13.2

# In this problem you, can simulate a simplified airport security system at a 
# busy airport. Passengers arrive according to a Poisson distribution with 
# λ1 = 5 per minute (i.e., mean interarrival rate μ1 = 0.2 minutes) to the 
# ID/boarding-pass check queue, where there are several servers who each have 
# exponential service time with mean rate μ2 = 0.75 minutes. [Hint: model them 
# as one block that has more than one resource.] After that, the passengers are 
# assigned to the shortest of the several personal-check queues, where they go 
# through the personal scanner (time is uniformly distributed between 0.5 
# minutes and 1 minute). Use the Arena software (PC users) or Python with 
# SimPy (PC or Mac users) to build a simulation of the system, and then 
# vary the number of ID/boarding-pass checkers and personal-check queues to 
# determine how many are needed to keep average wait times below 15 minutes. 
# [If you’re using SimPy, or if you have access to a non-student version of 
# Arena, you can use λ1 = 50 to simulate a busier airport.]



# Importing necessary packages

import random
import simpy


# Defining system attributes

number_of_checkers  = 10 # number_of_checkers = number of boarding pass checkers
number_of_scanners = 25 # number_of_scanners = number of scanners
r_seed = 500

# Setting rates

passenger_arrival_rate = 5 # passenger_arrival_rate is arrival of passengers per minute
passenger_check_rate = .75 # passenger_check_rate is check time in minutes per passenger
min_scan_time = .5 # Minimum scanner time - uniform distribution
max_scan_time = 1.0 # Maximum scanner time - uniform distribution

# Setting simulation parameters

sim_run_time = 100 # In minutes
sim_reps = 100 # Number of simulation repetitions 

# Initializing variables to 0 for later use

check_wait_time = 0
scanner_wait_time = 0
system_wait_time = 0
total_wait_time= 0
time_checker = 0
complete_time_checker = 0
time_scanner = 0 
complete_time_scanner = 0
passenger_count = 0

# Creating simulation

# Airport simulation, including checkers and scanners
class Airport(object):

    # Define checkers and scanners
    def __init__(self, sim_environ):

        # Simulation environment
        self.sim_environ = sim_environ

        # Initialize checkers as resource
        self.checker = simpy.Resource(sim_environ, number_of_checkers)

        # Initialize scanner as resource, with each scanner having its own queue
        self.scanners = []
        for i in range(0,25):
            resource = simpy.Resource(sim_environ, capacity = 1)
            self.scanners.append(resource)


    # Set how long it takes for a passenger to get to the checkout
    def check(self, passenger):
        yield self.sim_environ.timeout(random.expovariate(1/passenger_check_rate))


    # Set how long it takes for a passenger to scan in
    def scan(self, passenger):
        yield self.sim_environ.timeout(random.uniform(max_scan_time, min_scan_time))

# Define how a passenger navigates through the system, both scanning and checking in
def passenger(sim_environ, name, s): 

    # Initalizing global variables. Resulting answers will be stored in these variables
    global check_wait_time
    global scanner_wait_time
    global system_wait_time
    global timeWait
    global time_checker
    global complete_time_checker
    global time_scanner
    global complete_time_scanner
    global passenger_count

    # Passanger arrival time
    arrival_time = sim_environ.now
    print('%s arrives at time %.2f' % (name, arrival_time))

    with s.checker.request() as request:
        yield request
        print('check queue length = %d' % len(s.checker.queue))

        # Passenger arrives at checker
        time_checker = sim_environ.now
        print('%s gets to checker at time %.2f' % (name, time_checker))

        yield sim_environ.process(s.check(name))

        # Passenger completes check in
        complete_time_checker = sim_environ.now
        print('%s complete checker at time %.2f' % (name, complete_time_checker))

    min_q = 0

    with s.scanners[min_q].request() as request:
        yield request
        print('scanner queue length = %d' % len(s.scanners[min_q].queue))

        for i in range(1, number_of_scanners):
            if (len(s.scanners[i].queue) < len(s.scanners[min_q].queue)):
                min_q = i

        # Passenger arrives at scanner
        time_scanner = sim_environ.now
        print('%s gets to scanner at time %.2f' % (name, time_scanner))

        yield sim_environ.process(s.scan(name))

        complete_time_scanner = sim_environ.now
        print('%s complete scanner at time %.2f' % (name, complete_time_scanner))


    # Total time at the end of entire process
    exit_time = sim_environ.now
    print('%s gets to complete system time %.2f' % (name, exit_time))
    
    system_wait_time = system_wait_time + (exit_time - arrival_time)
    check_wait_time = check_wait_time + (time_checker - arrival_time)
    scanner_wait_time = scanner_wait_time + (complete_time_scanner - complete_time_checker)
    total_wait_time = (check_wait_time + scanner_wait_time)

def setup(sim_environ):

    airport = Airport(sim_environ)

    i = 0

    while True:
        yield sim_environ.timeout(random.expovariate(1.0 / passenger_check_rate))
        i += 1
        sim_environ.process(passenger(sim_environ, 'Passenger %d' % i, airport))


# Variables that simulations values will be stored in

avg_wait_time = []
avg_check_time = []
avg_scan_time = []
avg_sys_time = []

# Iterate through simulation 

for i in range(0, sim_reps):

    sim_environ = simpy.Environment()
    sim_environ.process(setup(sim_environ))
    sim_environ.run(until = sim_run_time)
    
    avg_wait_time.append(total_wait_time) 
    avg_check_time.append(check_wait_time)
    avg_scan_time.append(scanner_wait_time)
    avg_sys_time.append(system_wait_time)
    
    passenger_count = 0
    system_wait_time = 0
    check_wait_time = 0
    scanner_wait_time = 0
    total_wait_time= 0
    
    
sim_wait_avg = sum(avg_wait_time) / sim_reps
sim_check_avg = sum(avg_check_time) / sim_reps
sim_scan_avg = sum(avg_scan_time) / sim_reps
sim_sys_time = sum(avg_sys_time) / sim_reps

# Results

print('Average cummulative wait time: ' + str(round(sim_wait_avg, 2)))
print('Average cummulative check time: ' + str(round(sim_check_avg, 2)))
print('Average cummulative scan time: ' + str(round(sim_scan_avg, 2)))
print('Average cummulative system time: ' + str(round(sim_sys_time, 2)))


# Output
### To view output, see [Don Smith: Introduction to Statistical Modeling - Output for Assignment  6 - Question 13.2](https://docs.google.com/spreadsheets/d/1YEwEPPcaHNVDLRbhXzpQ2-oxV-Fihm1NyzewMplsIlE/edit?usp=sharing).