import numpy

#---------------------------------------------------------------------------------------
BLOCK_LENGTH = 64
KEY_LENGTH = 128
NUMBER_OF_ROUNDS = 25

SBOX = [2, 9, 7, 14, 1, 12, 10, 0, 4, 3, 8, 13, 15, 6, 5, 11]
PBOX = [20, 16, 28, 24, 17, 21, 25, 29,
		22, 18, 30, 26, 19, 23, 27, 31,
		11, 15,  3,  7, 14, 10,  6,  2,
		 9, 13,  1,  5, 12,  8,  4,  0]
#---------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------
def key_schedule_128(key):
	round_keys = []

	for i in range(NUMBER_OF_ROUNDS):

    # First step, add the round_key
		round_keys.append(key[-32:])

    # Then, key_update
		key = key_update(key, i)

	return round_keys

def key_update(key, round_counter):
  # Step 1. Left rotation by 13 bits.
	new_key = numpy.roll(key, -13)

  # Step 2. S-box operation
	sbox_index = get_fragment_int(new_key, 124, 128)
	new_key[124:128] = int_to_bin(SBOX[sbox_index], 4)

  # Step 3. S-box operation
	sbox_index = get_fragment_int(new_key, 120, 124)
	new_key[120:124] = int_to_bin(SBOX[sbox_index], 4)

  # Step 4. X-OR with round_counter
	chunk = get_fragment_int(new_key, 64, 69)
	new_key[64:69] = int_to_bin(chunk ^ (round_counter % 32), 5)

	return list(new_key)
#---------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------
def cipher(plaintext, keys):
	pl = plaintext[:32]
	pr = plaintext[32:]

	for i in range(NUMBER_OF_ROUNDS):
		f1, f2 = f_function(pl)

		pt = xor(f1, pr)    
    
		pt = xor(pt, xor(f2, keys[i]))

		pr = p_layer(pl)
		pl = p_layer(pt)
        
	return pl + pr

def f_function(pl):
	f1 = list(numpy.roll(pl, -3))
	f2 = list(numpy.roll(pl, 8))
  
	f1 = sbox_operation(f1)
	f2 = sbox_operation(f2)

	return f1, f2

def sbox_operation(_in):
	for i in range(0, 32, 4):    
		sbox_index = get_fragment_int(_in, i, i + 4)
		_in[i:i+4] = int_to_bin(SBOX[sbox_index], 4)

	return _in

# Operation: p_layer
def p_layer(state):
	state_copy = state[:] 
	state_copy.reverse() 
	new_state = [0] * (32)

  # Permutation of all the bits, according to pbox
	for i in range(len(new_state)):    
		new_state[31 - PBOX[i]] = state_copy[i]    
  
	return new_state

def xor(v1, v2):
	return [v1[i] ^ v2[i] for i in range(len(v1))]
#---------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------
def get_fragment_int(array, begin, end):
	return int("".join(map(str, array[begin:end])), 2)

def int_to_bin(number, w):
	return list(map(int, numpy.binary_repr(number, width=w)))

def pretty_print(array):
	_str = ""

	for i in range(0, 64, 4):
		_str += hex(get_fragment_int(array, i, i + 4)).split('0x')[1]

	return _str

def pretty_printK(array):
	_str = ""

	for i in range(0, 128, 4):
		_str += hex(get_fragment_int(array, i, i + 4)).split('0x')[1]
	return _str

#---------------------------------------------------------------------------------------

if __name__ == '__main__':
	plaintext = [0]*64
	k = [0]*128

	keys = key_schedule_128(k)
	ciphertext = cipher(plaintext, keys)

#	newplaintext = Decrypt(ciphertext, keys)

	print("plaintext     = ", pretty_print(plaintext))
	print("ciphertext    = ", pretty_print(ciphertext))
	print("key    = ", pretty_printK(k))
#	print("Desciphertext = ", pretty_print(newplaintext))
