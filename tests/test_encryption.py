import pytest
from app.encryption import aes, caesar, des, hill, playfair, rail_fence, vigenere


def test_classical_roundtrips():
    assert caesar.decrypt(caesar.encrypt('Attack at Dawn', '3'), '3') == 'Attack at Dawn'
    assert vigenere.decrypt(vigenere.encrypt('Attack at Dawn', 'lemon'), 'lemon') == 'Attack at Dawn'
    assert rail_fence.decrypt(rail_fence.encrypt('WEAREDISCOVERED', '3'), '3') == 'WEAREDISCOVERED'
    assert hill.decrypt(hill.encrypt('help', '3,3,2,5'), '3,3,2,5') == 'help'
    assert playfair.decrypt(playfair.encrypt('hide', 'monarchy'), 'monarchy').startswith('hide')


def test_aes_integrity():
    result = aes.encrypt('رسالة سرية', 'test-key')
    assert aes.decrypt(result['ciphertext'], 'test-key', result['nonce'], result['tag']) == 'رسالة سرية'
    with pytest.raises(Exception):
        aes.decrypt(result['ciphertext'][:-2] + 'xx', 'test-key', result['nonce'], result['tag'])


def test_des_roundtrip():
    result = des.encrypt('legacy demo', 'key')
    assert des.decrypt(result, 'key') == 'legacy demo'
