"""Test NNDC data queries."""

from __future__ import print_function
import numpy as np
import pandas as pd
from becquerel.tools import nndc
import pytest

# pylint: disable=protected-access,no-self-use,too-many-public-methods
# pylint: disable=attribute-defined-outside-init,missing-docstring


def is_close(f1, f2, ppm=1.):
    """True if f1 and f2 are within the given parts per million."""
    return abs((f1 - f2) / f2) < ppm / 1.e6


class TestParseFloatUncertainty(object):
    """Test _parse_float_uncertainty()."""

    def test_01(self):
        """Test _parse_float_uncertainty('257.123', '0.005')..............."""
        answer = nndc._parse_float_uncertainty('257.123', '0.005')
        assert is_close(answer.nominal_value, 257.123)
        assert is_close(answer.std_dev, 0.005)

    def test_02(self):
        """Test _parse_float_uncertainty('257.123', '0.015')..............."""
        answer = nndc._parse_float_uncertainty('257.123', '0.015')
        assert is_close(answer.nominal_value, 257.123)
        assert is_close(answer.std_dev, 0.015)

    def test_03(self):
        """Test _parse_float_uncertainty('257.123E0', '0.005')............."""
        answer = nndc._parse_float_uncertainty('257.123E0', '0.005')
        assert is_close(answer.nominal_value, 257.123)
        assert is_close(answer.std_dev, 0.005)

    def test_04(self):
        """Test _parse_float_uncertainty('257.123E+0', '0.005')............"""
        answer = nndc._parse_float_uncertainty('257.123E+0', '0.005')
        assert is_close(answer.nominal_value, 257.123)
        assert is_close(answer.std_dev, 0.005)

    def test_05(self):
        """Test _parse_float_uncertainty('257.123E4', '5E3')..............."""
        answer = nndc._parse_float_uncertainty('257.123E4', '5E3')
        assert is_close(answer.nominal_value, 2571230.)
        assert is_close(answer.std_dev, 5000.)

    def test_06(self):
        """Test _parse_float_uncertainty('257.123E+4', '5E-3')............."""
        answer = nndc._parse_float_uncertainty('257.123E+4', '5E-3')
        assert is_close(answer.nominal_value, 2571230.)
        assert is_close(answer.std_dev, 0.005)

    def test_07(self):
        """Test _parse_float_uncertainty('257.123E+4', '5E-1E-2').........."""
        answer = nndc._parse_float_uncertainty('257.123E+4', '5E-1E-2')
        assert is_close(answer.nominal_value, 2571230.)
        assert is_close(answer.std_dev, 0.005)

    def test_08(self):
        """Test _parse_float_uncertainty('257.123', '')...................."""
        answer = nndc._parse_float_uncertainty('257.123', '')
        assert isinstance(answer, float)
        assert is_close(answer, 257.123)

    def test_09(self):
        """Test _parse_float_uncertainty('8', '2')........................."""
        answer = nndc._parse_float_uncertainty('8', '2')
        assert is_close(answer.nominal_value, 8.)
        assert is_close(answer.std_dev, 2.)

    def test_10(self):
        """Test _parse_float_uncertainty('8', '').........................."""
        answer = nndc._parse_float_uncertainty('8', '')
        assert isinstance(answer, float)
        assert is_close(answer, 8.)

    def test_11(self):
        """Test _parse_float_uncertainty('100.0%', '')....................."""
        answer = nndc._parse_float_uncertainty('100.0%', '')
        assert is_close(answer, 100.)

    def test_12(self):
        """Test _parse_float_uncertainty('73.92+X', '')...................."""
        answer = nndc._parse_float_uncertainty('73.92+X', '')
        assert is_close(answer, 73.92)

    def test_13(self):
        """Test _parse_float_uncertainty('Y', '').........................."""
        answer = nndc._parse_float_uncertainty('Y', '')
        assert answer == 0.

    def test_14(self):
        """Test _parse_float_uncertainty('', '')..........................."""
        answer = nndc._parse_float_uncertainty('', '')
        assert answer is None

    def test_15(self):
        """Test _parse_float_uncertainty('****', '')......................."""
        answer = nndc._parse_float_uncertainty('****', '')
        assert answer is None

    def test_16(self):
        """Test _parse_float_uncertainty('~7', '1')........................"""
        answer = nndc._parse_float_uncertainty('~7', '1')
        assert answer is None

    def test_17(self):
        """Test _parse_float_uncertainty('1', '****')......................"""
        answer = nndc._parse_float_uncertainty('1', '****')
        assert answer is None

    def test_18(self):
        """Test _parse_float_uncertainty('73.92', 'AP')...................."""
        answer = nndc._parse_float_uncertainty('73.92', 'AP')
        assert answer is None

    def test_19(self):
        """Test _parse_float_uncertainty('73.92', 'CA')...................."""
        answer = nndc._parse_float_uncertainty('73.92', 'CA')
        assert answer is None

    def test_20(self):
        """Test _parse_float_uncertainty('@', '7') raises NNDCRequestError."""
        with pytest.raises(nndc.NNDCRequestError):
            nndc._parse_float_uncertainty('@', '7')

    def test_21(self):
        """Test _parse_float_uncertainty('7', '@') raises NNDCRequestError."""
        with pytest.raises(nndc.NNDCRequestError):
            nndc._parse_float_uncertainty('7', '@')


