# Colourful constants

## _π_

One afternoon to lose? Let's visualize [_π_](https://en.wikipedia.org/wiki/Pi) using
your favourite language. (_The idea is
[not mine](https://www.visualcinnamon.com/portfolio/the-art-in-pi/); if you like the
idea -and π- please check her posters available
[there](https://shop.visualcinnamon.com/collections/the-art-in-pi)._)

For each digit, choose a direction and a colour, and plot it as a vector. Here are some
download [links](https://www.angio.net/pi/digits.html) for up to four billions
pre-computed digits of _π_. Best and/or smoothest and/or funkiest and/or most
psychedelic visualization wins!

And if you decide to _compute_ the digits yourself, below an implementation of the
[Spigot algorithm](https://en.wikipedia.org/wiki/Spigot_algorithm):

```python
def pi_digits(n):
    """Generate n digits of π via the Spigot algorithm by A. Sale et al."""
    k, a, b, a1, b1 = 2, 4, 1, 12, 4
    while n > 0:
        p, q, k = k * k, 2 * k + 1, k + 1
        a, b, a1, b1 = a1, b1, p * a + q * a1, p * b + q * b1
        d, d1 = a / b, a1 / b1
        while d == d1 and n > 0:
            yield int(d)
            n -= 1
            a, a1 = 10 * (a % b), 10 * (a1 % b1)
            d, d1 = a / b, a1 / b1
```

Feel free to re-implement in your own chosen language and fulfill your darkest
mathematical fantasies. But we want visualizations. Below the random walk corresponding
to the first 1,000 decimals of π:

![First 1,000 decimals of π](outputs/pi-1k.svg)

## _e_, Apery, Catalan, ...

[Let's get even nerdier!](http://www.numberworld.org/y-cruncher/internals/formulas.html)
Check [this one](http://www.numberworld.org/y-cruncher/#Download) out and compute a
couple digits of some random irrational numbers. Then apply the same idea as above. I
need colourful posters for my bathroom.

Quick run after downloading `y-cruncher` (v0.7.8.9507, static):

```bash
$ ./y-cruncher custom catalan -dec:100
$ cat "Catalan - Dec - Pilehrood (short).txt"
0.9159655941772190150546035149323841107741493742816721342664981196217630197762547694793565129261151062
```

| Apery | Catalan | _e_ |
| :-: | :-: | :-: |
| ![](outputs/apery-1k.svg) | ![](outputs/catalan-1k.svg) | ![](outputs/e-1k.svg) |
