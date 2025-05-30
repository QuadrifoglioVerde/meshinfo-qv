# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: meshtastic_custom/admin.proto
# Protobuf Python Version: 6.31.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    31,
    0,
    '',
    'meshtastic_custom/admin.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from meshtastic_custom import channel_pb2 as meshtastic__custom_dot_channel__pb2
from meshtastic_custom import config_pb2 as meshtastic__custom_dot_config__pb2
from meshtastic_custom import connection_status_pb2 as meshtastic__custom_dot_connection__status__pb2
from meshtastic_custom import mesh_pb2 as meshtastic__custom_dot_mesh__pb2
from meshtastic_custom import module_config_pb2 as meshtastic__custom_dot_module__config__pb2
from meshtastic_custom import device_ui_pb2 as meshtastic__custom_dot_device__ui__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1dmeshtastic_custom/admin.proto\x12\nmeshtastic\x1a\x1fmeshtastic_custom/channel.proto\x1a\x1emeshtastic_custom/config.proto\x1a)meshtastic_custom/connection_status.proto\x1a\x1cmeshtastic_custom/mesh.proto\x1a%meshtastic_custom/module_config.proto\x1a!meshtastic_custom/device_ui.proto\"\x82\x17\n\x0c\x41\x64minMessage\x12\x17\n\x0fsession_passkey\x18\x65 \x01(\x0c\x12\x1d\n\x13get_channel_request\x18\x01 \x01(\rH\x00\x12\x33\n\x14get_channel_response\x18\x02 \x01(\x0b\x32\x13.meshtastic.ChannelH\x00\x12\x1b\n\x11get_owner_request\x18\x03 \x01(\x08H\x00\x12.\n\x12get_owner_response\x18\x04 \x01(\x0b\x32\x10.meshtastic.UserH\x00\x12\x41\n\x12get_config_request\x18\x05 \x01(\x0e\x32#.meshtastic.AdminMessage.ConfigTypeH\x00\x12\x31\n\x13get_config_response\x18\x06 \x01(\x0b\x32\x12.meshtastic.ConfigH\x00\x12N\n\x19get_module_config_request\x18\x07 \x01(\x0e\x32).meshtastic.AdminMessage.ModuleConfigTypeH\x00\x12>\n\x1aget_module_config_response\x18\x08 \x01(\x0b\x32\x18.meshtastic.ModuleConfigH\x00\x12\x34\n*get_canned_message_module_messages_request\x18\n \x01(\x08H\x00\x12\x35\n+get_canned_message_module_messages_response\x18\x0b \x01(\tH\x00\x12%\n\x1bget_device_metadata_request\x18\x0c \x01(\x08H\x00\x12\x42\n\x1cget_device_metadata_response\x18\r \x01(\x0b\x32\x1a.meshtastic.DeviceMetadataH\x00\x12\x1e\n\x14get_ringtone_request\x18\x0e \x01(\x08H\x00\x12\x1f\n\x15get_ringtone_response\x18\x0f \x01(\tH\x00\x12.\n$get_device_connection_status_request\x18\x10 \x01(\x08H\x00\x12S\n%get_device_connection_status_response\x18\x11 \x01(\x0b\x32\".meshtastic.DeviceConnectionStatusH\x00\x12\x31\n\x0cset_ham_mode\x18\x12 \x01(\x0b\x32\x19.meshtastic.HamParametersH\x00\x12/\n%get_node_remote_hardware_pins_request\x18\x13 \x01(\x08H\x00\x12\\\n&get_node_remote_hardware_pins_response\x18\x14 \x01(\x0b\x32*.meshtastic.NodeRemoteHardwarePinsResponseH\x00\x12 \n\x16\x65nter_dfu_mode_request\x18\x15 \x01(\x08H\x00\x12\x1d\n\x13\x64\x65lete_file_request\x18\x16 \x01(\tH\x00\x12\x13\n\tset_scale\x18\x17 \x01(\rH\x00\x12\x45\n\x12\x62\x61\x63kup_preferences\x18\x18 \x01(\x0e\x32\'.meshtastic.AdminMessage.BackupLocationH\x00\x12\x46\n\x13restore_preferences\x18\x19 \x01(\x0e\x32\'.meshtastic.AdminMessage.BackupLocationH\x00\x12L\n\x19remove_backup_preferences\x18\x1a \x01(\x0e\x32\'.meshtastic.AdminMessage.BackupLocationH\x00\x12%\n\tset_owner\x18  \x01(\x0b\x32\x10.meshtastic.UserH\x00\x12*\n\x0bset_channel\x18! \x01(\x0b\x32\x13.meshtastic.ChannelH\x00\x12(\n\nset_config\x18\" \x01(\x0b\x32\x12.meshtastic.ConfigH\x00\x12\x35\n\x11set_module_config\x18# \x01(\x0b\x32\x18.meshtastic.ModuleConfigH\x00\x12,\n\"set_canned_message_module_messages\x18$ \x01(\tH\x00\x12\x1e\n\x14set_ringtone_message\x18% \x01(\tH\x00\x12\x1b\n\x11remove_by_nodenum\x18& \x01(\rH\x00\x12\x1b\n\x11set_favorite_node\x18\' \x01(\rH\x00\x12\x1e\n\x14remove_favorite_node\x18( \x01(\rH\x00\x12\x32\n\x12set_fixed_position\x18) \x01(\x0b\x32\x14.meshtastic.PositionH\x00\x12\x1f\n\x15remove_fixed_position\x18* \x01(\x08H\x00\x12\x17\n\rset_time_only\x18+ \x01(\x07H\x00\x12\x1f\n\x15get_ui_config_request\x18, \x01(\x08H\x00\x12<\n\x16get_ui_config_response\x18- \x01(\x0b\x32\x1a.meshtastic.DeviceUIConfigH\x00\x12\x35\n\x0fstore_ui_config\x18. \x01(\x0b\x32\x1a.meshtastic.DeviceUIConfigH\x00\x12\x1a\n\x10set_ignored_node\x18/ \x01(\rH\x00\x12\x1d\n\x13remove_ignored_node\x18\x30 \x01(\rH\x00\x12\x1d\n\x13\x62\x65gin_edit_settings\x18@ \x01(\x08H\x00\x12\x1e\n\x14\x63ommit_edit_settings\x18\x41 \x01(\x08H\x00\x12\x30\n\x0b\x61\x64\x64_contact\x18\x42 \x01(\x0b\x32\x19.meshtastic.SharedContactH\x00\x12\x1e\n\x14\x66\x61\x63tory_reset_device\x18^ \x01(\x05H\x00\x12\x1c\n\x12reboot_ota_seconds\x18_ \x01(\x05H\x00\x12\x18\n\x0e\x65xit_simulator\x18` \x01(\x08H\x00\x12\x18\n\x0ereboot_seconds\x18\x61 \x01(\x05H\x00\x12\x1a\n\x10shutdown_seconds\x18\x62 \x01(\x05H\x00\x12\x1e\n\x14\x66\x61\x63tory_reset_config\x18\x63 \x01(\x05H\x00\x12\x16\n\x0cnodedb_reset\x18\x64 \x01(\x05H\x00\"\xd6\x01\n\nConfigType\x12\x11\n\rDEVICE_CONFIG\x10\x00\x12\x13\n\x0fPOSITION_CONFIG\x10\x01\x12\x10\n\x0cPOWER_CONFIG\x10\x02\x12\x12\n\x0eNETWORK_CONFIG\x10\x03\x12\x12\n\x0e\x44ISPLAY_CONFIG\x10\x04\x12\x0f\n\x0bLORA_CONFIG\x10\x05\x12\x14\n\x10\x42LUETOOTH_CONFIG\x10\x06\x12\x13\n\x0fSECURITY_CONFIG\x10\x07\x12\x15\n\x11SESSIONKEY_CONFIG\x10\x08\x12\x13\n\x0f\x44\x45VICEUI_CONFIG\x10\t\"\xbb\x02\n\x10ModuleConfigType\x12\x0f\n\x0bMQTT_CONFIG\x10\x00\x12\x11\n\rSERIAL_CONFIG\x10\x01\x12\x13\n\x0f\x45XTNOTIF_CONFIG\x10\x02\x12\x17\n\x13STOREFORWARD_CONFIG\x10\x03\x12\x14\n\x10RANGETEST_CONFIG\x10\x04\x12\x14\n\x10TELEMETRY_CONFIG\x10\x05\x12\x14\n\x10\x43\x41NNEDMSG_CONFIG\x10\x06\x12\x10\n\x0c\x41UDIO_CONFIG\x10\x07\x12\x19\n\x15REMOTEHARDWARE_CONFIG\x10\x08\x12\x17\n\x13NEIGHBORINFO_CONFIG\x10\t\x12\x1a\n\x16\x41MBIENTLIGHTING_CONFIG\x10\n\x12\x1a\n\x16\x44\x45TECTIONSENSOR_CONFIG\x10\x0b\x12\x15\n\x11PAXCOUNTER_CONFIG\x10\x0c\"#\n\x0e\x42\x61\x63kupLocation\x12\t\n\x05\x46LASH\x10\x00\x12\x06\n\x02SD\x10\x01\x42\x11\n\x0fpayload_variant\"[\n\rHamParameters\x12\x11\n\tcall_sign\x18\x01 \x01(\t\x12\x10\n\x08tx_power\x18\x02 \x01(\x05\x12\x11\n\tfrequency\x18\x03 \x01(\x02\x12\x12\n\nshort_name\x18\x04 \x01(\t\"f\n\x1eNodeRemoteHardwarePinsResponse\x12\x44\n\x19node_remote_hardware_pins\x18\x01 \x03(\x0b\x32!.meshtastic.NodeRemoteHardwarePin\"A\n\rSharedContact\x12\x10\n\x08node_num\x18\x01 \x01(\r\x12\x1e\n\x04user\x18\x02 \x01(\x0b\x32\x10.meshtastic.UserB`\n\x13\x63om.geeksville.meshB\x0b\x41\x64minProtosZ\"github.com/meshtastic/go/generated\xaa\x02\x14Meshtastic.Protobufs\xba\x02\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'meshtastic_custom.admin_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\023com.geeksville.meshB\013AdminProtosZ\"github.com/meshtastic/go/generated\252\002\024Meshtastic.Protobufs\272\002\000'
  _globals['_ADMINMESSAGE']._serialized_start=258
  _globals['_ADMINMESSAGE']._serialized_end=3204
  _globals['_ADMINMESSAGE_CONFIGTYPE']._serialized_start=2616
  _globals['_ADMINMESSAGE_CONFIGTYPE']._serialized_end=2830
  _globals['_ADMINMESSAGE_MODULECONFIGTYPE']._serialized_start=2833
  _globals['_ADMINMESSAGE_MODULECONFIGTYPE']._serialized_end=3148
  _globals['_ADMINMESSAGE_BACKUPLOCATION']._serialized_start=3150
  _globals['_ADMINMESSAGE_BACKUPLOCATION']._serialized_end=3185
  _globals['_HAMPARAMETERS']._serialized_start=3206
  _globals['_HAMPARAMETERS']._serialized_end=3297
  _globals['_NODEREMOTEHARDWAREPINSRESPONSE']._serialized_start=3299
  _globals['_NODEREMOTEHARDWAREPINSRESPONSE']._serialized_end=3401
  _globals['_SHAREDCONTACT']._serialized_start=3403
  _globals['_SHAREDCONTACT']._serialized_end=3468
# @@protoc_insertion_point(module_scope)
