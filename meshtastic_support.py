#!/usr/bin/env python3

from enum import Enum

"""
HardwareModel definition of Meshtastic supported hardware models
from https://buf.build/meshtastic/protobufs/docs/main:meshtastic#meshtastic.HardwareModel
"""

class HardwareModel(Enum):
    UNSET = 0
    TLORA_V2 = 1
    TLORA_V1 = 2
    TLORA_V2_1_1P6 = 3
    TBEAM = 4
    HELTEC_V2_0 = 5
    TBEAM_V0P7 = 6
    T_ECHO = 7
    TLORA_V1_1P3 = 8
    RAK4631 = 9
    HELTEC_V2_1 = 10
    HELTEC_V1 = 11
    LILYGO_TBEAM_S3_CORE = 12
    RAK11200 = 13
    NANO_G1 = 14
    TLORA_V2_1_1P8 = 15
    TLORA_T3_S3 = 16
    NANO_G1_EXPLORER = 17
    NANO_G2_ULTRA = 18
    LORA_TYPE = 19
    WIPHONE = 20
    WIO_WM1110 = 21
    RAK2560 = 22
    HELTEC_HRU_3601 = 23
    HELTEC_WIRELESS_BRIDGE = 24
    STATION_G1 = 25
    RAK11310 = 26
    SENSELORA_RP2040 = 27
    SENSELORA_S3 = 28
    CANARYONE = 29
    RP2040_LORA = 30
    STATION_G2 = 31
    LORA_RELAY_V1 = 32
    NRF52840DK = 33
    PPR = 34
    GENIEBLOCKS = 35
    NRF52_UNKNOWN = 36
    PORTDUINO = 37
    ANDROID_SIM = 38
    DIY_V1 = 39
    NRF52840_PCA10059 = 40
    DR_DEV = 41
    M5STACK = 42
    HELTEC_V3 = 43
    HELTEC_WSL_V3 = 44
    BETAFPV_2400_TX = 45
    BETAFPV_900_NANO_TX = 46
    RPI_PICO = 47
    HELTEC_WIRELESS_TRACKER = 48
    HELTEC_WIRELESS_PAPER = 49
    T_DECK = 50
    T_WATCH_S3 = 51
    PICOMPUTER_S3 = 52
    HELTEC_HT62 = 53
    EBYTE_ESP32_S3 = 54
    ESP32_S3_PICO = 55
    CHATTER_2 = 56
    HELTEC_WIRELESS_PAPER_V1_0 = 57
    HELTEC_WIRELESS_TRACKER_V1_0 = 58
    UNPHONE = 59
    TD_LORAC = 60
    CDEBYTE_EORA_S3 = 61
    TWC_MESH_V4 = 62
    NRF52_PROMICRO_DIY = 63
    RADIOMASTER_900_BANDIT_NANO = 64
    HELTEC_CAPSULE_SENSOR_V3 = 65
    HELTEC_VISION_MASTER_T190 = 66
    HELTEC_VISION_MASTER_E213 = 67
    HELTEC_VISION_MASTER_E290 = 68
    HELTEC_MESH_NODE_T114 = 69
    SENSECAP_INDICATOR = 70
    TRACKER_T1000_E = 71
    RAK3172 = 72
    WIO_E5 = 73
    RADIOMASTER_900_BANDIT = 74
    ME25LS01_4Y10TD = 75
    RP2040_FEATHER_RFM95 = 76
    M5STACK_COREBASIC = 77
    M5STACK_CORE2 = 78
    RPI_PICO2 = 79
    M5STACK_CORES3 = 80
    SEEED_XIAO_S3 = 81
    MS24SF1 = 82
    TLORA_C6 = 83
    WISMESH_TAP = 84
    ROUTASTIC = 85
    MESH_TAB = 86
    MESHLINK = 87
    XIAO_NRF52_KIT = 88
    THINKNODE_M1 = 89
    THINKNODE_M2 = 90
    T_ETH_ELITE = 91
    HELTEC_SENSOR_HUB = 92
    RESERVED_FRIED_CHICKEN = 93
    HELTEC_MESH_POCKET = 94
    SEEED_SOLAR_NODE = 95
    NOMADSTAR_METEOR_PRO = 96
    CROWPANEL = 97
    PRIVATE_HW = 255

