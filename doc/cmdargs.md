## <a name="main_help"></a> python3 -m uncrustimpact --help
```
usage: python3 -m uncrustimpact [-h] [-la] [--listtools]
                                {genparamsspace,impact} ...

display uncrustify configuration impact on given source files

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
usage: python3 -m uncrustimpact genparamsspace [-h]

generate parameters space dict

optional arguments:
  -h, --help  show this help message and exit
```



## <a name="impact_help"></a> python3 -m uncrustimpact impact --help
```
usage: python3 -m uncrustimpact impact [-h] -f FILE -c CONFIG -od OUTPUTDIR
                                       [-ps PARAMSSPACE] [-odps]
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
  -ps PARAMSSPACE, --paramsspace PARAMSSPACE
                        Path to params space config JSON
  -odps, --overridedefparamsspace
                        Override default params space with given one
  -ip IGNOREPARAMS [IGNOREPARAMS ...], --ignoreparams IGNOREPARAMS [IGNOREPARAMS ...]
                        Parameters list to ignore
  -cp CONSIDERPARAMS [CONSIDERPARAMS ...], --considerparams CONSIDERPARAMS [CONSIDERPARAMS ...]
                        Parameters list to consider
```
