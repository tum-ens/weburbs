
# Configuration

Examples can be found in [backend/config](../backend/config).
Every file needs to have the following format.
Most fields correspond closely to the fields found in the forms.
However, you can find some more [special option](#special-options).

```json
{
  "commodity": {
    "name_of_com": {
      "type": "SupIm", // SupIm, Demand, Stock, Env, Buy, Sell
      "autoquery": "Solar", // Solar, Wind or empty
      "price": 0, // can be left out
      "max": -1, // can be left out
      "maxperhour": -1, // can be left out
      "unitR": "kW", // unit for the rate (should be unitC/h)
      "unitC": "kWh" // unit for the capacity of this commodity
    },
    ...
  },
  "process": {
    "Photovoltaics": {
      "description": "Generates electricity from sun",
      "instcap": 0,
      "caplo": 0,
      "capup": -1,
      "maxgrad": -1,
      "minfraction": 0,
      "invcost": 1000,
      "fixcost": 0,
      "varcost": 0,
      "wacc": 0.07,
      "depreciation": 25,
      "areapercap": 5,
      "commodities": {
        "Solar": {
          "direction": "In",
          "ratio": 1,
          "ratiomin": 1
        },
        "Elec": {
          "direction": "Out",
          "ratio": 1,
          "ratiomin": 1
        }
      },
      "autoadd": true
    },
    ...
  },
  "demand": {
    "Agricultural_Mill or Thresher or Grater": {
      "description": "Agricultural_Mill or Thresher or Grater",
      "steps": [ // exactly 8760 numbers
        0,
        1,
        1,
        ...
      ]
    },
    ...
  },
  "storage": {
    "Lead-Acid Battery": {
      "description": "Lead-Acid battery",
      "commodity": "Elec",
      "instcapc": 0,
      "caploc": 0,
      "capupc": -1,
      "instcapp": 0,
      "caplop": 0,
      "capupp": -1,

      "effin": 0.80,
      "effout": 0.80,

      "invcostc": 200,
      "fixcostc": 0,
      "varcostc": 0,
      "invcostp": 0,
      "fixcostp": 0,
      "varcostp": 0,

      "wacc": 0.007,
      "depreciation": 5,
      "init": 0.5,
      "discharge": 0.0000035
    },
    ...
  }
}
```

## Special options

|   Table   |    Key    |                                            Description                                            |           Values           |
|:---------:|:---------:|:-------------------------------------------------------------------------------------------------:|:--------------------------:|
| commodity |  autoadd  |                       This commodity will for every site when being created                       | True \| False \| undefined |
| commodity | autoquery |            The selected SupIm will be pulled automatically when adding this commodity             |       Solar \| Wind        |
|  process  |  autoadd  | This process will be added automatically when being created. Also adds all the needed commodities | True \| False \| undefined |
