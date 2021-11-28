Constants computed via:

```bash
$ VERSION=0.7.8.9507
$ wget -O y-cruncher.tar.xz http://www.numberworld.org/y-cruncher/y-cruncher%20v$VERSION-static.tar.xz
$ tar -xf y-cruncher.tar.xz
$ mv "y-cruncher v$VERSION" y-cruncher_$VERSION
$ for c in apery catalan e pi; do
>   mkdir -p constants/$c
>   y-cruncher_$VERSION/y-cruncher custom $c -dec:1M -o constants/$c
>   mv constants/$c/*Dec*.txt constants/$c.dat
>   rm -r constants/$c
> done
```
