## <a name="main_help"></a> python3 -m uncrustimpact --help
```
usage: __main__.py [-h] [-la] [--listtools] {genparamsdict,impact} ...

uncrustify-impact

optional arguments:
  -h, --help            show this help message and exit
  -la, --logall         Log all messages
  --listtools           List tools

subcommands:
  use one of tools

  {genparamsdict,impact}
                        one of tools
    genparamsdict       generate parameters space dict
    impact              calculate config impact
```



## <a name="genparamsdict_help"></a> python3 -m uncrustimpact genparamsdict --help
```
usage: __main__.py genparamsdict [-h]

generate parameters space dict

optional arguments:
  -h, --help  show this help message and exit
```



## <a name="impact_help"></a> python3 -m uncrustimpact impact --help
```
usage: __main__.py impact [-h] -f FILE -c CONFIG -od OUTPUTDIR
                          [-ip IGNOREPARAMS [IGNOREPARAMS ...]]
                          [--randomseed RANDOMSEED]

calculate config impact

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  File to analyze
  -c CONFIG, --config CONFIG
                        Base uncrustify config
  -od OUTPUTDIR, --outputdir OUTPUTDIR
                        Output directory
  -ip IGNOREPARAMS [IGNOREPARAMS ...], --ignoreparams IGNOREPARAMS [IGNOREPARAMS ...]
                        Parameters list to ignore
  --randomseed RANDOMSEED
                        Seed for random number generator
```
