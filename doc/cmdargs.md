## <a name="main_help"></a> python3 -m uncrustimpact --help
```
usage: python3 -m uncrustimpact [-h] [-la] [--listtools]
                                {genparamsspace,impact,diff,fit} ...

display uncrustify configuration impact on given source files

optional arguments:
  -h, --help            show this help message and exit
  -la, --logall         Log all messages (default: False)
  --listtools           List tools (default: False)

subcommands:
  use one of tools

  {genparamsspace,impact,diff,fit}
                        one of tools
    genparamsspace      generate parameters space dict
    impact              calculate config impact
    diff                show changes made by given config
    fit                 find config to make smallest impact on files
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
usage: python3 -m uncrustimpact impact [-h] [-f FILES [FILES ...]] [-d DIR]
                                       [--extlist EXTLIST [EXTLIST ...]] -c
                                       CONFIG -od OUTPUTDIR [-ps PARAMSSPACE]
                                       [-odps]
                                       [-ip IGNOREPARAMS [IGNOREPARAMS ...]]
                                       [-cp CONSIDERPARAMS [CONSIDERPARAMS ...]]

calculate config impact

optional arguments:
  -h, --help            show this help message and exit
  -f FILES [FILES ...], --files FILES [FILES ...]
                        Files to analyze (default: [])
  -d DIR, --dir DIR     Path to directory to search for files (default: None)
  --extlist EXTLIST [EXTLIST ...]
                        List of extensions to look for (in case of --dir)
                        (default: ['.h', '.hpp', '.c', 'cpp'])
  -c CONFIG, --config CONFIG
                        Base uncrustify config (default: None)
  -od OUTPUTDIR, --outputdir OUTPUTDIR
                        Output directory (default: None)
  -ps PARAMSSPACE, --paramsspace PARAMSSPACE
                        Path to params space config JSON (default: None)
  -odps, --overridedefparamsspace
                        Override default params space with given one (default:
                        False)
  -ip IGNOREPARAMS [IGNOREPARAMS ...], --ignoreparams IGNOREPARAMS [IGNOREPARAMS ...]
                        Parameters list to ignore (default: [])
  -cp CONSIDERPARAMS [CONSIDERPARAMS ...], --considerparams CONSIDERPARAMS [CONSIDERPARAMS ...]
                        Parameters list to consider (default: [])
```



## <a name="diff_help"></a> python3 -m uncrustimpact diff --help
```
usage: python3 -m uncrustimpact diff [-h] [-f FILES [FILES ...]] [-d DIR]
                                     [--extlist EXTLIST [EXTLIST ...]] -c
                                     CONFIG -od OUTPUTDIR

show changes made by given config

optional arguments:
  -h, --help            show this help message and exit
  -f FILES [FILES ...], --files FILES [FILES ...]
                        Files to analyze (default: [])
  -d DIR, --dir DIR     Path to directory to search for files (default: None)
  --extlist EXTLIST [EXTLIST ...]
                        List of extensions to look for (in case of --dir)
                        (default: ['.h', '.hpp', '.c', 'cpp'])
  -c CONFIG, --config CONFIG
                        Base uncrustify config (default: None)
  -od OUTPUTDIR, --outputdir OUTPUTDIR
                        Output directory (default: None)
```



## <a name="fit_help"></a> python3 -m uncrustimpact fit --help
```
usage: python3 -m uncrustimpact fit [-h] [-f FILES [FILES ...]] [-d DIR]
                                    [--extlist EXTLIST [EXTLIST ...]] -c
                                    CONFIG -od OUTPUTDIR [-ps PARAMSSPACE]
                                    [-odps]
                                    [-ip IGNOREPARAMS [IGNOREPARAMS ...]]
                                    [-cp CONSIDERPARAMS [CONSIDERPARAMS ...]]

find config to make smallest impact on files

optional arguments:
  -h, --help            show this help message and exit
  -f FILES [FILES ...], --files FILES [FILES ...]
                        Files to analyze (default: [])
  -d DIR, --dir DIR     Path to directory to search for files (default: None)
  --extlist EXTLIST [EXTLIST ...]
                        List of extensions to look for (in case of --dir)
                        (default: ['.h', '.hpp', '.c', 'cpp'])
  -c CONFIG, --config CONFIG
                        Base uncrustify config (default: None)
  -od OUTPUTDIR, --outputdir OUTPUTDIR
                        Output directory (default: None)
  -ps PARAMSSPACE, --paramsspace PARAMSSPACE
                        Path to params space config JSON (default: None)
  -odps, --overridedefparamsspace
                        Override default params space with given one (default:
                        False)
  -ip IGNOREPARAMS [IGNOREPARAMS ...], --ignoreparams IGNOREPARAMS [IGNOREPARAMS ...]
                        Parameters list to ignore (default: [])
  -cp CONSIDERPARAMS [CONSIDERPARAMS ...], --considerparams CONSIDERPARAMS [CONSIDERPARAMS ...]
                        Parameters list to consider (default: [])
```
