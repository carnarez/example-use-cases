# Colourful constants

## Pi

One afternoon to lose? Let's visualize [Pi](https://en.wikipedia.org/wiki/Pi) using your
favourite language. (The idea is
[not mine](https://www.visualcinnamon.com/portfolio/the-art-in-pi/).)

For each digit, choose a direction and a colour, and plot it as a vector. Here are some
download [links](https://www.angio.net/pi/digits.html) for up to four billions
pre-computed digits of pi. Best and/or smoothest and/or funkiest and/or most psychedelic
visualization wins!

And if you decide to _compute_ the digits yourself, below an implementation of the
[Spigot algorithm](https://en.wikipedia.org/wiki/Spigot_algorithm):

```python
def pi_digits(n):
    """Generate n digits of Pi via the Spigot algorithm by A. Sale et al."""
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
mathematical fantasies. But we want visualizations.

## e, Apery, Catalan, ...

[Let's get even nerdier!](http://www.numberworld.org/y-cruncher/internals/formulas.html)
Check [this one](http://www.numberworld.org/y-cruncher/#Download) out and compute a
couple digits of some random irrational numbers.

Apply the same idea as above. I need colourful posters for my bathroom.
