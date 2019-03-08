"""	Implementation of GIFT LWC	"""

import numpy

#------------------------------------------------Boxes---------------------------------------------------------
#-----------------Sizes---------------------
BLOCK_SIZE = 64
KEY_SIZE = 128
ROUNDS = 28
#-------------------------------------------

# Definition of the SBOX, used in subcells method
SBOX = [1, 10, 4, 12, 6, 15, 3, 9, 2, 13, 11, 7, 5, 0, 8, 14]
SBOX_INV = [13, 0, 8, 6, 2, 12, 4, 11, 14, 7, 1, 10, 3, 9, 15, 5]

# Definition of the PBOX, used in Permbits method
PBOX = [0, 17, 34, 51, 48, 1, 18, 35, 32, 49, 2, 19, 16, 33, 50, 3,
		4, 21, 38, 55, 52, 5, 22, 39, 36, 53, 6, 23, 20, 37, 54, 7,
		8, 25, 42, 59, 56, 9, 26, 43, 40, 57, 10, 27, 24, 41, 58, 11,
		12, 29, 46, 63, 60, 13, 30, 47, 44, 61, 14, 31, 28, 45, 62, 15]

PBOX_INV = [0, 5, 10, 15, 16, 21, 26, 31, 32, 37, 42, 47, 48, 53, 58, 63,
			12, 1, 6, 11, 28, 17, 22, 27, 44, 33, 38, 43, 60, 49, 54, 59,
			8, 13, 2, 7, 24, 29, 18, 23, 40, 45, 34, 39, 56, 61, 50, 55,
			4, 9, 14, 3, 20, 25, 30, 19, 36, 41, 46, 35, 52, 57, 62, 51]

# Definition of the NUMBER_OF_ROUNDS constants
CONSTANTS = [0x01, 0x03, 0x07, 0x0f, 0x1f, 0x3e, 0x3d, 0x3b, 0x37, 0x2f, 0x1e, 0x3c, 0x39, 0x33, 0x27, 0x0e,
			0x1d, 0x3a, 0x35, 0x2b, 0x16, 0x2c, 0x18, 0x30, 0x21, 0x02, 0x05, 0x0b, 0x17, 0x2e, 0x1c, 0x38,
			0x31, 0x23, 0x06, 0x0d, 0x1b, 0x36, 0x2d, 0x1a, 0x34, 0x29, 0x12, 0x24, 0x08, 0x11, 0x22, 0x04]

CONSTANTS_28 = CONSTANTS[:28]
#--------------------------------------------------------------------------------------------------------------


#-------------------------------------------Key Schedule---------------------------------------------
#--------------------------------------------------------------------------------
# Method that generates the 28 keys of 32 bits that are used in the algorithm
def KeySchedule(key):	
	SubKeys = []	#Array that contains the subkeys
	#state = key     #State of key

	for i in range(ROUNDS):
		#--------Key State Update----------
		SubKeys.append(key[-32:]) # Get U <-[32-16]"K1" and V <-[16-0]"K0"
		#----------------------------------

		#--------Key State Update----------
		key = key_state_update(key) #Update of the state of key
		#----------------------------------
	
	return SubKeys #Return the key with all subkeys
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method that updates the key, in each iteration of generate_round_keys method
def key_state_update(key):
	k1 = key[-32:-16]	#U
	k0 = key[-16:] 		#V
	
	#-------------------Rot-----------------------
	k1 = list(numpy.roll(k1, 2))	#k1 >>> 2
	k0 = list(numpy.roll(k0, 12))   #k0 >>> 12
	#---------------------------------------------
	k1 += k0	
	k1 += key

	return k1[:128]
#--------------------------------------------------------------------------------
	
	
def get_fragment_int(array, begin, end):
	return int("".join(map(str, array[begin:end])), 2)

def int_to_bin(number, w):
	return map(int, numpy.binary_repr(number, width=w))

#-------------------------------------------------------------------------------------------


#----------------------------------------Encrypt--------------------------------------------
#Each round of GIFT consists of 3 steps: SubCells, PermBits and AddRoundKey

def Encrypt(plaintext, keys):
	ciphertext = plaintext

	# Rounds of the algorithm.
	for i in range(0, ROUNDS):
		ciphertext = subcells(ciphertext)
		
		ciphertext = permbits(ciphertext)

		ciphertext = add_round_key(ciphertext, keys[i], i)

	return ciphertext
#-------------------------------Subcells-----------------------------------
#1. Put the content into a box (SubCells)
def subcells(subcell):
	#aux = BLOCK_SIZE/4
	#aux = 16
	for i in range(16):
		pos = 4 * i
		#------Convert bin to dec------- 
		index = get_fragment_int(subcell, pos, pos + 4)
		#-------------------------------
		#--------------SBOX operation-------------------
		subcell[pos:pos+4] = int_to_bin(SBOX[index], 4)	#Convert int to bin
		#-----------------------------------------------

	return subcell
#--------------------------------------------------------------------------

