# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: calculator.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10\x63\x61lculator.proto\x12\ncalculator\"6\n\x12\x43\x61lculationRequest\x12\x0f\n\x07number1\x18\x01 \x01(\x01\x12\x0f\n\x07number2\x18\x02 \x01(\x01\"%\n\x13\x43\x61lculationResponse\x12\x0e\n\x06result\x18\x01 \x01(\x01\x32\xb9\x02\n\nCalculator\x12\x46\n\x03\x41\x64\x64\x12\x1e.calculator.CalculationRequest\x1a\x1f.calculator.CalculationResponse\x12K\n\x08Subtract\x12\x1e.calculator.CalculationRequest\x1a\x1f.calculator.CalculationResponse\x12K\n\x08Multiply\x12\x1e.calculator.CalculationRequest\x1a\x1f.calculator.CalculationResponse\x12I\n\x06\x44ivide\x12\x1e.calculator.CalculationRequest\x1a\x1f.calculator.CalculationResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'calculator_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_CALCULATIONREQUEST']._serialized_start=32
  _globals['_CALCULATIONREQUEST']._serialized_end=86
  _globals['_CALCULATIONRESPONSE']._serialized_start=88
  _globals['_CALCULATIONRESPONSE']._serialized_end=125
  _globals['_CALCULATOR']._serialized_start=128
  _globals['_CALCULATOR']._serialized_end=441
# @@protoc_insertion_point(module_scope)