class NNDCQueryTests(object):
    """Tests common to NNDCQuery-derived classes."""

    def setup_method(self):
        self.cls = nndc._NNDCQuery

        def fetch_dummy(**kwargs):  # pylint: disable=unused-argument
            """Dummy fetch_ function for self.fetch."""
            return pd.DataFrame()

        self.fetch = fetch_dummy

    def stable_isotope_condition(self, df):
        """What should be true about the dataframe if the isotope is stable."""
        return len(df) > 0

    def test_query_nuc_Co60(self):
        """Test NNDCQuery: nuc='Co-60'....................................."""
        d = self.fetch(nuc='Co-60')
        assert len(d) > 0

    def test_query_nuc_He4(self):
        """Test NNDCQuery: nuc='He-4'......................................"""
        d = self.fetch(nuc='He-4')
        assert self.stable_isotope_condition(d)

    def test_query_nuc_V50(self):
        """Test NNDCQuery: nuc='V-50'......................................"""
        d = self.fetch(nuc='V-50')
        assert len(d) > 0

    def test_query_nuc_Ge70(self):
        """Test NNDCQuery: nuc='Ge-70'....................................."""
        d = self.fetch(nuc='Ge-70')
        assert self.stable_isotope_condition(d)

    def test_query_nuc_U238(self):
        """Test NNDCQuery: nuc='U-238'....................................."""
        d = self.fetch(nuc='U-238')
        assert len(d) > 0

    def test_query_nuc_Pa234m(self):
        """Test NNDCQuery: nuc='Pa-234m' raises exception.................."""
        with pytest.raises(nndc.NNDCRequestError):
            self.fetch(nuc='Pa-234m')

    def test_query_nuc_Pa234(self):
        """Test NNDCQuery: nuc='Pa-234'...................................."""
        d = self.fetch(nuc='Pa-234')
        assert len(d) > 0

    def test_query_z_6(self):
        """Test NNDCQuery: z=6............................................."""
        d = self.fetch(z=6)
        assert len(d) > 0

    def test_query_a_12(self):
        """Test NNDCQuery: a=12............................................"""
        d = self.fetch(a=12)
        assert len(d) > 0

    def test_query_n_6(self):
        """Test NNDCQuery: n=6............................................."""
        d = self.fetch(n=6)
        assert len(d) > 0

    def test_query_z_6_a_12(self):
        """Test NNDCQuery: z=6, a=12......................................."""
        d = self.fetch(z=6, a=12)
        assert self.stable_isotope_condition(d)

    def test_query_n_6_a_12(self):
        """Test NNDCQuery: n=6, a=12......................................."""
        d = self.fetch(n=6, a=12)
        assert self.stable_isotope_condition(d)

    def test_query_z_6_a_12_n_6(self):
        """Test NNDCQuery: z=6, a=12, n=6.................................."""
        d = self.fetch(z=6, a=12, n=6)
        assert self.stable_isotope_condition(d)

    def test_query_zrange_1_20(self):
        """Test NNDCQuery: z_range=(1, 20)................................."""
        d = self.fetch(z_range=(1, 20))
        assert len(d) > 0

    def test_query_zrange_None_20(self):
        """Test NNDCQuery: z_range=(None, 20).............................."""
        d = self.fetch(z_range=(None, 20))
        assert len(d) > 0

    def test_query_zrange_100_None(self):
        """Test NNDCQuery: z_range=(100, None)............................."""
        d = self.fetch(z_range=(100, None))
        assert len(d) > 0

    def test_query_zrange_1_20_z_any(self):
        """Test NNDCQuery: z_range=(1, 20), z_any=True....................."""
        d = self.fetch(z_range=(1, 20), z_any=True)
        assert len(d) > 0

    def test_query_zrange_1_20_z_even(self):
        """Test NNDCQuery: z_range=(1, 20), z_even=True...................."""
        d = self.fetch(z_range=(1, 20), z_even=True)
        assert len(d) > 0

    def test_query_zrange_1_20_z_odd(self):
        """Test NNDCQuery: z_range=(1, 20), z_odd=True....................."""
        d = self.fetch(z_range=(1, 20), z_odd=True)
        assert len(d) > 0

    def test_query_zrange_30_50(self):
        """Test NNDCQuery: z_range=(30, 50)................................"""
        d = self.fetch(z_range=(30, 50))
        assert len(d) > 0

    def test_query_zrange_100_118(self):
        """Test NNDCQuery: z_range=(100, 118).............................."""
        d = self.fetch(z_range=(100, 118))
        assert len(d) > 0

    def test_query_zrange_230_250(self):
        """Test NNDCQuery: z_range=(230, 250) returns empty dataframe......"""
        d = self.fetch(z_range=(230, 250))
        assert len(d) == 0

    def test_query_arange_1_20(self):
        """Test NNDCQuery: a_range=(1, 20)................................."""
        d = self.fetch(a_range=(1, 20))
        assert len(d) > 0

    def test_query_arange_1_20_a_any(self):
        """Test NNDCQuery: a_range=(1, 20), a_any=True....................."""
        d = self.fetch(a_range=(1, 20), a_any=True)
        assert len(d) > 0

    def test_query_arange_1_20_a_even(self):
        """Test NNDCQuery: a_range=(1, 20), a_even=True...................."""
        d = self.fetch(a_range=(1, 20), a_even=True)
        assert len(d) > 0

    def test_query_arange_1_20_a_odd(self):
        """Test NNDCQuery: a_range=(1, 20), a_odd=True....................."""
        d = self.fetch(a_range=(1, 20), a_odd=True)
        assert len(d) > 0

    def test_query_nrange_1_20(self):
        """Test NNDCQuery: n_range=(1, 20)................................."""
        d = self.fetch(n_range=(1, 20))
        assert len(d) > 0

    def test_query_nrange_1_20_n_any(self):
        """Test NNDCQuery: n_range=(1, 20), n_any=True....................."""
        d = self.fetch(n_range=(1, 20), n_any=True)
        assert len(d) > 0

    def test_query_nrange_1_20_n_even(self):
        """Test NNDCQuery: n_range=(1, 20), n_even=True...................."""
        d = self.fetch(n_range=(1, 20), n_even=True)
        assert len(d) > 0

    def test_query_nrange_1_20_n_odd(self):
        """Test NNDCQuery: n_range=(1, 20), n_odd=True....................."""
        d = self.fetch(n_range=(1, 20), n_odd=True)
        assert len(d) > 0

    def test_query_nrange_1_20_z_even_a_even_n_any(self):
        """Test NNDCQuery: z_range=(1, 20), z_even, a_even, n_any.........."""
        d = self.fetch(
            z_range=(1, 20), z_even=True, a_even=True, n_any=True)
        assert len(d) > 0

    def test_query_exception_not_found(self):
        """Test NNDCQuery exception if website not found..................."""
        _URL_ORIG = self.cls._URL
        self.cls._URL = 'http://httpbin.org/status/404'
        with pytest.raises(nndc.NNDCRequestError):
            self.fetch(nuc='Co-60')
        self.cls._URL = _URL_ORIG

    def test_query_exception_empty(self):
        """Test NNDCQuery exception if website is empty...................."""
        _URL_ORIG = self.cls._URL
        self.cls._URL = 'http://httpbin.org/post'
        with pytest.raises(nndc.NNDCRequestError):
            self.fetch(nuc='Co-60')
        self.cls._URL = _URL_ORIG

    def test_query_exception_range_None(self):
        """Test NNDCQuery exception if a range kwarg is not iterable......."""
        with pytest.raises(nndc.NNDCInputError):
            self.fetch(n_range=None)

    def test_query_exception_range_empty(self):
        """Test NNDCQuery exception if a range kwarg is empty.............."""
        with pytest.raises(nndc.NNDCInputError):
            self.fetch(n_range=())

    def test_query_exception_range_len_1(self):
        """Test NNDCQuery exception if a range kwarg has length 1.........."""
        with pytest.raises(nndc.NNDCInputError):
            self.fetch(n_range=(0, ))

    def test_query_exception_range_len_3(self):
        """Test NNDCQuery exception if a range kwarg has length 3.........."""
        with pytest.raises(nndc.NNDCInputError):
            self.fetch(n_range=(0, 10, 100))

    def test_query_exception_unknown_kwarg(self):
        """Test NNDCQuery exception if an invalid kwarg is given..........."""
        with pytest.raises(nndc.NNDCInputError):
            self.fetch(bad_kwarg=None)

    def test_query_trange_1Em6_1Em5(self):
        """Test NNDCQuery: t_range=(1e-6, 1e-5)............................"""
        d = self.fetch(t_range=(1e-6, 1e-5))
        assert len(d) > 0

    def test_query_zrange_1_20_trange_None_1E4(self):
        """Test NNDCQuery: z_range=(1, 20), t_range=(None, 1e4)............"""
        d = self.fetch(z_range=(1, 20), t_range=(None, 1e4))
        assert len(d) > 0

    def test_query_zrange_1_20_trange_0_1E4(self):
        """Test NNDCQuery: z_range=(1, 20), t_range=(0, 1e4)..............."""
        d = self.fetch(z_range=(1, 20), t_range=(0, 1e4))
        assert len(d) > 0

    def test_query_zrange_1_20_trange_1E4_1E9(self):
        """Test NNDCQuery: z_range=(1, 20), t_range=(1e4, 1e9)............."""
        d = self.fetch(z_range=(1, 20), t_range=(1e4, 1e9))
        assert len(d) > 0

    def test_query_zrange_1_20_trange_1E9_None(self):
        """Test NNDCQuery: z_range=(1, 20), t_range=(1e9, None)............"""
        d = self.fetch(z_range=(1, 20), t_range=(1e9, None))
        assert len(d) > 0

    def test_query_zrange_1_20_trange_1E9_inf(self):
        """Test NNDCQuery: z_range=(1, 20), t_range=(1e9, np.inf).........."""
        d = self.fetch(z_range=(1, 20), t_range=(1e9, np.inf))
        assert len(d) > 0

    def test_query_zrange_1_20_elevelrange_0_01(self):
        """Test NNDCQuery: z_range=(1, 20), elevel_range=(0, 0.1).........."""
        d = self.fetch(z_range=(1, 20), elevel_range=(0, 0.1))
        assert len(d) > 0

    def test_query_zrange_1_20_elevelrange_01_10(self):
        """Test NNDCQuery: z_range=(1, 20), elevel_range=(0.1, 10)........."""
        d = self.fetch(z_range=(1, 20), elevel_range=(0.1, 10))
        assert len(d) > 0

    def test_query_nuc_Pu239_decay_A(self):
        """Test NNDCQuery: nuc='Pu-239', decay='Alpha'....................."""
        d = self.fetch(nuc='Pu-239', decay='Alpha')
        assert len(d) > 0

    def test_query_nuc_Co60_decay_BM(self):
        """Test NNDCQuery: nuc='Co-60', decay='B-'........................."""
        d = self.fetch(nuc='Co-60', decay='B-')
        assert len(d) > 0

    def test_query_nuc_Na22_decay_ECBP(self):
        """Test NNDCQuery: nuc='Na-22', decay='EC+B+'......................"""
        d = self.fetch(nuc='Na-22', decay='EC+B+')
        assert len(d) > 0

    def test_query_exception_bad_decay(self):
        """Test NNDCQuery raises exception for an invalid decay mode......."""
        with pytest.raises(nndc.NNDCInputError):
            self.fetch(nuc='Pu-239', decay='InvalidMode')