#-------------------------------PermBits-----------------------------------
#2. Wrap the ribbon around the box (PermBits)
def permbits(ciphertext):
	permutation = [0] * BLOCK_SIZE
	aux = BLOCK_SIZE - 1
	#----------------Permutation-----------------
	for i in range(BLOCK_SIZE):
		permutation[aux - PBOX[i]] = ciphertext[aux - i]
	#--------------------------------------------
	return permutation
#--------------------------------------------------------------------------

#------------------------------AddRoundKey---------------------------------
#3. Tie a knot to secure the content (AddRoundKey)
def add_round_key(ciphertext, key, Nround):
	U = key[:16]    #U <- 32-16
	V = key[16:]    #V <- 16-0
	temp = ciphertext.copy()
	c = int_to_bin(CONSTANTS_28[Nround], 6)
	b = 3
	aux = BLOCK_SIZE - 1
	
	#------------XOR U and V with b4i+1 and b4i-----------
	for i in range(16):
		indexU = (4*i)+1
		indexV = 4*i
		temp[aux - indexU] ^= U[15 - i] #b4i+1 <- b4i+1 xor ui
		temp[aux - indexV] ^= V[15 - i] #b4i <- b4i xor vi
	#-----------------------------------------------------

	temp.reverse()   #bn-1 

	#---------------XOR with constants---------------------------
	temp[BLOCK_SIZE - 1] ^= 1     #bn-1 <- bn-1 xor 1
	
	for i in range(5):
		temp[b] ^= c[5 - (i+1)]     #b3 XOR C0, b7 XOR C1, b11 XOR C2, b15 XOR C3, b19 XOR C4, b23 XOR C5
		b += 4   #b3, b7, b11, b15, b19, b23 
	temp.reverse() #Return to normal form
	#------------------------------------------------------------
	return temp

#--------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------

#--------------------------------------Decrypt----------------------------------------------
def Decrypt(ciphertext, keys):
	plaintext = ciphertext

	# Rounds of the algorithm.
	for i in range(ROUNDS - 1, -1, -1):

		plaintext = add_round_key(plaintext, keys[i], i)
		
		plaintext = INV_permbits(plaintext)

		plaintext = INV_subcells(plaintext)

	return plaintext
#-------------------------------Subcells-----------------------------------
#1. Put the content into a box (SubCells)
def INV_subcells(subcell):
	#aux = BLOCK_SIZE/4
	aux = 16
	for i in range(aux):
		pos = 4 * i
		#------Convert bin to dec------- #############################3**************************************Modificar
		index = get_fragment_int(subcell, pos, pos + 4)
		#-------------------------------
		#--------------SBOX operation-------------------
		subcell[pos:pos+4] = int_to_bin(SBOX_INV[index], 4)   #Convert int to bin
		#-----------------------------------------------

	return subcell
#--------------------------------------------------------------------------

#-------------------------------PermBits-----------------------------------
#2. Wrap the ribbon around the box (PermBits)
def INV_permbits(ciphertext):
	permutation = [0] * BLOCK_SIZE
	offset = BLOCK_SIZE - 1
	#----------------Permutation-----------------
	for i in range(BLOCK_SIZE):
		permutation[offset - PBOX_INV[i]] = ciphertext[offset - i]
	#--------------------------------------------
	return permutation
#--------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
# Method to convert a number represented in binary in decimal
def get_fragment_int(array, begin, end):
	return int("".join(map(str, array[begin:end])), 2)

# Method to convert an integer to a string, representing the binary form of the integer
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

#-------------------------------------------------------------------------------------------



if __name__ == '__main__':
	k = [1]*128
	#k = [0]*128
	#k = [0,0,0,1]*32
	m =  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
	#m = [1,1,0,1,1,1,1,1,0,1,0,1,1,0,1,1,1,1,1,0,1,0,1,1,0,0,1,1,1,1,1,0,1,0,0,0,0,1,0,0,0,0,1,1,0,0,0,1,1,0,0,1,1,0,0,0,0,0,0,0,1,0,1,1]
	#m = [d,f,5,b,e,b,3,e,8,4,3,1,9,4,b,b]
	#m = [1,1,0,1,1,1,1,1,0,1,0,1,1,0,1,1,1,1,1,0,1,0,1,1,0,0,1,1,1,1,1,0,1,0,0,0,0,1,0,0,0,0,1,1,0,0,0,1,1,0,0,1,0,1,0,0,1,0,1,1,1,0,1,1]
	#m=1101111101011011111010110011111010000100001100011001010010111011
	key = KeySchedule(k)
	ciphertext = Encrypt(m, key)

#	print("plaintext = ",str(m).replace(",","").replace(" ","").replace("[","").replace("]",""))
#	print("ciphertext= ",str(ciphertext).replace(",","").replace(" ","").replace("[","").replace("]",""))
	
	plaintext = Decrypt(ciphertext, key)
#	print("plaintext = ",str(plaintext).replace(",","").replace(" ","").replace("[","").replace("]",""))
	#print("plaintext = ",pretty_print(list(str(m).replace(",","").replace(" ","").replace("[","").replace("]",""))))
	print("plaintext     = ",pretty_print(plaintext))
	print("key = ", pretty_printK(k))
	print("ciphertext    = ",pretty_print(ciphertext))
	print("Desciphertext = ",pretty_print(plaintext))
	
