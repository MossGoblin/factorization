## How to view the prepared data from the repo

**Graph**

The main.html file in the root folder is exported by the bokeh visualization library on each run.

The 'output' folder contains three files for each run - a .csv file with the generated data, an .html file with the generated plot and a .log file with the run logs.

The main html file can be viewed by opening the following link:

https://raw.githack.com/MossGoblin/factorization/master/main.html

Keep in mind that every time I go through a new local run and push my changes to the repo, the main.html file will be replaced with the new version.

The main.html file is always the same as the html file in 'output' with the latest timestamp.

To view an html file from the output folder, do the following:

To view such a file, do the following:

1. Copy the link to the .html file from the repo - for example https://github.com/MossGoblin/factorization/blob/master/main_100000.html
2. Go to https://raw.githack.com and paste the link there
3. Copy one of the resulting URLs, preferably the one for development, and open it in your browser.

------

# Blowing up composite numbers

## Explanation of the idea

*Disclaimer*: prime numbers are not mentioned in the explanation as being extreme (in the terms of what is described below). All of the below works for them, but I don't think they bring much to the table at this point.

### Base

Composite numbers have one or more factorizations.
Example:
12 =

* 12
* 2 x 6
* 2 x 2 x 3

Each of the factorizations represents an n-dimensional cube, where n is the number of factors in that particular factorization. Each  n-cube for the same composite number can be said to have the same size (in this example 12) and can also be assigned value for surface.

*Both size and surface here are used in a general meaning. For a 2-D object, for example, 'size' is the area of the object and ''surface' is the perimeter. For 3-D 'size' is the volume and 'sufrace' is the area.*

Let's have a look only at the prime factorizations of composite objects - in this case 2 x 2 x 3.
This object has size 12 and a surface of 34.

Consider blowing up a non-elastic balloon. Blowing up a rigid air-tight membrane is a process of trying to have it encompass as larger volume as possible, when you have a fixed surface area.

Our case with composite objects is the reverse - trying to maximize the surface area of an object with a fixed size.

The n-dimensional object, produced by projecting each factor of a composite object into a separate dimension, is one such blown up membrane. All factorizations have the same size, but have different surface areas. Switching through the different factorization objects of the same size while increasing the surface area is like trying to blow up as much as possible the membrane that holds that size. If effect the size will try to redistribute itself such that the surface area is as large as possible.
In the 12 example let's start with:

* [ 12 ] , surface area = 12 (in 1 dimension the 'surface area' is the length, as we have only one 'face', measure 12)
* blow it up a bit and the object becomes [ 4 x 3 ], 'surface area' = 14 (essentially the perimeter of a rectangle of 4 x 3); It could also be [ 2 x 6 ] with 'surface area' = 16
* blow it up even more to a [ 2 x 2 x 3 ] and the 'surface area' becomes 32 (2 * 2 x 2, 4 * 2 x 3)

The prime factorization of each composite number is the factorization that has the most factors for that number - you can produce each other factorization of the number by multiplying two or more prime factors together, which reduces their total number.

And since the more factors you use, the larger the area, this means that the prime factorization has the largest surface area for object of that size, i.e. this particular n-cube for that number is the closest as you can get to a perfect n-cube with that size.

This all means that the prime factorization of the composite number gives the dimensions of the most 'blown up' possible object of that size.

### Next

It is clear that 2 x 2 x 3 is not the most symmetrical object ever, but that's a close to symmetry as it can be done with size 12.
For comparison, 8 blows up to a perfect n-cube - each dimension reading a value of 2.

So we can make a comparison between composite objects, based on the symmetry of their prime factorization n-cubes.

As a comparison tool, let's calculate and assign a value to that symmetry. The chosen methods is the following:

* calculate the prime factors of the number
* calculate their mean - this represents the dimensions of a perfectly symmetrical n-cube of that size, if non-integer magnitudes of the sides were allowed (for 12 that would be a cube with an edge length of appr. 2.2894)
* calculate the deviation of each side, compared to the mean factor
* get the mean of the deviations

If we use this method to compare two of the factorizations of 12 (with a prime factor mean of 2.33 (rec.)), we'll see that
2 x 6 has a mean deviation of 2, while

