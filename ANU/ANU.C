/*
  File name: ANU.c
  Author: Joel López
  Project: Implementacion of ANU in C
*/
#include <stdio.h>
#include <stdlib.h>
#include <string>

//---------------------------------------------------------------------------------------
#define BLOCK_SIZE = 64
#define KEY_SIZE = 128
#define ROUNDS = 25

int SBOX[15] = {2, 9, 7, 14, 1, 12, 10, 0, 4, 3, 8, 13, 15, 6, 5, 11};
int PBOX[63] = {20, 16, 28, 24, 17, 21, 25, 29,
				22, 18, 30, 26, 19, 23, 27, 31,
				11, 15,  3,  7, 14, 10,  6,  2,
		 		 9, 13,  1,  5, 12,  8,  4,  0};
//---------------------------------------------------------------------------------------

//-------------------------------------------key schedule-----------------------------------------------
//-----------------------------------------------------
int ** key_schedule_128(int* key){
	int sub_keys[ROUNDS];

	for (int i = 0; i < ROUNDS; ++i){
    //-------First step, add the round_key---------
		sub_keys[i] = get_chunk(key, 32, 0); //Obtain 32 bits for Ki
	//---------------------------------------------
    //--------------key update---------------------
		key = key_update(key, i);
	//---------------------------------------------
	}
	return sub_keys
}
//----------------------------------------------------

//-------------------------------------Key Update---------------------------------------------
int* key_update(int* key, int count){

	//----------------------Step 1. Left rotation by 13 bits-----------------------------
									//KEY <<<13
	int new_key[KEY_SIZE] = key << 13;
	//-----------------------------------------------------------------------------------

	//---------------------------Step 2. S-box operation---------------------------------
							//[K3,K2,K1,K0] ¬ S[K3,K2,K1,K0]
	int sbox_index[4]; 
	sbox_index = get_chunk(new_key, 124, 128);
	sbox_index = chunk_to_int(sbox_index, 4);
	new_key = set_values(int_to_bin_array(SBOX[sbox_index], 4), new_key, 124, 128); 
	//-----------------------------------------------------------------------------------

	//---------------------------Step 3. S-box operation---------------------------------
							//[K7,K6,K5,K4] ← S[K7,K6,K5,K4]
	sbox_index = get_chunk(new_key, 120, 124);
	sbox_index = chunk_to_int(sbox_index, 4);
	new_key = set_values(int_to_bin_array(SBOX[sbox_index], 4), new_key, 120, 124);
	//-----------------------------------------------------------------------------------

	//-----------------------Step 4. X-OR with round_counter-----------------------------
				//[K63,K62,K61,K60,K59] ¬ [K63,K62,K61,K60,K59] ÅRCi
	chunk = get_chunk(new_key, 64, 69);
	chunk = chunk_to_int(chunk, 4);
	new_key = set_values(int_to_bin_array(chunk ^ (count % 32), 5), new_key, 64, 69);
	//-----------------------------------------------------------------------------------

	return new_key;
}
//--------------------------------------------------------------------------------------------
//------------------------------------------------------------------------------------------------------

//------------------------------------------------------------------------------------------------------
int* cipher(int* plaintext, int* keys){
	int p_left[]  = get_chunk(plaintext, 32, 0);
	int p_rigth[] = get_chunk(plaintext, 64, 32);
	int p_aux[31];
	int* f1 = p_left;
	int* f2 = p_left;

	for (int i = 0; i < ROUNDS; i++){
	  //----------1. Apply F function-----------
		//--------F Function----------
			f1 = f1 << 3;
			f2 = f2 >> 8;
			f1 = sbox_operation(f1);
			f2 = sbox_operation(f2);
		//----------------------------

	  //---2. XOR with p_r, F1 apply Key RKi----
	  	p_aux = xor(f1, p_rigth, 32);
		p_aux = xor(p_aux, xor(f2, keys[i], 32), 32);

	  	//----------P Layer-----------
		p_rigth = pbox_layer(p_left);
		p_left  = pbox_layer(p_rigth);
		//----------------------------
	}
	printf("%d", p_left);
	printf("%d", p_rigth);
//	return p_left p_rigth;
}

//------------------------------------------------------------------------------
int* sbox_operation(int* f){
	for (int i = 1; i <= 8; ++i){
		int* sbox_index = get_chunk(f, i*4-4, i*4);
		sbox_index = chunk_to_int(sbox_index, 4);
		f = set_values(int_to_bin_array(SBOX[sbox_index], 4), f, i*4-4, i*4);
	}
	return f;
}

int* pbox_layer(int* state){
	int* new_state = malloc(sizeof(int) * BLOCK_SIZE);
	int i;
	for (i = 0; i < BLOCK_SIZE; i++) {
    	new_state[PBOX[i]] = state[i];
	}
  return new_state;
}
//------------------------------------------------------------------------------


//------------------------------------------------------------------------------------------------------

//--------------------Auxiliar Functions-------------------------
int* int_to_bin_array(int int_num, int size) {
	int* bin_array = malloc(sizeof(int) * size);
	int div = int_num;
	int i = size - 1;

	while (div != 0) {
    	bin_array[i] = div % 2;
    	div /= 2;
    	i--;
	}
  return bin_array;
}

int* xor(int* a, int* b, int size) {
	for (int i = 0; i < size; i++) {    
    	a[i] = a[i] != b[i];
  	}
  return a;
}

int* get_chunk(int* array, int begin, int final) {  
	int size = final - begin;
	int* chunk = malloc(sizeof(int) * size);

	for (int i = begin, j = 0; i < final; i++, j++) {
		chunk[j] = array[i];    
  	}  
  return chunk;
}

int chunk_to_int(int* array, int size) {
	int value = 0;  
  
	for (int i = 0; i < size; i++) {    
    	value += array[i] << (3 - i);    
	}
  return value;
}

int* set_values(int* values, int* array, int begin, int end){
	for (int i = begin, j=0; i < end; i++, j++){
		array[i] = values[j];
	}
	return array;
}
//----------------------------------------------------------------


int main(int argc, char const *argv[])
{
	int key[KEY_SIZE];
	int plaintext[BLOCK_SIZE];
	int i; int** sub_keys;
	int 
	for (i = 0; i < KEY_SIZE; i++){
		key[i] = 0;
	}
	for (i = 0; i < BLOCK_SIZE; i++){
		plaintext[i] = 0;
	}

	sub_keys = key_schedule_128(key);


}