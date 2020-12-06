This example shows how JUDI can be used to merge the results of biblical Tortoise VS Hare race.
With the difference that there were two races: in the second one Hare learnt from mistake.

We have four files to simulate:
1. timing of hare in first race as in [hare_1](hare_1)
2. timing of tortoise in first race in [tortoise_1](tortoise_1)
3. and 4. similarly

Then one task to merge results of each game in a single file.

So we will have two merged files:

`combined_1.csv` results from first race
```
racer,time,distance
tortoise,0.0,0.0
tortoise,0.25,0.25
tortoise,0.5,0.5
tortoise,0.75,0.75
tortoise,1.0,1.0
hare,0.0,0.0
hare,0.25,0.4
hare,0.5,0.4
hare,0.75,0.4
hare,1.0,0.8
```
Similarly for `combined_2.csv`

How to do this in JUDI is shown in [dodo.py](dodo.py)

Tried to do the same in Snakemake unsuccessfully in [snakefile](snakefile).

The best I could do without using `Paramspace` as in [snakefile.simple](snakefile.simple). However, in that case, what happens if there are more than one parameter (in this case racer) to collate on? How to ensure partly expanded form in the input declaration? How to ensure the order of the parameters?