HARDWARE_PHOTOS = {
    HardwareModel.UNSET: "UNSET.png",
    HardwareModel.TLORA_V2: "TLORA_V2.png",
    HardwareModel.TLORA_V1: "TLORA_V1.png",
    HardwareModel.TLORA_V2_1_1P6: "TLORA_V2_1_1P6.png",
    HardwareModel.TBEAM: "TBEAM.png",
    HardwareModel.HELTEC_V2_0: "HELTEC_V2_0.png",
    HardwareModel.TBEAM_V0P7: "TBEAM_V0P7.png",
    HardwareModel.T_ECHO: "T_ECHO.png",
    HardwareModel.TLORA_V1_1P3: "TLORA_V1_1P3.png",
    HardwareModel.RAK4631: "RAK4631.png",
    HardwareModel.HELTEC_V2_1: "HELTEC_V2_1.png",
    HardwareModel.HELTEC_V1: "HELTEC_V1.png",
    HardwareModel.LILYGO_TBEAM_S3_CORE: "LILYGO_TBEAM_S3_CORE.png",
    HardwareModel.RAK11200: "RAK11200.png",
    HardwareModel.NANO_G1: "NANO_G1.png",
    HardwareModel.TLORA_V2_1_1P8: "TLORA_V2_1_1P8.png",
    HardwareModel.TLORA_T3_S3: "TLORA_T3_S3.png",
    HardwareModel.NANO_G1_EXPLORER: "NANO_G1_EXPLORER.png",
    HardwareModel.NANO_G2_ULTRA: "NANO_G2_ULTRA.png",
    HardwareModel.LORA_TYPE: "LORA_TYPE.png",
    HardwareModel.WIPHONE: "WIPHONE.png",
    HardwareModel.WIO_WM1110: "WIO_WM1110.png",
    HardwareModel.RAK2560: "RAK2560.png",
    HardwareModel.HELTEC_HRU_3601: "HELTEC_HRU_3601.png",
    HardwareModel.HELTEC_WIRELESS_BRIDGE: "HELTEC_WIRELESS_BRIDGE.png",
    HardwareModel.STATION_G1: "STATION_G1.png",
    HardwareModel.RAK11310: "RAK11310.png",
    HardwareModel.SENSELORA_RP2040: "SENSELORA_RP2040.png",
    HardwareModel.SENSELORA_S3: "SENSELORA_S3.png",
    HardwareModel.CANARYONE: "CANARYONE.png",
    HardwareModel.RP2040_LORA: "RP2040_LORA.png",
    HardwareModel.STATION_G2: "STATION_G2.png",
    HardwareModel.LORA_RELAY_V1: "LORA_RELAY_V1.png",
    HardwareModel.NRF52840DK: "NRF52840DK.png",
    HardwareModel.PPR: "PPR.png",
    HardwareModel.GENIEBLOCKS: "GENIEBLOCKS.png",
    HardwareModel.NRF52_UNKNOWN: "NRF52_UNKNOWN.png",
    HardwareModel.PORTDUINO: "PORTDUINO.png",
    HardwareModel.ANDROID_SIM: "ANDROID_SIM.png",
    HardwareModel.DIY_V1: "DIY_V1.png",
    HardwareModel.NRF52840_PCA10059: "NRF52840_PCA10059.png",
    HardwareModel.DR_DEV: "DR_DEV.png",
    HardwareModel.M5STACK: "M5STACK.png",
    HardwareModel.HELTEC_V3: "HELTEC_V3.png",
    HardwareModel.HELTEC_WSL_V3: "HELTEC_WSL_V3.png",
    HardwareModel.BETAFPV_2400_TX: "BETAFPV_2400_TX.png",
    HardwareModel.BETAFPV_900_NANO_TX: "BETAFPV_900_NANO_TX.png",
    HardwareModel.RPI_PICO: "RPI_PICO.png",
    HardwareModel.HELTEC_WIRELESS_TRACKER: "HELTEC_WIRELESS_TRACKER.png",
    HardwareModel.HELTEC_WIRELESS_PAPER: "HELTEC_WIRELESS_PAPER.png",
    HardwareModel.T_DECK: "T_DECK.png",
    HardwareModel.T_WATCH_S3: "T_WATCH_S3.png",
    HardwareModel.PICOMPUTER_S3: "PICOMPUTER_S3.png",
    HardwareModel.HELTEC_HT62: "HELTEC_HT62.png",
    HardwareModel.EBYTE_ESP32_S3: "EBYTE_ESP32_S3.png",
    HardwareModel.ESP32_S3_PICO: "ESP32_S3_PICO.png",
    HardwareModel.CHATTER_2: "CHATTER_2.png",
    HardwareModel.HELTEC_WIRELESS_PAPER_V1_0: "HELTEC_WIRELESS_PAPER_V1_0.png",
    HardwareModel.HELTEC_WIRELESS_TRACKER_V1_0: "HELTEC_WIRELESS_TRACKER_V1_0.png",
    HardwareModel.UNPHONE: "UNPHONE.png",
    HardwareModel.TD_LORAC: "TD_LORAC.png",
    HardwareModel.CDEBYTE_EORA_S3: "CDEBYTE_EORA_S3.png",
    HardwareModel.TWC_MESH_V4: "TWC_MESH_V4.png",
    HardwareModel.NRF52_PROMICRO_DIY: "NRF52_PROMICRO_DIY.png",
    HardwareModel.RADIOMASTER_900_BANDIT_NANO: "RADIOMASTER_900_BANDIT_NANO.png",
    HardwareModel.HELTEC_CAPSULE_SENSOR_V3: "HELTEC_CAPSULE_SENSOR_V3.png",
    HardwareModel.HELTEC_VISION_MASTER_T190: "HELTEC_VISION_MASTER_T190.png",
    HardwareModel.HELTEC_VISION_MASTER_E213: "HELTEC_VISION_MASTER_E213.png",
    HardwareModel.HELTEC_VISION_MASTER_E290: "HELTEC_VISION_MASTER_E290.png",
    HardwareModel.HELTEC_MESH_NODE_T114: "HELTEC_MESH_NODE_T114.png",
    HardwareModel.SENSECAP_INDICATOR: "SENSECAP_INDICATOR.png",
    HardwareModel.TRACKER_T1000_E: "TRACKER_T1000_E.png",
    HardwareModel.RAK3172: "RAK3172.png",
    HardwareModel.WIO_E5: "WIO_E5.png",
    HardwareModel.RADIOMASTER_900_BANDIT: "RADIOMASTER_900_BANDIT.png",
    HardwareModel.ME25LS01_4Y10TD: "ME25LS01_4Y10TD.png",
    HardwareModel.RP2040_FEATHER_RFM95: "RP2040_FEATHER_RFM95.png",
    HardwareModel.M5STACK_COREBASIC: "M5STACK_COREBASIC.png",
    HardwareModel.M5STACK_CORE2: "M5STACK_CORE2.png",
    HardwareModel.RPI_PICO2: "RPI_PICO.png",
    HardwareModel.M5STACK_CORES3: "M5STACK_CORES3.png",
    HardwareModel.SEEED_XIAO_S3: "XIAO.png",
    HardwareModel.MS24SF1: "MS24SF1.png",
    HardwareModel.TLORA_C6: "TLORA_C6.png",
    HardwareModel.WISMESH_TAP: "WISMESH_TAP.png",
    HardwareModel.ROUTASTIC: "ROUTASTIC.png",
    HardwareModel.MESH_TAB: "MESH_TAB.png",
    HardwareModel.MESHLINK: "MESHLINK.png",
    HardwareModel.XIAO_NRF52_KIT: "XIAO.png",
    HardwareModel.THINKNODE_M1: "THINKNODE_M1.png",
    HardwareModel.THINKNODE_M2: "THINKNODE_M2.png",
    HardwareModel.T_ETH_ELITE: "T_ETH_ELITE.png",
    HardwareModel.HELTEC_SENSOR_HUB: "HELTEC_SENSOR_HUB.png",
    HardwareModel.RESERVED_FRIED_CHICKEN: "RESERVED_FRIED_CHICKEN.png",
    HardwareModel.HELTEC_MESH_POCKET: "HELTEC_MESH_POCKET.png",
    HardwareModel.SEEED_SOLAR_NODE: "SEEED_SOLAR_NODE.png",
    HardwareModel.NOMADSTAR_METEOR_PRO: "NOMADSTAR_METEOR_PRO.png",
    HardwareModel.CROWPANEL: "CROWPANEL.png",
    HardwareModel.PRIVATE_HW: "PRIVATE_HW.png",
}
