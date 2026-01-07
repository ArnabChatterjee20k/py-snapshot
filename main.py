from src.snapshot.Reader import Reader
from src.snapshot.Writer import Writer
from src.snapshot.handlers.IntHandler import IntHandler
from io import BytesIO

data = BytesIO()
writer = Writer({}, data)
reader = Reader({}, data)
writer.buffer.write(b"12")
data.seek(0)
handler = IntHandler()
print(handler.serialise(writer, "ljsdfls;f"))
data.seek(0)
print(handler.deserialise(reader))
