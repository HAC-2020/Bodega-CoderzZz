# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: temp/proto_order/temp1.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='temp/proto_order/temp1.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x1ctemp/proto_order/temp1.proto\"\x16\n\x07Message\x12\x0b\n\x03msg\x18\x01 \x01(\t2:\n\x13MessageTransmission\x12#\n\x0bsendMessage\x12\x08.Message\x1a\x08.Message\"\x00\x62\x06proto3')
)




_MESSAGE = _descriptor.Descriptor(
  name='Message',
  full_name='Message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='msg', full_name='Message.msg', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=32,
  serialized_end=54,
)

DESCRIPTOR.message_types_by_name['Message'] = _MESSAGE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Message = _reflection.GeneratedProtocolMessageType('Message', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGE,
  __module__ = 'temp.proto_order.temp1_pb2'
  # @@protoc_insertion_point(class_scope:Message)
  ))
_sym_db.RegisterMessage(Message)



_MESSAGETRANSMISSION = _descriptor.ServiceDescriptor(
  name='MessageTransmission',
  full_name='MessageTransmission',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=56,
  serialized_end=114,
  methods=[
  _descriptor.MethodDescriptor(
    name='sendMessage',
    full_name='MessageTransmission.sendMessage',
    index=0,
    containing_service=None,
    input_type=_MESSAGE,
    output_type=_MESSAGE,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_MESSAGETRANSMISSION)

DESCRIPTOR.services_by_name['MessageTransmission'] = _MESSAGETRANSMISSION

# @@protoc_insertion_point(module_scope)