3 x 4 has a mean deviation of 1.66 (rec.)
2 x 2 x 3 has a mean deviation of 0.44 (rec.) - the most symmetrical n-cube 12 can do
(again, for comparison, 8 equals 2 x 2 x 2, which has a mean deviation of 0, because all of it's factors are equal, i.e. they equal the mean).

Now we can make a comparison between sets of composite numbers.

List the numbers, calculate the mean deviations and plot them.

---

## Notes on the data and the graph

**Graph**

The x-axis are the composite numbers (primes are excluded by default, but can be included by changing the value of include_primes in config.ini to true)

The y-axis are the calculated mean prime factor deviations.

**Antislope**
As an additional piece of data I added the slope for each data point. The main goal of the graph was so see how much a number deviates from its ideal 'blow-up'. However in the early iterations I mistakenly calculated that slope in reverse - run / rise. And it's good that I did, because the values of that antislope are easier to read than the real slope values (4.005 is better than 0.2496). That's why the graph reports the antislope (1/slope a.k.a. run/rise). As it will become apparent later, the antislopes (well, and the slopes, really) have a way of converging nicely to integer values, which can prove useful. I consider this error fortuitous, as I can not imagine I would have easily seen a pattern in the values of the slopes.

The lines that the points form on the graph are not real lines, but are very close.

It turns out that if you round the antislope of the points to their closest integer, all numbers fall into families.

The topmost line have slopes that round down to 4. Not only that, but the antislopes actually slowly converge to 4. The difference starts big (4.471 for 38), but that's to be expected, but at 166 the antislope is below 4.1 and at 1706 it drops below 4.01.

There are similar lines below the top one that converge on higher antislopes - the next one being 6, then 9, then 10 and so on.

It's easy to find (looking at the graph) which numbers converge to which integer antislope - another description of the same families of numbers is the product of all prime factors of the number except the largest one.

I.e. all numbers that produce 2 when divided by their largest prime factor will have antislope that is rounded down to 4. All numbers that produce 3 will have antislope rounded down to 6.

| Integer antislope | Prime factors (P = largest prime) | Number / P (P = largest prime) |
| ----------------- | --------------------------------- | ------------------------------ |
| 4                 | 2, P                              | 2                              |
| 6                 | 3, P                              | 3                              |
| 9                 | 2, 2, P                           | 4                              |
| 10                | 5, P                              | 5                              |
| 13                | 2, 3, P                           | 6                              |
| 14                | 7, P                              | 7                              |

And yes, it can be seen that consecutive families produce consecutive integers (starting at 2) when dividing the numbers in each family by the number's largest factor.

This, practically, means that each line is a modulo N family, where N is a positive integer. And those family lines fall below one another.

**TO BE EXPLORED**

- Why the integer antislope is 4, 6, 9...? It probably relates to the remainder when removing the largest prime factor, but I have yet to find how. (Just to be sure (and a bit lazy), I looked in OEIS for the first 10 integer antislopes - 4, 6, 9, 10, 13, 14, 20, 21, 22, 26 - and did not find a matching sequence)
- Rate of converges to those limits - why converge at all and why always from above?

**PROBLEM**

The 'integer antislope' concept hits a limit pretty soon, which means that the converging behaviour is questionable.

Example:

Look at **7183** and **7190**

7183 has factors 11, 653 and 7190 has 2, 5, 719
That puts 7183 in the family of numbers divisible by 11 and 7190 - divisible by 10.
But thus far it seemed that the higher this divisibility factor, the higher the integer antislope of the number.
The problem is that 7183 has an antislope of 22.377 and 7190 has an antislope 22.610, which puts the larger number on a lower integer antislope line. More importantly, it also means that both converge to 22.

---

# Notes on the code and the graph

**Beware**: this code has not been optimized; 1-10000 takes 7 seconds to run, and 1-100000 run takes more than 30 min. If at some point I feel the need to generate frequently larger datasets, I'll work on optimizing the code for speed.

**Colors**: The library I chose for visualization (bokeh) has a limit on the number of colors that can be used - 11.
I could not color each antislope line, so I did some bucketing, based on the antislope - if we have X antislope lines on the graph, the heavier half of them (the half with largest antislopes) are in one color bucket. Of the rest, the heavier half is another color bucket and so on.
As a result the first one or two lines are different colors, then you have 2 with the same color, 4 with another and so on.
Given that the colors are only for graph readability, I don't plan to optimize that further for now.

Additionally, if you run the script for a range that would require more than 11 color buckets, it will default to the monocolour version.
