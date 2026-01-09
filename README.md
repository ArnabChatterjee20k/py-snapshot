# About
An easy to use python dictionary snapshot generation and saving it.
Major part of  https://github.com/ArnabChatterjee20k/pycache

Extracting here for usage in other projects
Use cases -> Backups, saving inmemory states in compressed form

<!-- Format -->
[OBJECT_TYPE]
[KEY_LENGTH]
[KEY_DATA]
[Compressed Length/Original Length]
[ENCODING_MARKER] | if 3 then read the data for compressed length else the original length
[VALUE_ENCODING/DATA]

# Numbers are also written as string
so used the Encoder to write them to the bytes
mask = 3 << 6 => 3 means 11 => so getting a 8bit
encoding = mask | encoding => gives the value
so we will have something like 11000000, 11000001, 11000010
-> read MSB == 11 => integer encoding => read the LSB