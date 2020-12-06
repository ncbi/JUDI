This example shows how JUDI can be used to merge the results of biblical Tortoise VS Hare race.
With the difference that there were two races: in the second one Hare learnt from mistake.

We have four files to simulate:
`hare_1.csv` timing of hare in first race in the follwing form:
```
time,distance
0, 0
0.5, 0.4
1, 0.8
and so on
```

`tortoise_1.csv` timing of tortoise in first race in the follwing form:
```
time,distance
0, 0
0.5, 0.4
1, 0.8
and so on
```

`hare_2.csv`, `tortoise_2.csv` timings in second race

Then one task to merge results of each game in a single file.
So we will have two merged files:

`combined_1.csv` results from first race
```
racer,time,distance
hare,0, 0
hare,0.5, 0.4
hare,1, 0.8
tortoise,0,0
tortoise,0.5,0.5
tortoise,1,1
```
Similarly for `combined_2.csv`

How to do this in JUDI is shown in [dodo.py](dodo.py)

Tried to do the same in Snakemake unsuccessfully in [snakefile](snakefile)
