from src.snapshot.Reader import Reader
from src.snapshot.Writer import Writer
from io import BytesIO

data = BytesIO()
source = {"key": "arnab", "nested": {"key": "values"}}
writer = Writer(source, data)
reader = Reader({}, data)
# print(writer.write_key_value(writer, {"key": "arnab", "nested": {"key": "values"}}))
print(writer.write())
data.seek(0)
print(data.read()[-1])
data.seek(0)
print(reader.read_length())
# # while True:
# #     result = handler.deserialise(reader)
# #     if not result:
# #         break
# #     print(result)
