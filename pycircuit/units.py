import re
import numpy as np


class Value(object):
    E3  =       [1.0, 2.2, 4.7]
    E6  = E3  + [1.5, 3.3, 6.8]
    E12 = E6  + [1.2, 1.8, 2.7, 3.9, 5.6, 8.2]
    E24 = E12 + [1.1, 1.3, 1.6, 2.0, 2.4, 3.0, 3.6, 4.3, 5.1, 6.2, 7.5, 9.1]

    default_series_by_unit = {'H': E6, 'F': E12, '': E24}

    def __init__(self, value, unit='', series=None):
        # Original value
        self.value = value
        # Unit information
        self.unit = unit
        # Series of selectable values
        if series is None:
            series = Value.default_series_by_unit[unit]
        self.series = series

        self.numeric_value = None
        self.pprint_value = None

    def value_from_series(self):
        # Exponent
        exp = int(np.floor(np.log10(self.value)))
        # Exponent to scale selected value
        sexp = exp % 3
        # Exponent for engineering units
        eexp = exp - sexp

        # Normalized value for selection
        normalized = self.value / 10 ** exp

        # Find nearest value in series
        delta, selected_value = 10, 1.0
        for val in self.series:
            ndelta = abs(val - normalized)
            if ndelta < delta - 0.01:
                selected_value = val
                delta = ndelta
        selected_value = selected_value
        # Numeric value from series
        numeric_value = selected_value * 10 ** exp

        # Pretty print value
        tbl = {
            'e-3': 'm', 'e-6': 'u', 'e-9': 'n', 'e-12': 'p', 'e-15': 'f',
            'e0': '',
            'e3':  'K', 'e6':  'M', 'e9':  'G', 'e12':  'G', 'e15':  'P'
        }
        pretty_value = selected_value * 10 ** sexp
        if np.floor(pretty_value) == pretty_value:
            pretty_value = int(pretty_value)
        pprint_value = str(pretty_value) + tbl['e' + str(eexp)] + self.unit

        self.numeric_value = numeric_value
        self.pprint_value = pprint_value
        return self.numeric_value

    def __repr__(self):
        return str(self.value) + self.unit

    def __str__(self):
        if self.pprint_value is None:
            self.value_from_series()
        return self.pprint_value

    def __float__(self):
        if self.numeric_value is None:
            self.value_from_series()
        return self.numeric_value


    @classmethod
    def from_string(cls, text):
        regex = re.compile('^([0-9]*)(\.([0-9]*))?([munpfKMGTP])?([HF])?$')
        tbl = {
            'm': 'e-3', 'u': 'e-6', 'n': 'e-9', 'p': 'e-12', 'f': 'e-15',
            'K': 'e3',  'M': 'e6',  'G': 'e9',  'T': 'e12',  'P': 'e15'
        }

        res = regex.match(text)

        if res is None:
            return res

        absv, frac, exp, unit = res.group(1), res.group(3), \
                                res.group(4), res.group(5)

        absv = '0' if absv is None else absv
        frac = '0' if frac is None else frac
        exp = 'e0' if exp is None else tbl[exp]
        unit = '' if unit is None else unit

        return cls(float(absv + '.' + frac + exp), unit)
