import os
import sys
import math

file_header = {
    'MPG': '000001b3',
    'PDF': '25504446',
    'BMP': '424d',
    'GIF87a': '474946383761',
    'GIF89a': '474946383961',
    'JPG': 'ffd8ff',
    'DOCX': '504b030414000600',
    'AVI': '52494646',
    'PNG': '89504e470d0a1a0a',
    'ZIP': '504b0304'
}

file_footer = {
    'MPG1': '000001b7',
    'MPG2': '000001b9',
    'PDF1': '0a2525454f46',
    'PDF2': '0a2525454f460a',
    'PDF3': '0d0a2525454f460d0a',
    'PDF4': '0d2525454f460d',
    'GIF': '003b',
    'JPG': 'ffd9',
    'DOCX': '504b0506',
    'PNG': '49454e44ae426082',
    'ZIP': '504b0506'
}

def FileRecovery(disk_hex):
    # Number of files found
    total_found = 0

    # Look for all headers
    for header in file_header:

        # Initial search location
        search = 0

        # Signature location
        loc = disk_hex.find(file_header[header])

        while loc != -1:

            # MPG
            if header == 'MPG':
                # Handle MPG files (code not included here)
                pass

            # PDF
            elif header == 'PDF':
                # Handle PDF files (code not included here)
                pass

            # BMP
            elif header == 'BMP':
                if loc % 512 == 0:
                    total_found += 1

                    # Extract the file size from bytes 2-5 (offsets 4-12 in hex string)
                    size_hex = disk_hex[loc + 4: loc + 12]
                    # Reverse byte order (little-endian)
                    file_size = size_hex[6:8] + size_hex[4:6] + size_hex[2:4] + size_hex[0:2]
                    file_size = int(file_size, 16)

                    # Generate file name
                    file_name = f'File{total_found}.bmp'

                    # Extract file
                    start_offset = loc // 2
                    end_offset = start_offset + file_size

                    # Print information
                    print(f"{file_name}, Start Offset: {hex(start_offset)}, End Offset: {hex(end_offset)}")

                    File_Extract(start_offset, file_size, file_name)

                    search = loc + file_size * 2  # Move search index beyond current file
                else:
                    search = loc + 4

            # GIF87a and GIF89a
            elif header in ['GIF87a', 'GIF89a']:
                if loc % 512 == 0:
                    total_found += 1

                    # File footer location
                    footer = disk_hex.find(file_footer['GIF'], loc)

                    if footer != -1:
                        # Include footer in the file
                        footer += 4  # '003b' is 4 characters in hex

                        # Generate file name
                        file_name = f'File{total_found}.gif'

                        # Extract file
                        start_offset = loc // 2
                        end_offset = (footer + 1) // 2
                        filesize = end_offset - start_offset

                        # Print information
                        print(f"{file_name}, Start Offset: {hex(start_offset)}, End Offset: {hex(end_offset)}")

                        File_Extract(start_offset, filesize, file_name)

                        search = footer
                    else:
                        print(f"End of GIF file not found for {file_name}")
                        search = loc + 12
                else:
                    search = loc + 12

            # JPG
            elif header == 'JPG':
                if loc % 512 == 0:
                    total_found += 1

                    # File footer location
                    footer = disk_hex.find(file_footer['JPG'], loc)

                    if footer != -1:
                        # Include footer in the file
                        footer += 4  # 'ffd9' is 4 characters in hex

                        # Generate file name
                        file_name = f'File{total_found}.jpg'

                        # Extract file
                        start_offset = loc // 2
                        end_offset = (footer + 1) // 2
                        filesize = end_offset - start_offset

                        # Print information
                        print(f"{file_name}, Start Offset: {hex(start_offset)}, End Offset: {hex(end_offset)}")

                        File_Extract(start_offset, filesize, file_name)

                        search = footer
                    else:
                        print(f"End of JPG file not found for {file_name}")
                        search = loc + 6
                else:
                    search = loc + 6

            # AVI
            elif header == 'AVI':
                if loc % 512 == 0:
                    total_found += 1

                    # Extract the file size from bytes 4-7 after 'RIFF' (offsets 8-16 in hex string)
                    size_hex = disk_hex[loc + 8: loc + 16]
                    # Reverse byte order (little-endian)
                    file_size = size_hex[6:8] + size_hex[4:6] + size_hex[2:4] + size_hex[0:2]
                    file_size = int(file_size, 16) + 8  # Include 'RIFF' and size fields

                    # Generate file name
                    file_name = f'File{total_found}.avi'

                    # Extract file
                    start_offset = loc // 2
                    end_offset = start_offset + file_size

                    # Print information
                    print(f"{file_name}, Start Offset: {hex(start_offset)}, End Offset: {hex(end_offset)}")

                    File_Extract(start_offset, file_size, file_name)

                    search = loc + file_size * 2
                else:
                    search = loc + 8

            # PNG
            elif header == 'PNG':
                # Handle PNG files (code not included here)
                pass

            # ZIP
            elif header == 'ZIP':
                if loc % 512 == 0:
                    total_found += 1

                    # Find the end of central directory record
                    footer = disk_hex.find(file_footer['ZIP'], loc)

                    if footer != -1:
                        # The End of Central Directory Record is at least 22 bytes (44 hex characters)
                        footer_end = footer + 44

                        # Generate file name
                        file_name = f'File{total_found}.zip'

                        # Extract file
                        start_offset = loc // 2
                        end_offset = (footer_end + 1) // 2
                        filesize = end_offset - start_offset

                        # Print information
                        print(f"{file_name}, Start Offset: {hex(start_offset)}, End Offset: {hex(end_offset)}")

                        File_Extract(start_offset, filesize, file_name)

                        search = footer_end
                    else:
                        print(f"End of ZIP file not found for {file_name}")
                        search = loc + 8
                else:
                    search = loc + 8

            else:
                # Other file types (code not included here)
                pass

            # Find next occurrence of header
            loc = disk_hex.find(file_header[header], search)

def File_Extract(start_offset, count, file_name):
    extraction_command = f'dd if="{sys.argv[1]}" of="{file_name}" bs=1 skip={start_offset} count={count} status=none'
    os.system(extraction_command)
    generateHash(file_name)

def generateHash(inputFile):
    hash_command = f'shasum -a 256 "{inputFile}"'
    os.system(hash_command)

if __name__ == "__main__":
    with open(sys.argv[1], 'rb') as disk_image:
        disk_data = disk_image.read()
    disk_hex = disk_data.hex()

    FileRecovery(disk_hex)
