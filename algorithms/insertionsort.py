
def iisort(A):
    "Sort an array using Insertion Sort"
    i = 1
    size = len(A)

    # Start the loop at the second array element
    while i < size:
        # x is the element we want to insert in its correct place
        x = A[i]

        # j keeps track of the correct place for x
        j = i - 1

        # Run through the left side of the array checking for adjacent
        # elements greater than x
        while A[j] > x and j >= 0:
            # shift the greater value one place to the right
            A[j + 1] = A[j]
            j -= 1  # keep moving left

        # when we're finished moving the elements, we position x in its correct place
        A[j + 1] = x
        i += 1  # continue to end of the array

    return A
