## <a name="main_help"></a> python3 -m uncrustimpact --help
```
usage: __main__.py [-h] [-la] [--listtools] {genparamsspace,impact} ...

uncrustify-impact

optional arguments:
  -h, --help            show this help message and exit
  -la, --logall         Log all messages
  --listtools           List tools

subcommands:
  use one of tools

  {genparamsspace,impact}
                        one of tools
    genparamsspace      generate parameters space dict
    impact              calculate config impact
```



## <a name="genparamsspace_help"></a> python3 -m uncrustimpact genparamsspace --help
```
usage: __main__.py genparamsspace [-h]

generate parameters space dict

optional arguments:
  -h, --help  show this help message and exit
```



## <a name="impact_help"></a> python3 -m uncrustimpact impact --help
```
usage: __main__.py impact [-h] -f FILE -c CONFIG -od OUTPUTDIR
                          [-ip IGNOREPARAMS [IGNOREPARAMS ...]]
                          [-cp CONSIDERPARAMS [CONSIDERPARAMS ...]]

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
  -cp CONSIDERPARAMS [CONSIDERPARAMS ...], --considerparams CONSIDERPARAMS [CONSIDERPARAMS ...]
                        Parameters list to consider
```
