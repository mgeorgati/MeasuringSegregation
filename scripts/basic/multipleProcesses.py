import multiprocessing
from datetime import datetime 

def multiple():
    # Create a list of numbers
    numbers = list(range(1, 10001))

    # Create a multiprocessing.Queue to store the output
    output = multiprocessing.Queue()

    # Divide the list of numbers into chunks
    num_chunks = 4
    chunk_size = len(numbers) // num_chunks
    chunks = [numbers[i:i+chunk_size] for i in range(0, len(numbers), chunk_size)]
    print('proce')
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
    # Create a list of processes
    processes = []
    for chunk in chunks:
        p = multiprocessing.Process(target=square_numbers, args=(chunk, output))
        processes.append(p)
    print('proce1111')
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
    # Start the processes
    for p in processes:
        p.start()
    print('______________________')
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
    # Wait for the processes to finish
    for p in processes:
        p.join()
    
    print('proce--------')
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

    # Get the output from the queue
    results = []
    while not output.empty():
        result = output.get()
        results.append(result)

    # Print the results
    print(results)


def square_numbers(numbers, output):
    for num in numbers:
        output.put(num*num)


    