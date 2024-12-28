![pylint](https://img.shields.io/badge/pylint-9.09-green?logo=python&logoColor=white) 

# TlfUdp2WinTest

## Description

Convert [TLF](https://github.com/tlf/tlf) UDP QSO information to WinTest format.

The main use case is to connect TLF to QSO aggregators.

The default topology is

TLF --UDP 9873--> tlfudp2wintest --UDP 9871--> (aggregator)


## Usage

### TLF configuration

Assuming that both TLF and the converter run on the same host,
add an extra node to TLF

```
ADDNODE=127.0.0.1:9873
```

where 9873 is the default UDP listener port of tlfudp2wintest.

### Running the converter

```
python3 tlfudp2wintest.py
```

### Options

```
python3 tlfudp2wintest.py --help

  -h, --help       show this help message and exit
  -d, --debug      debug log level
  --tlf-host HOST  TLF node host/IP (default: 127.0.0.1)
  --tlf-port PORT  TLF node port (default: 9873)
  --wt-host HOST   WinTest destination host/IP (default: 127.0.0.1)
  --wt-port PORT   WinTest destination port (default: 9871)

```

## Credits

Code is based on protocol dumps by HA6OI (SK)
and [aiowintest](https://github.com/hin/aiowintest) by Hans SM0UTY.

