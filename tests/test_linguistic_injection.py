"""Real phone-plan compiler on constructed tokens, not observed pronunciation."""
import pathlib
import sys
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'services/speech'))
from acoustic_alignment import compile_scopes
from acoustic_plan import scopes


class LinguisticInjection(unittest.TestCase):
    def compile(self,text,word,reference,changed,tail=' me',unit='contrast',missing=None):
        op=dict(unit_id=unit,scope=dict(start=0,end=len(word)),controller='phone_pair',parameters=dict(reference_ipa=reference,mutated_ipa=changed))
        turn=dict(operations=[dict(text=text)],acoustic_edits=[op])
        scopes(turn)
        piece=dict(operations=[dict(text=text)],g2p_tokens=[dict(text=word,phonemes=reference,whitespace=' '),dict(text=tail.strip(),phonemes='mi',whitespace='')])
        vocabulary={x:1 for x in reference+changed+'mi '}
        if missing:vocabulary.pop(missing,None)
        compile_scopes(piece,[op],0,vocabulary)
        return piece

    def test_metathesis_target_positive(self):
        p=self.compile('Ask me','Ask','æsk','æks')
        self.assertEqual(p['operations'][0]['text'],'Ask me')
        self.assertEqual(p['compiled_phonemes'],'æsk mi')
        self.assertEqual(p['phone_variants']['contrast']['compiled_phonemes'],'æks mi')

    def test_allowed_metathesis_control_negative(self):
        # Reverse direction remains renderable; the compiler is not a dialect judge.
        p=self.compile('Ask me','Ask','æks','æsk',unit='permitted_control')
        self.assertEqual(p['compiled_phonemes'],'æks mi')
        self.assertEqual(p['phone_variants']['permitted_control']['compiled_phonemes'],'æsk mi')
        self.assertNotIn('expected_judgment',p)

    def test_internal_vowel_elision_positive(self):
        p=self.compile('Camera me','Camera','kæməɹə','kæmɹə')
        self.assertEqual(p['compiled_phonemes'],'kæməɹə mi')
        self.assertEqual(p['phone_variants']['contrast']['compiled_phonemes'],'kæmɹə mi')

    def test_spelling_does_not_force_syllables_negative(self):
        p=self.compile('Camera me','Camera','kæmɹə','kæməɹə',unit='permitted_control')
        self.assertEqual(p['operations'][0]['text'],'Camera me')
        self.assertEqual(p['compiled_phonemes'],'kæmɹə mi')

    def test_missing_model_phone_negative(self):
        with self.assertRaises(ValueError):
            self.compile('Ask me','Ask','æsk','æks',missing='k')

    def test_one_repair_unit_positive(self):
        p=self.compile('Ask me','Ask','æsk','æks',unit='one_word_repair')
        self.assertEqual(list(p['phone_variants']),['one_word_repair'])
        self.assertEqual(len(p['acoustic_token_scopes']),1)
        self.assertEqual(p['acoustic_token_scopes'][0]['unit_id'],'one_word_repair')


if __name__=='__main__':unittest.main(verbosity=2)