@pytest.mark.webtest
class TestNuclearWalletCard(NNDCQueryTests):
    """Test NNDC nuclear_wallet_card query."""

    def setup_method(self):
        self.cls = nndc._NuclearWalletCardQuery
        self.fetch = nndc.fetch_wallet_card

    def test_wallet_zrange_1_20_j_0(self):
        """Test fetch_wallet_card: z_range=(1, 20), j='0'.................."""
        with pytest.raises(nndc.NNDCRequestError):
            d = self.fetch(z_range=(1, 20), j='0')
            assert len(d) > 0

    def test_wallet_zrange_1_20_j_3_2(self):
        """Test fetch_wallet_card: z_range=(1, 20), j='3/2'................"""
        with pytest.raises(nndc.NNDCRequestError):
            d = self.fetch(z_range=(1, 20), j='3/2')
            assert len(d) > 0

    def test_wallet_zrange_1_20_parity_any(self):
        """Test fetch_wallet_card: z_range=(1, 20), parity='ANY'..........."""
        d = self.fetch(z_range=(1, 20), parity='ANY')
        assert len(d) > 0

    def test_wallet_zrange_1_20_parity_p(self):
        """Test fetch_wallet_card: z_range=(1, 20), parity='+'............."""
        with pytest.raises(nndc.NNDCRequestError):
            d = self.fetch(z_range=(1, 20), parity='+')
            assert len(d) > 0

    def test_wallet_zrange_1_20_parity_m(self):
        """Test fetch_wallet_card: z_range=(1, 20), parity='-'............."""
        with pytest.raises(nndc.NNDCRequestError):
            d = self.fetch(z_range=(1, 20), parity='-')
            assert len(d) > 0

    def test_wallet_zrange_1_20_parity_bad(self):
        """Test fetch_wallet_card raises except. for invalid parity........"""
        with pytest.raises(nndc.NNDCInputError):
            self.fetch(z_range=(1, 20), parity='InvalidParity')

    def test_wallet_zrange_1_20_j_2_parity_p(self):
        """Test fetch_wallet_card: z_range=(1, 20), j='2', parity='+'......"""
        with pytest.raises(nndc.NNDCRequestError):
            d = self.fetch(z_range=(1, 20), j='2', parity='+')
            assert len(d) > 0

    def test_wallet_j_10(self):
        """Test fetch_wallet_card: j='10'.................................."""
        with pytest.raises(nndc.NNDCRequestError):
            d = self.fetch(j='10')
            assert len(d) > 0

    def test_wallet_decay_cluster(self):
        """Test fetch_wallet_card: decay='Cluster'........................."""
        d = self.fetch(decay='Cluster')
        assert len(d) > 0


