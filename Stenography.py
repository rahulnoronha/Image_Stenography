#!/usr/bin/python
# -*- coding: utf-8 -*-
# import all the required libraries
'''
Author: Rahul Noronha
Date:
23/09/2020
->Encoding function worked for png only, RGB_To_Grayscale and JPEG_To_PNG throwing IOError
24/09/2020
->Encoding function worked for png and jpg only RGB_To_Grayscale worked succesfully, 
->JPEG_To_PNG works only for JPG and fails for JPEG
'''
import cv2
import numpy as np
import types
from Convert_Image import *    # User defined module to Convert JP(E)G to PNG and RGB to Grayscale
# Has two functions RGB_To_Grayscale and JPEG_To_PNG which take parameters input file name and output file name

DELIMETER = '#####'

def to_binary(message):
	'''
	Function to convert the message to be encoded to Binary
	'''

	if type(message) == str:
		return ''.join([format(ord(i), '08b') for i in message])
	elif type(message) == bytes or type(message) == np.ndarray:
		return [format(i, '08b') for i in message]
	elif type(message) == int or type(message) == np.uint8:
		return format(message, '08b')
	else:
		raise TypeError('Input type not supported')


def hide_data(image, secret_message):
	'''
	Function to Hide the binary data into the Image
	Hidden one bit in LSB of red, green and blue pixel
	LSB technique causes minor change in the pixel values
	TODO: Consider encrypting the hidden message before encoding and decrypting the decoded message later to provide additional security
	'''

	# calculate the maximum bytes that can be encoded

	n_bytes = image.shape[0] * image.shape[1] * 3 // 8
	print('Maximum bytes to encode:', n_bytes)

	# Check if the number of bytes to encode is less than the maximum bytes in the image

	if len(secret_message) > n_bytes:
		raise ValueError('Error: Insufficient bytes. Need bigger image or less data')

	secret_message += DELIMETER    # you can use any string as the delimeter

	data_index = 0

	# convert input data to binary format using to_binary() fucntion

	binary_secret_msg = to_binary(secret_message)

	data_len = len(binary_secret_msg)    # Find the length of data that needs to be hidden
	for values in image:
		for pixel in values:

			# convert RGB values to binary format

			(r, g, b) = to_binary(pixel)

			# modify the least significant bit only if there is still data to store

			if data_index < data_len:

				# hide the data into least significant bit of red pixel

				pixel[0] = int(r[:-1] + binary_secret_msg[data_index], 
							   2)
				data_index += 1
			if data_index < data_len:

				# hide the data into least significant bit of green pixel

				pixel[1] = int(g[:-1] + binary_secret_msg[data_index], 
							   2)
				data_index += 1
			if data_index < data_len:

				# hide the data into least significant bit of  blue pixel

				pixel[2] = int(b[:-1] + binary_secret_msg[data_index], 
							   2)
				data_index += 1

			# if data is encoded, just break out of the loop

			if data_index >= data_len:
				break

	return image


def show_data(image):
	'''
   This function is used to decode the message from the png image file by checking for our preset delimiter DELIMETER which can be changed to anything we want
   
  '''

	binary_data = ''
	for values in image:
		for pixel in values:
			(r, g, b) = to_binary(pixel)    # convert the red, green and blue values into binary format
			binary_data += r[-1]    # extracting data from the least significant bit of red pixel
			binary_data += g[-1]    # extracting data from the least significant bit of red pixel
			binary_data += b[-1]    # extracting data from the least significant bit of red pixel

	# split by 8-bits

	all_bytes = [binary_data[i:i + 8] for i in range(0, 
				 len(binary_data), 8)]

	# convert from bits to characters

	decoded_data = ''
	for byte in all_bytes:
		decoded_data += chr(int(byte, 2))
		if decoded_data[-5:] == DELIMETER:    # check if we have reached the delimeter which is "#####"
			break

	# print(decoded_data)

	return decoded_data[:-5]    # remove the delimeter to show the original hidden message


# Encode data into image

def encode_text(): # split into more functions
	'''
	This function is used to read the message to be encoded and the image file to hide the message in and then decode the message into the image using hide_data.
	TODO: Fails for jpeg images, so fix this.
	'''

	image_name = input('Enter image path: ')
	old_name = image_name

	# # TODO rpartition on dot seems like a better way
	# if image_name[-3:] == 'peg':
	# 	image_name = image_name[:-5] + 'Renamed' + '.png'
	# 	print(old_name, ' ', image_name, '\n')
	# 	JPEG_To_PNG(old_name, image_name)

	# elif image_name[-3:] == 'jpg':
	# 	image_name = image_name[:-4] + 'Renamed' + '.png'
	# 	print(old_name, ' ', image_name, '\n')
	# 	JPEG_To_PNG(old_name, image_name)

	grayscale_or_color = int(input("Grayscale (1) or Colour (2): "))
	
	if grayscale_or_color == 1:
		new_name = image_name[:-4] + 'ProperGrayed' + '.png'
		RGB_To_Grayscale(image_name, new_name)
		image_name = new_name
	
	image = cv2.imread(image_name) # Read the input image using OpenCV-Python.

	# details of the image

	print('The shape of the image is', image.shape)    # check the shape of image to calculate size in bytes
	resized_image = cv2.resize(image, (500, 500))    # resize the image as per your requirement
	cv2.imshow('Resized Input Image', resized_image)    # display the image
	cv2.waitKey(0)
	cv2.destroyAllWindows()

	data = input('Enter data to be encoded : ')
	if len(data) == 0:
		raise ValueError('Data is empty')

	filename = input('Enter path for output image: ')
	encoded_image = hide_data(image, data)    
	cv2.imwrite(filename, encoded_image)


def decode_text():
	# Decode the data in the image
	# read the image that contains the hidden image

	image_name = input("Enter path of image to decode: ")
	image = cv2.imread(image_name)    # read the image using cv2.imread()

	resized_image = cv2.resize(image, (500, 500))    # resize the original image as per your requirement
	cv2.imshow('Resized Image with Hidden text', resized_image)    # display the Steganographed image
	cv2.waitKey(0)
	cv2.destroyAllWindows()

	text = show_data(image)
	return text

def menu():
	choice = input("Encode(1) or Decode(2): ")
	choice = int(choice)
	if choice == 1:
		print('Encoding...')
		encode_text()
	elif choice == 2:
		print('Decoding...')
		print('Decoded message is ' + decode_text())
	else:
		raise Exception('Invalid input.')


for i in range(2):    # First run for encoding and second run for decoding.
	menu()