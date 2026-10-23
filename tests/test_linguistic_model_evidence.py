"""Read actual finite observations; this command never dispatches inference.

Expected labels come from the authored case file, not a model's key. Retained
native responses remain model observations, not empirical linguistic gold.
"""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
CASES=json.loads((ROOT/'audit/linguistic-fullness-20261023/MODEL-CASES.json').read_text())['cases']
EVIDENCE=ROOT/'data/linguistic-fullness-20261023'


class LinguisticModelEvidence(unittest.TestCase):
    pass


def observation(case,index):
    def check(self):
        observation_index=json.loads((EVIDENCE/'model-observation-index.json').read_text())
        self.assertIn(case['id'],observation_index,'Current literal input has no actual observation')
        directory=ROOT/observation_index[case['id']]['directory']
        self.assertTrue((directory/'native-result.json').exists(),'Actual finite model observation missing; no inferred pass')
        raw=json.loads((directory/'native-result.json').read_text())
        self.assertEqual(raw['error'],'<nil>')
        self.assertGreaterEqual(len(raw['result']['receipt_ids']),1)
        self.assertTrue(raw['result']['context_snapshot_ids'])
        self.assertTrue((directory/'native-diagnostic.json').exists(),'Native diagnostic readback missing')
        inputs=json.loads((directory/'candidate-input.json').read_text())
        self.assertEqual(inputs[case['id']],case['input'])
        self.assertNotIn('expected',inputs[case['id']])
        self.assertNotIn('expected_reason',inputs[case['id']])
        self.assertNotIn('category',inputs[case['id']])
        hits=[x for x in raw['judgment']['verdicts'] if x['proposition_id']==case['id']]
        self.assertEqual(len(hits),1)
        got=hits[0]
        self.assertEqual(got['verdict'],case['expected'],case['reference_id']+': '+got['reason'])
        self.assertTrue(got['reason'].strip())
        if case['expected']=='unknown':
            self.assertTrue(got['missing_reason'],'Missing actual sound must remain explicitly unknown')
        else:
            self.assertTrue(got['evidence'],'A semantic verdict must identify its actual supplied context')
    return check


