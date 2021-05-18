# Blowing up composite numbers

##short explanation:

*Disclaimer*: prime numbers are being excluded as being extreme (in the terms of what is described below) and not bringing much useful information via the described method.

Composite numbers have one or more factorizations.
Example:
12 =
* 12
* 2 x 6
* 2 x 2 x 3

Each of the factorizations represents an n-dimentional cube, where n is the number of factors in that particular factorization. Each  n-cube for the same composite number can be said to have the same volume (in this example 12) and can also be assigned value for surface.

Let's have a look only at the prime factorizations of composite objects - in this case 2 x 2 x 3.
This object has volume of 12 and a surface of 26.

Consider blowing up a non-elastic baloon. Blowing up a rigid airtight membrane is a process of trying to make it encompass as larger volume as possible, when you have a fixed surface.

Our case with composite objects is the reverse - trying to maximimze the surface of a fixed volume.

The n-dimentional object, produced by projecting each factor of a composite object into a separate dimention is one such blown up membrane. All factorizations have the same volume, but have different surface areas. Switching through the different factorization objects of the same volume while increasing the surface area is like trying to blow up the membrane that holds that volume as much as possible. If effect the volume will try to redistribute itself such that the surface area is as large as possible.
In the 12 example let's start with
* 12, surface area (tricky for a 1D volume) - 12 (only one face, measure 12)
* blow it up a bit and the object becomes 2 x 6, surface area 16 (essentially the perimeter of a rectangle of 2 x 6)
* blow it up even more to a 2 x 2 x 3 and the surface area becomes 26

It is not hard to show that the more factors you use, the larger the area. Which means that the prime factorization has the largest surface area for object of that volume, i.e. this particular object for that number is the closest as you can get to a perfect n-cube with that volume.
The prime factorization of each composite number is the factorization that has the most factors for that number (you can produce each other factorization of the number by multiplying two or more prime factors together, which reduces their total number)

This all means that the prime factorization of the composite number gives the dimentions of the most 'blown up' possible object of that volume.

What next.

It is clear that 2 x 2 x 3 is not the most symmetrical object ever, but that's a close to symmetry as it can be done with volume 12.
On the other hand, 8 blows up to a perfect n-cube - each dimention reading a value of 2.

So we can make a comparison between composite objects, based on the symmetry of their prime factorization n-cubes.

As a comparison tool, let's calculate and assicg a value to that symmetry. The chosen methos is the following:
* calculate the prime factors of the number
* calculate their mean - this represents the dimentions of a perfectly symmetrical n-cube of that volume, if non-integer magnitudes of the sides were allowed
* calculate the deviation of each side, compared to the mean factor
* get the mean of the deviations
  
If we use this method to compare two of the factorizations of 12, we'll see that
2 x 6 has a mean deviation of 4, while
2x 2x 3 has a mean deviation of 3.25 - the most symmetrical n-cube 12 can do
(of course, 8 has a mean deviation of 0, because all of it's factors are equal, i.e. they equal the mean)

Now we can make a comparison between sets of composite numbers.

List the numbers, calculate the mean deviations and plot them.

---
## notes on the data and the graph

**antislope**
As an additional piece of data I added the slope for each data point. However in the early iterations I mistakenly calculated that slope in reverse - run / rise. And it's good that I did, cause the values of that antislope are directly linked to the form of the graph - those lines that can be seen are (almost) described by the antislope.

All points on the top line have antislopes that are very very very close to 4.
They start at 4.471 at the first one (the number 38), then 4.381 (for 46), then close and closer to 4 with the value converging to 4 slower and slower. The antisplot drops below 4.1 at 166 and it drops below 4.01 at 1706. From there on the number of numbers with an antislope close to 4 that share an exact antislope becomes larger and larger (a lot of such numbers with antislope 4.003, even more with 4.002 and so on.). I haven't explored yet that part - the rate of convergence of the antislope.

There are similar lines below the top one that converge on higher antislopes - the next one being 6, then 9, then 10 and so on (I'haven't looked for the pattern yet).

Antislope as a function of prime factorization composition.
All numbers with antislope converging to 4 are a product of an even and a prime. Similarily the numbers wiht antislope close to 3 are a product of 3 and a prime. The antislope 9 numbers are 2 x 2 x prime.

I haven't explored any of that yet, but there are two linked and very clear patterns.
Antislope   Prime factors (P - larger prime)
4           2, P
6           3, P
9           2, 2, P
10          5, P
13          2, 3, P
14          7, P
(continues)
I haven't extracted more at this point from the patterns, nor have I made attemt to analize them yet.

---
## notes on the code

**beware**: this code has not been optimized; 1-10000 takes 7 seconds to run, but I am yet to gather the patience to wait for a 1-100000 run