@pytest.mark.webtest
class TestDecayRadiationQuery(NNDCQueryTests):
    """Test NNDC decay_radiation."""

    def setup_method(self):
        self.cls = nndc._DecayRadiationQuery
        self.fetch = nndc.fetch_decay_radiation

    def stable_isotope_condition(self, df):
        """What should be true about the dataframe if the isotope is stable."""
        return len(df) == 0

    def test_decay_nuc_Pu239_type_G(self):
        """Test fetch_decay_radiation: nuc='Pu-239', type='Gamma'.........."""
        d = self.fetch(nuc='Pu-239', type='Gamma')
        assert len(d) > 0

    def test_decay_exception_bad_type(self):
        """Test fetch_decay_radiation raises except. for invalid rad type.."""
        with pytest.raises(nndc.NNDCInputError):
            self.fetch(nuc='Pu-239', type='InvalidType')

    def test_decay_zrange_100_120_type_ANY(self):
        """Test fetch_decay_radiation: z_range=(100, 120), type='ANY'......"""
        d = self.fetch(z_range=(100, 120), type='ANY')
        assert len(d) > 0

    def test_decay_zrange_100_120_type_G(self):
        """Test fetch_decay_radiation: z_range=(100, 120), type='Gamma'...."""
        d = self.fetch(z_range=(100, 120), type='Gamma')
        assert len(d) > 0

    def test_decay_nuc_Ba133_erange_300_400(self):
        """Test fetch_decay_radiation: nuc='Ba-133', e_range=(300, 400)...."""
        d = self.fetch(nuc='Ba-133', e_range=(300, 400))
        assert len(d) > 0

    def test_decay_nuc_Ba133_erange_300_None(self):
        """Test fetch_decay_radiation: nuc='Ba-133', e_range=(300, None)..."""
        d = self.fetch(nuc='Ba-133', e_range=(300, None))
        assert len(d) > 0

    def test_decay_nuc_Ba133_erange_None_400(self):
        """Test fetch_decay_radiation: nuc='Ba-133', e_range=(None, 400)..."""
        d = self.fetch(nuc='Ba-133', e_range=(None, 400))
        assert len(d) > 0

    def test_decay_nuc_Ba133_irange_10_100(self):
        """Test fetch_decay_radiation: nuc='Ba-133', i_range=(10, 100)....."""
        d = self.fetch(nuc='Ba-133', i_range=(10, 100))
        assert len(d) > 0

    def test_decay_nuc_Ba133_irange_40_None(self):
        """Test fetch_decay_radiation: nuc='Ba-133', i_range=(40, None)...."""
        d = self.fetch(nuc='Ba-133', i_range=(40, None))
        assert len(d) > 0

    def test_decay_nuc_Ba133_irange_None_40(self):
        """Test fetch_decay_radiation: nuc='Ba-133', i_range=(None, 40)...."""
        d = self.fetch(nuc='Ba-133', i_range=(None, 40))
        assert len(d) > 0

    def test_decay_erange_661_663(self):
        """Test fetch_decay_radiation: e_range=(661, 663).................."""
        d = self.fetch(e_range=(661, 663))
        assert len(d) > 0