# Literal identities for the existing DAG owner parser; generated from MODEL-CASES.
class LinguisticObservedCases(unittest.TestCase):
    def test_p0001_positive(self):
        observation(CASES[0], 0)(self)

    def test_p0002_negative(self):
        observation(CASES[1], 1)(self)

    def test_p0003_negative(self):
        observation(CASES[2], 2)(self)

    def test_p0004_positive(self):
        observation(CASES[3], 3)(self)

    def test_p0005_positive(self):
        observation(CASES[4], 4)(self)

    def test_p0006_positive(self):
        observation(CASES[5], 5)(self)

    def test_p0007_positive(self):
        observation(CASES[6], 6)(self)

    def test_p0008_negative(self):
        observation(CASES[7], 7)(self)

    def test_p0009_positive(self):
        observation(CASES[8], 8)(self)

    def test_p0010_positive(self):
        observation(CASES[9], 9)(self)

    def test_p0011_positive(self):
        observation(CASES[10], 10)(self)

    def test_p0012_positive(self):
        observation(CASES[11], 11)(self)

    def test_p0013_positive(self):
        observation(CASES[12], 12)(self)

    def test_p0014_positive(self):
        observation(CASES[13], 13)(self)

    def test_p0015_negative(self):
        observation(CASES[14], 14)(self)

    def test_p0016_negative(self):
        observation(CASES[15], 15)(self)

    def test_p0017_positive(self):
        observation(CASES[16], 16)(self)

    def test_p0018_negative(self):
        observation(CASES[17], 17)(self)

    def test_p0019_positive(self):
        observation(CASES[18], 18)(self)

    def test_p0020_positive(self):
        observation(CASES[19], 19)(self)

    def test_p0021_positive(self):
        observation(CASES[20], 20)(self)

    def test_p0022_negative(self):
        observation(CASES[21], 21)(self)

    def test_p0023_positive(self):
        observation(CASES[22], 22)(self)

    def test_p0024_positive(self):
        observation(CASES[23], 23)(self)

    def test_p0025_positive(self):
        observation(CASES[24], 24)(self)

    def test_p0026_negative(self):
        observation(CASES[25], 25)(self)

    def test_p0027_positive(self):
        observation(CASES[26], 26)(self)

    def test_p0028_positive(self):
        observation(CASES[27], 27)(self)

    def test_p0029_positive(self):
        observation(CASES[28], 28)(self)

    def test_p0030_positive(self):
        observation(CASES[29], 29)(self)

    def test_p0031_positive(self):
        observation(CASES[30], 30)(self)

    def test_p0032_negative(self):
        observation(CASES[31], 31)(self)

    def test_p0033_negative(self):
        observation(CASES[32], 32)(self)

    def test_p0034_positive(self):
        observation(CASES[33], 33)(self)

    def test_p0035_negative(self):
        observation(CASES[34], 34)(self)

    def test_p0036_negative(self):
        observation(CASES[35], 35)(self)

    def test_p0037_positive(self):
        observation(CASES[36], 36)(self)

    def test_p0038_negative(self):
        observation(CASES[37], 37)(self)

    def test_p0039_negative(self):
        observation(CASES[38], 38)(self)

    def test_p0040_positive(self):
        observation(CASES[39], 39)(self)

    def test_p0041_positive(self):
        observation(CASES[40], 40)(self)

    def test_p0042_negative(self):
        observation(CASES[41], 41)(self)

    def test_p0043_negative(self):
        observation(CASES[42], 42)(self)

    def test_p0044_positive(self):
        observation(CASES[43], 43)(self)

    def test_p0045_positive(self):
        observation(CASES[44], 44)(self)

    def test_p0046_positive(self):
        observation(CASES[45], 45)(self)

    def test_p0047_positive(self):
        observation(CASES[46], 46)(self)

    def test_p0048_positive(self):
        observation(CASES[47], 47)(self)

    def test_p0049_positive(self):
        observation(CASES[48], 48)(self)

    def test_p0050_positive(self):
        observation(CASES[49], 49)(self)

    def test_p0051_positive(self):
        observation(CASES[50], 50)(self)

    def test_p0052_positive(self):
        observation(CASES[51], 51)(self)

    def test_p0053_negative(self):
        observation(CASES[52], 52)(self)

    def test_p0054_negative(self):
        observation(CASES[53], 53)(self)

    def test_p0055_positive(self):
        observation(CASES[54], 54)(self)

    def test_p0056_negative(self):
        observation(CASES[55], 55)(self)

    def test_p0057_positive(self):
        observation(CASES[56], 56)(self)

    def test_p0058_positive(self):
        observation(CASES[57], 57)(self)

    def test_p0059_positive(self):
        observation(CASES[58], 58)(self)

    def test_p0060_positive(self):
        observation(CASES[59], 59)(self)

    def test_p0061_negative(self):
        observation(CASES[60], 60)(self)

    def test_p0062_positive(self):
        observation(CASES[61], 61)(self)

    def test_p0063_positive(self):
        observation(CASES[62], 62)(self)

    def test_p0064_negative(self):
        observation(CASES[63], 63)(self)

    def test_p0065_positive(self):
        observation(CASES[64], 64)(self)

    def test_p0066_negative(self):
        observation(CASES[65], 65)(self)

    def test_p0067_positive(self):
        observation(CASES[66], 66)(self)

    def test_p0068_positive(self):
        observation(CASES[67], 67)(self)

    def test_p0069_positive(self):
        observation(CASES[68], 68)(self)

    def test_p0070_negative(self):
        observation(CASES[69], 69)(self)

    def test_p0071_negative(self):
        observation(CASES[70], 70)(self)

    def test_p0072_positive(self):
        observation(CASES[71], 71)(self)

    def test_p0073_positive(self):
        observation(CASES[72], 72)(self)

    def test_p0074_negative(self):
        observation(CASES[73], 73)(self)

    def test_p0075_positive(self):
        observation(CASES[74], 74)(self)

    def test_p0076_positive(self):
        observation(CASES[75], 75)(self)

    def test_p0077_positive(self):
        observation(CASES[76], 76)(self)

    def test_p0078_positive(self):
        observation(CASES[77], 77)(self)

    def test_p0079_positive(self):
        observation(CASES[78], 78)(self)

    def test_p0080_positive(self):
        observation(CASES[79], 79)(self)

    def test_p0081_negative(self):
        observation(CASES[80], 80)(self)

    def test_p0082_positive(self):
        observation(CASES[81], 81)(self)

    def test_p0083_positive(self):
        observation(CASES[82], 82)(self)

    def test_p0084_negative(self):
        observation(CASES[83], 83)(self)

    def test_p0085_negative(self):
        observation(CASES[84], 84)(self)

    def test_p0086_positive(self):
        observation(CASES[85], 85)(self)

    def test_p0087_negative(self):
        observation(CASES[86], 86)(self)

    def test_p0088_negative(self):
        observation(CASES[87], 87)(self)

    def test_p0089_positive(self):
        observation(CASES[88], 88)(self)

    def test_p0090_negative(self):
        observation(CASES[89], 89)(self)

    def test_p0091_positive(self):
        observation(CASES[90], 90)(self)

    def test_p0092_positive(self):
        observation(CASES[91], 91)(self)

    def test_p0093_positive(self):
        observation(CASES[92], 92)(self)

    def test_p0094_negative(self):
        observation(CASES[93], 93)(self)

    def test_p0095_positive(self):
        observation(CASES[94], 94)(self)

    def test_p0096_negative(self):
        observation(CASES[95], 95)(self)

    def test_p0097_negative(self):
        observation(CASES[96], 96)(self)

    def test_p0098_positive(self):
        observation(CASES[97], 97)(self)

    def test_p0099_positive(self):
        observation(CASES[98], 98)(self)

    def test_p0100_positive(self):
        observation(CASES[99], 99)(self)

    def test_p0101_positive(self):
        observation(CASES[100], 100)(self)

    def test_p0102_positive(self):
        observation(CASES[101], 101)(self)

    def test_p0103_negative(self):
        observation(CASES[102], 102)(self)

    def test_p0104_negative(self):
        observation(CASES[103], 103)(self)

    def test_p0105_positive(self):
        observation(CASES[104], 104)(self)

    def test_p0106_positive(self):
        observation(CASES[105], 105)(self)

    def test_p0107_positive(self):
        observation(CASES[106], 106)(self)

    def test_p0108_positive(self):
        observation(CASES[107], 107)(self)

    def test_p0109_positive(self):
        observation(CASES[108], 108)(self)

    def test_p0110_positive(self):
        observation(CASES[109], 109)(self)

    def test_p0111_positive(self):
        observation(CASES[110], 110)(self)

    def test_p0112_negative(self):
        observation(CASES[111], 111)(self)

    def test_p0113_negative(self):
        observation(CASES[112], 112)(self)

    def test_p0114_negative(self):
        observation(CASES[113], 113)(self)

    def test_p0115_negative(self):
        observation(CASES[114], 114)(self)

    def test_p0116_positive(self):
        observation(CASES[115], 115)(self)

    def test_p0117_positive(self):
        observation(CASES[116], 116)(self)

    def test_p0118_negative(self):
        observation(CASES[117], 117)(self)

    def test_p0119_positive(self):
        observation(CASES[118], 118)(self)

    def test_p0120_positive(self):
        observation(CASES[119], 119)(self)

    def test_p0121_positive(self):
        observation(CASES[120], 120)(self)

    def test_p0122_positive(self):
        observation(CASES[121], 121)(self)

    def test_p0123_positive(self):
        observation(CASES[122], 122)(self)

    def test_p0124_negative(self):
        observation(CASES[123], 123)(self)

    def test_p0125_positive(self):
        observation(CASES[124], 124)(self)

    def test_p0126_positive(self):
        observation(CASES[125], 125)(self)

    def test_p0127_positive(self):
        observation(CASES[126], 126)(self)

    def test_p0128_positive(self):
        observation(CASES[127], 127)(self)

    def test_p0129_positive(self):
        observation(CASES[128], 128)(self)

    def test_p0130_positive(self):
        observation(CASES[129], 129)(self)

    def test_p0131_positive(self):
        observation(CASES[130], 130)(self)

    def test_p0132_positive(self):
        observation(CASES[131], 131)(self)

    def test_p0133_positive(self):
        observation(CASES[132], 132)(self)

    def test_p0134_positive(self):
        observation(CASES[133], 133)(self)

    def test_p0135_negative(self):
        observation(CASES[134], 134)(self)

    def test_p0136_negative(self):
        observation(CASES[135], 135)(self)

    def test_p0137_positive(self):
        observation(CASES[136], 136)(self)

    def test_p0138_positive(self):
        observation(CASES[137], 137)(self)

    def test_p0139_positive(self):
        observation(CASES[138], 138)(self)

    def test_p0140_positive(self):
        observation(CASES[139], 139)(self)

    def test_p0141_positive(self):
        observation(CASES[140], 140)(self)

    def test_p0142_positive(self):
        observation(CASES[141], 141)(self)

    def test_p0143_positive(self):
        observation(CASES[142], 142)(self)

    def test_p0144_negative(self):
        observation(CASES[143], 143)(self)

    def test_p0145_positive(self):
        observation(CASES[144], 144)(self)

    def test_p0146_positive(self):
        observation(CASES[145], 145)(self)

    def test_p0147_positive(self):
        observation(CASES[146], 146)(self)

    def test_p0148_positive(self):
        observation(CASES[147], 147)(self)

    def test_p0149_negative(self):
        observation(CASES[148], 148)(self)

    def test_p0150_positive(self):
        observation(CASES[149], 149)(self)

    def test_p0151_positive(self):
        observation(CASES[150], 150)(self)

    def test_p0152_positive(self):
        observation(CASES[151], 151)(self)

    def test_p0153_positive(self):
        observation(CASES[152], 152)(self)

    def test_p0154_negative(self):
        observation(CASES[153], 153)(self)

    def test_p0155_positive(self):
        observation(CASES[154], 154)(self)

    def test_p0156_negative(self):
        observation(CASES[155], 155)(self)

    def test_p0157_negative(self):
        observation(CASES[156], 156)(self)

    def test_p0158_positive(self):
        observation(CASES[157], 157)(self)

    def test_p0159_negative(self):
        observation(CASES[158], 158)(self)

    def test_p0160_positive(self):
        observation(CASES[159], 159)(self)

    def test_p0161_negative(self):
        observation(CASES[160], 160)(self)

    def test_p0162_negative(self):
        observation(CASES[161], 161)(self)

    def test_p0163_negative(self):
        observation(CASES[162], 162)(self)

    def test_p0164_positive(self):
        observation(CASES[163], 163)(self)

    def test_p0165_positive(self):
        observation(CASES[164], 164)(self)

    def test_p0166_positive(self):
        observation(CASES[165], 165)(self)

    def test_p0167_positive(self):
        observation(CASES[166], 166)(self)

    def test_p0168_negative(self):
        observation(CASES[167], 167)(self)

    def test_p0169_positive(self):
        observation(CASES[168], 168)(self)

    def test_p0170_negative(self):
        observation(CASES[169], 169)(self)

    def test_p0171_negative(self):
        observation(CASES[170], 170)(self)

    def test_p0172_positive(self):
        observation(CASES[171], 171)(self)

    def test_p0173_positive(self):
        observation(CASES[172], 172)(self)

    def test_p0174_positive(self):
        observation(CASES[173], 173)(self)

    def test_p0175_positive(self):
        observation(CASES[174], 174)(self)

    def test_p0176_positive(self):
        observation(CASES[175], 175)(self)

    def test_p0177_positive(self):
        observation(CASES[176], 176)(self)

    def test_p0178_positive(self):
        observation(CASES[177], 177)(self)

    def test_p0179_positive(self):
        observation(CASES[178], 178)(self)

    def test_p0180_negative(self):
        observation(CASES[179], 179)(self)

    def test_p0181_positive(self):
        observation(CASES[180], 180)(self)

    def test_p0182_negative(self):
        observation(CASES[181], 181)(self)

    def test_p0183_positive(self):
        observation(CASES[182], 182)(self)

    def test_p0184_positive(self):
        observation(CASES[183], 183)(self)

    def test_p0185_negative(self):
        observation(CASES[184], 184)(self)

    def test_p0186_positive(self):
        observation(CASES[185], 185)(self)

    def test_p0187_negative(self):
        observation(CASES[186], 186)(self)

    def test_p0188_negative(self):
        observation(CASES[187], 187)(self)

    def test_p0189_negative(self):
        observation(CASES[188], 188)(self)

    def test_p0190_positive(self):
        observation(CASES[189], 189)(self)

    def test_p0191_positive(self):
        observation(CASES[190], 190)(self)

    def test_p0192_positive(self):
        observation(CASES[191], 191)(self)

    def test_p0193_positive(self):
        observation(CASES[192], 192)(self)

    def test_p0194_negative(self):
        observation(CASES[193], 193)(self)

    def test_p0195_positive(self):
        observation(CASES[194], 194)(self)

    def test_p0196_positive(self):
        observation(CASES[195], 195)(self)

    def test_p0197_positive(self):
        observation(CASES[196], 196)(self)

    def test_p0198_positive(self):
        observation(CASES[197], 197)(self)

    def test_p0199_positive(self):
        observation(CASES[198], 198)(self)

    def test_p0200_negative(self):
        observation(CASES[199], 199)(self)

    def test_p0201_positive(self):
        observation(CASES[200], 200)(self)

    def test_p0202_negative(self):
        observation(CASES[201], 201)(self)

    def test_p0203_positive(self):
        observation(CASES[202], 202)(self)

    def test_p0204_negative(self):
        observation(CASES[203], 203)(self)

    def test_p0205_positive(self):
        observation(CASES[204], 204)(self)

    def test_p0206_negative(self):
        observation(CASES[205], 205)(self)

    def test_p0207_positive(self):
        observation(CASES[206], 206)(self)

    def test_p0208_positive(self):
        observation(CASES[207], 207)(self)

    def test_p0209_negative(self):
        observation(CASES[208], 208)(self)

    def test_p0210_positive(self):
        observation(CASES[209], 209)(self)

    def test_p0211_positive(self):
        observation(CASES[210], 210)(self)

    def test_p0212_positive(self):
        observation(CASES[211], 211)(self)

    def test_p0213_positive(self):
        observation(CASES[212], 212)(self)

    def test_p0214_positive(self):
        observation(CASES[213], 213)(self)

    def test_p0215_negative(self):
        observation(CASES[214], 214)(self)

    def test_p0216_positive(self):
        observation(CASES[215], 215)(self)

    def test_p0217_negative(self):
        observation(CASES[216], 216)(self)

    def test_p0218_positive(self):
        observation(CASES[217], 217)(self)

    def test_p0219_positive(self):
        observation(CASES[218], 218)(self)

    def test_p0220_negative(self):
        observation(CASES[219], 219)(self)

    def test_p0221_negative(self):
        observation(CASES[220], 220)(self)

    def test_p0222_positive(self):
        observation(CASES[221], 221)(self)

    def test_p0223_positive(self):
        observation(CASES[222], 222)(self)

    def test_p0224_positive(self):
        observation(CASES[223], 223)(self)

    def test_p0225_negative(self):
        observation(CASES[224], 224)(self)

    def test_p0226_positive(self):
        observation(CASES[225], 225)(self)

    def test_p0227_positive(self):
        observation(CASES[226], 226)(self)

    def test_p0228_positive(self):
        observation(CASES[227], 227)(self)

    def test_p0229_negative(self):
        observation(CASES[228], 228)(self)

    def test_p0230_positive(self):
        observation(CASES[229], 229)(self)

    def test_p0231_positive(self):
        observation(CASES[230], 230)(self)

    def test_p0232_negative(self):
        observation(CASES[231], 231)(self)

    def test_p0233_positive(self):
        observation(CASES[232], 232)(self)

    def test_p0234_positive(self):
        observation(CASES[233], 233)(self)

    def test_p0235_negative(self):
        observation(CASES[234], 234)(self)

    def test_p0236_positive(self):
        observation(CASES[235], 235)(self)

    def test_p0237_positive(self):
        observation(CASES[236], 236)(self)

    def test_p0238_positive(self):
        observation(CASES[237], 237)(self)

    def test_p0239_negative(self):
        observation(CASES[238], 238)(self)

    def test_p0240_positive(self):
        observation(CASES[239], 239)(self)

    def test_p0241_negative(self):
        observation(CASES[240], 240)(self)

    def test_p0242_positive(self):
        observation(CASES[241], 241)(self)

    def test_p0243_positive(self):
        observation(CASES[242], 242)(self)

    def test_p0244_positive(self):
        observation(CASES[243], 243)(self)

    def test_p0245_positive(self):
        observation(CASES[244], 244)(self)

    def test_p0246_positive(self):
        observation(CASES[245], 245)(self)

    def test_p0247_negative(self):
        observation(CASES[246], 246)(self)

    def test_p0248_positive(self):
        observation(CASES[247], 247)(self)

    def test_p0249_positive(self):
        observation(CASES[248], 248)(self)

    def test_p0250_positive(self):
        observation(CASES[249], 249)(self)

    def test_p0251_negative(self):
        observation(CASES[250], 250)(self)

    def test_p0252_positive(self):
        observation(CASES[251], 251)(self)

    def test_p0253_positive(self):
        observation(CASES[252], 252)(self)

    def test_p0254_positive(self):
        observation(CASES[253], 253)(self)

    def test_p0255_negative(self):
        observation(CASES[254], 254)(self)

    def test_p0256_negative(self):
        observation(CASES[255], 255)(self)

    def test_p0257_positive(self):
        observation(CASES[256], 256)(self)

    def test_p0258_negative(self):
        observation(CASES[257], 257)(self)

    def test_p0259_positive(self):
        observation(CASES[258], 258)(self)

    def test_p0260_negative(self):
        observation(CASES[259], 259)(self)

    def test_p0261_positive(self):
        observation(CASES[260], 260)(self)

    def test_p0262_negative(self):
        observation(CASES[261], 261)(self)

    def test_p0263_positive(self):
        observation(CASES[262], 262)(self)

    def test_p0264_negative(self):
        observation(CASES[263], 263)(self)

    def test_p0265_negative(self):
        observation(CASES[264], 264)(self)

    def test_p0266_negative(self):
        observation(CASES[265], 265)(self)

    def test_p0267_positive(self):
        observation(CASES[266], 266)(self)

    def test_p0268_positive(self):
        observation(CASES[267], 267)(self)

    def test_p0269_negative(self):
        observation(CASES[268], 268)(self)

    def test_p0270_positive(self):
        observation(CASES[269], 269)(self)

    def test_p0271_negative(self):
        observation(CASES[270], 270)(self)

    def test_p0272_negative(self):
        observation(CASES[271], 271)(self)

    def test_p0273_positive(self):
        observation(CASES[272], 272)(self)

    def test_p0274_positive(self):
        observation(CASES[273], 273)(self)

    def test_p0275_negative(self):
        observation(CASES[274], 274)(self)

    def test_p0276_positive(self):
        observation(CASES[275], 275)(self)

    def test_p0277_positive(self):
        observation(CASES[276], 276)(self)

    def test_p0278_positive(self):
        observation(CASES[277], 277)(self)

    def test_p0279_positive(self):
        observation(CASES[278], 278)(self)

    def test_p0280_positive(self):
        observation(CASES[279], 279)(self)

    def test_p0281_positive(self):
        observation(CASES[280], 280)(self)

    def test_p0282_positive(self):
        observation(CASES[281], 281)(self)

    def test_p0283_positive(self):
        observation(CASES[282], 282)(self)

    def test_p0284_positive(self):
        observation(CASES[283], 283)(self)

    def test_p0285_positive(self):
        observation(CASES[284], 284)(self)

    def test_p0286_positive(self):
        observation(CASES[285], 285)(self)

    def test_p0287_negative(self):
        observation(CASES[286], 286)(self)

    def test_p0288_positive(self):
        observation(CASES[287], 287)(self)

    def test_p0289_positive(self):
        observation(CASES[288], 288)(self)

    def test_p0290_negative(self):
        observation(CASES[289], 289)(self)

    def test_p0291_positive(self):
        observation(CASES[290], 290)(self)

    def test_p0292_positive(self):
        observation(CASES[291], 291)(self)

    def test_p0293_negative(self):
        observation(CASES[292], 292)(self)

    def test_p0294_negative(self):
        observation(CASES[293], 293)(self)

    def test_p0295_negative(self):
        observation(CASES[294], 294)(self)

    def test_p0296_positive(self):
        observation(CASES[295], 295)(self)

    def test_p0297_positive(self):
        observation(CASES[296], 296)(self)

    def test_p0298_positive(self):
        observation(CASES[297], 297)(self)

    def test_p0299_negative(self):
        observation(CASES[298], 298)(self)

    def test_p0300_positive(self):
        observation(CASES[299], 299)(self)

    def test_p0301_positive(self):
        observation(CASES[300], 300)(self)

    def test_p0302_negative(self):
        observation(CASES[301], 301)(self)

    def test_p0303_positive(self):
        observation(CASES[302], 302)(self)

    def test_p0304_negative(self):
        observation(CASES[303], 303)(self)

    def test_p0305_negative(self):
        observation(CASES[304], 304)(self)

    def test_p0306_positive(self):
        observation(CASES[305], 305)(self)

    def test_p0307_positive(self):
        observation(CASES[306], 306)(self)

    def test_p0308_positive(self):
        observation(CASES[307], 307)(self)

    def test_p0309_positive(self):
        observation(CASES[308], 308)(self)

    def test_p0310_positive(self):
        observation(CASES[309], 309)(self)

    def test_p0311_negative(self):
        observation(CASES[310], 310)(self)

    def test_p0312_negative(self):
        observation(CASES[311], 311)(self)

    def test_p0313_negative(self):
        observation(CASES[312], 312)(self)

    def test_p0314_positive(self):
        observation(CASES[313], 313)(self)

    def test_p0315_positive(self):
        observation(CASES[314], 314)(self)

    def test_p0316_negative(self):
        observation(CASES[315], 315)(self)

    def test_p0317_negative(self):
        observation(CASES[316], 316)(self)

    def test_p0318_positive(self):
        observation(CASES[317], 317)(self)

    def test_p0319_positive(self):
        observation(CASES[318], 318)(self)

    def test_p0320_positive(self):
        observation(CASES[319], 319)(self)

    def test_p0321_positive(self):
        observation(CASES[320], 320)(self)

    def test_p0322_negative(self):
        observation(CASES[321], 321)(self)

    def test_p0323_positive(self):
        observation(CASES[322], 322)(self)

    def test_p0324_negative(self):
        observation(CASES[323], 323)(self)

    def test_p0325_negative(self):
        observation(CASES[324], 324)(self)

    def test_p0326_positive(self):
        observation(CASES[325], 325)(self)

    def test_p0327_negative(self):
        observation(CASES[326], 326)(self)

    def test_p0328_positive(self):
        observation(CASES[327], 327)(self)

    def test_p0329_negative(self):
        observation(CASES[328], 328)(self)

    def test_p0330_positive(self):
        observation(CASES[329], 329)(self)

    def test_p0331_positive(self):
        observation(CASES[330], 330)(self)

    def test_p0332_positive(self):
        observation(CASES[331], 331)(self)

    def test_p0333_negative(self):
        observation(CASES[332], 332)(self)

    def test_p0334_positive(self):
        observation(CASES[333], 333)(self)

    def test_p0335_positive(self):
        observation(CASES[334], 334)(self)

    def test_p0336_negative(self):
        observation(CASES[335], 335)(self)

    def test_p0337_negative(self):
        observation(CASES[336], 336)(self)

    def test_p0338_positive(self):
        observation(CASES[337], 337)(self)

    def test_p0339_positive(self):
        observation(CASES[338], 338)(self)

    def test_p0340_negative(self):
        observation(CASES[339], 339)(self)

    def test_p0341_positive(self):
        observation(CASES[340], 340)(self)

    def test_p0342_positive(self):
        observation(CASES[341], 341)(self)

    def test_p0343_positive(self):
        observation(CASES[342], 342)(self)

    def test_p0344_positive(self):
        observation(CASES[343], 343)(self)

    def test_p0345_negative(self):
        observation(CASES[344], 344)(self)

    def test_p0346_positive(self):
        observation(CASES[345], 345)(self)

    def test_p0347_negative(self):
        observation(CASES[346], 346)(self)

    def test_p0348_positive(self):
        observation(CASES[347], 347)(self)

    def test_p0349_negative(self):
        observation(CASES[348], 348)(self)

    def test_p0350_negative(self):
        observation(CASES[349], 349)(self)

    def test_p0351_positive(self):
        observation(CASES[350], 350)(self)

    def test_p0352_positive(self):
        observation(CASES[351], 351)(self)

    def test_p0353_negative(self):
        observation(CASES[352], 352)(self)

    def test_p0354_positive(self):
        observation(CASES[353], 353)(self)

    def test_p0355_positive(self):
        observation(CASES[354], 354)(self)

    def test_p0356_positive(self):
        observation(CASES[355], 355)(self)

    def test_p0357_positive(self):
        observation(CASES[356], 356)(self)

    def test_p0358_negative(self):
        observation(CASES[357], 357)(self)

    def test_p0359_negative(self):
        observation(CASES[358], 358)(self)

    def test_p0360_positive(self):
        observation(CASES[359], 359)(self)

    def test_p0361_negative(self):
        observation(CASES[360], 360)(self)

    def test_p0362_negative(self):
        observation(CASES[361], 361)(self)

    def test_p0363_negative(self):
        observation(CASES[362], 362)(self)

    def test_p0364_positive(self):
        observation(CASES[363], 363)(self)

    def test_p0365_negative(self):
        observation(CASES[364], 364)(self)

    def test_p0366_positive(self):
        observation(CASES[365], 365)(self)

    def test_p0367_negative(self):
        observation(CASES[366], 366)(self)

    def test_p0368_positive(self):
        observation(CASES[367], 367)(self)

    def test_p0369_positive(self):
        observation(CASES[368], 368)(self)

    def test_p0370_positive(self):
        observation(CASES[369], 369)(self)

    def test_p0371_negative(self):
        observation(CASES[370], 370)(self)

    def test_p0372_positive(self):
        observation(CASES[371], 371)(self)

    def test_p0373_positive(self):
        observation(CASES[372], 372)(self)

    def test_p0374_negative(self):
        observation(CASES[373], 373)(self)

    def test_p0375_positive(self):
        observation(CASES[374], 374)(self)

    def test_p0376_positive(self):
        observation(CASES[375], 375)(self)

    def test_p0377_positive(self):
        observation(CASES[376], 376)(self)

    def test_p0378_negative(self):
        observation(CASES[377], 377)(self)

    def test_p0379_positive(self):
        observation(CASES[378], 378)(self)

    def test_p0380_positive(self):
        observation(CASES[379], 379)(self)

    def test_p0381_positive(self):
        observation(CASES[380], 380)(self)

    def test_p0382_positive(self):
        observation(CASES[381], 381)(self)

    def test_p0383_positive(self):
        observation(CASES[382], 382)(self)

    def test_p0384_positive(self):
        observation(CASES[383], 383)(self)

    def test_p0385_positive(self):
        observation(CASES[384], 384)(self)

    def test_p0386_positive(self):
        observation(CASES[385], 385)(self)

    def test_p0387_negative(self):
        observation(CASES[386], 386)(self)

    def test_p0388_positive(self):
        observation(CASES[387], 387)(self)

    def test_p0389_positive(self):
        observation(CASES[388], 388)(self)

    def test_p0390_negative(self):
        observation(CASES[389], 389)(self)

    def test_p0391_negative(self):
        observation(CASES[390], 390)(self)

    def test_p0392_positive(self):
        observation(CASES[391], 391)(self)

    def test_p0393_positive(self):
        observation(CASES[392], 392)(self)

    def test_p0394_negative(self):
        observation(CASES[393], 393)(self)

    def test_p0395_positive(self):
        observation(CASES[394], 394)(self)

    def test_p0396_negative(self):
        observation(CASES[395], 395)(self)

    def test_p0397_positive(self):
        observation(CASES[396], 396)(self)

    def test_p0398_negative(self):
        observation(CASES[397], 397)(self)

    def test_p0399_positive(self):
        observation(CASES[398], 398)(self)

    def test_p0400_positive(self):
        observation(CASES[399], 399)(self)

    def test_p0401_positive(self):
        observation(CASES[400], 400)(self)

    def test_p0402_positive(self):
        observation(CASES[401], 401)(self)

    def test_p0403_positive(self):
        observation(CASES[402], 402)(self)

    def test_p0404_positive(self):
        observation(CASES[403], 403)(self)

    def test_p0405_positive(self):
        observation(CASES[404], 404)(self)

    def test_p0406_positive(self):
        observation(CASES[405], 405)(self)

    def test_p0407_positive(self):
        observation(CASES[406], 406)(self)

    def test_p0408_positive(self):
        observation(CASES[407], 407)(self)

    def test_p0409_positive(self):
        observation(CASES[408], 408)(self)

    def test_p0410_negative(self):
        observation(CASES[409], 409)(self)

    def test_p0411_positive(self):
        observation(CASES[410], 410)(self)

    def test_p0412_positive(self):
        observation(CASES[411], 411)(self)

    def test_p0413_negative(self):
        observation(CASES[412], 412)(self)

    def test_p0414_positive(self):
        observation(CASES[413], 413)(self)

    def test_p0415_negative(self):
        observation(CASES[414], 414)(self)

    def test_p0416_positive(self):
        observation(CASES[415], 415)(self)


if __name__=='__main__':
    unittest.main(verbosity=2)
