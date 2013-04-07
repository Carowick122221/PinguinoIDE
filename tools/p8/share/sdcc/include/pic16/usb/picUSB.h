// Firmware framework for USB I/O on PIC 18F2455 (and siblings)
// Copyright (C) 2005 Alexander Enzmann
//
// Adapted to Pinguino by Jean-Pierre Mandon (C) 2010
// 
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 2.1 of the License, or (at your option) any later version.
//
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public
// License along with this library; if not, write to the Free Software
// Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
//
/**
TODO:
 - BufferDescriptorTable should be an array
**/
#ifndef PICUSB_H
#define PICUSB_H

#include <pic18fregs.h>

#ifdef USB_USE_UART
#include "usb_uart.h"
#endif
#ifdef USB_USE_CDC
#include "usb_cdc.h"
#endif

#define PTR16(x) ((unsigned int)(((unsigned long)x) & 0xFFFF))

#define LSB(x) (x & 0xFF)
#define MSB(x) ((x & 0xFF00) >> 8)

/*
definition for the initial ep0, most are defined here since they are used be the user in the usb_config.h file
*/
#define EP0_BUFFER_SIZE         64

/* USB direction */
#define OUT                 0
#define IN                  1

/* UEPn Initialization Parameters */
#define EP_CTRL     0x06            // Cfg Control pipe for this ep
#define EP_OUT      0x0C            // Cfg OUT only pipe for this ep
#define EP_IN       0x0A            // Cfg IN only pipe for this ep
#define EP_OUT_IN   0x0E            // Cfg both OUT & IN pipes for this ep
#define HSHK_EN     0x10            // Enable handshake packet
                                    // Handshake should be disable for isoch
//
// Standard Request Codes USB 2.0 Spec Ref Table 9-4
//
#define GET_STATUS         0
#define CLEAR_FEATURE      1
#define SET_FEATURE        3
#define SET_ADDRESS        5
#define GET_DESCRIPTOR     6
#define SET_DESCRIPTOR     7
#define GET_CONFIGURATION  8
#define SET_CONFIGURATION  9
#define GET_INTERFACE     10
#define SET_INTERFACE     11
#define SYNCH_FRAME       12

// Descriptor Types
#define DEVICE_DESCRIPTOR       	0x01
#define CONFIGURATION_DESCRIPTOR 	0x02
#define STRING_DESCRIPTOR        	0x03
#define INTERFACE_DESCRIPTOR     	0x04
#define ENDPOINT_DESCRIPTOR      	0x05
#define DEVICE_QUALIFIER_DESCRIPTOR	0x06

// Standard Feature Selectors
#define DEVICE_REMOTE_WAKEUP    0x01
#define ENDPOINT_HALT           0x00

// Buffer Descriptor bit masks (from PIC datasheet)
#define BDS_COWN   0x00 // CPU Own Bit
#define BDS_UOWN   0x80 // USB Own Bit
#define BDS_DTS    0x40 // Data Toggle Synchronization Bit
#define BDS_KEN    0x20 // BD Keep Enable Bit
#define BDS_INCDIS 0x10 // Address Increment Disable Bit
#define BDS_DTSEN  0x08 // Data Toggle Synchronization Enable Bit
#define BDS_BSTALL 0x04 // Buffer Stall Enable Bit
#define BDS_BC9    0x02 // Byte count bit 9
#define BDS_BC8    0x01 // Byte count bit 8

#define BDS_DAT0   0x00 //DATA0 packet expected next
#define BDS_DAT1   0x40 //DATA1 packet expected next

// Device states (Chap 9.1.1)
#define DETACHED     0
#define ATTACHED     1
#define POWERED      2
#define DEFAULT      3
#define ADDRESS      4
#define CONFIGURED   5

/** Buffer Descriptor Status Register **/
typedef union
{
    unsigned char uc;
    struct{
        unsigned BC8:1;
        unsigned BC9:1;
        unsigned BSTALL:1;              /*!< Buffer Stall Enable */
        unsigned DTSEN:1;               /*!< Data Toggle Synch Enable */
        unsigned INCDIS:1;              /*!< Address Increment Disable */
        unsigned KEN:1;                 /*!< BD Keep Enable */
        unsigned DTS:1;                 /*!< Data Toggle Synch Value */
        unsigned UOWN:1;                /*!< USB Ownership */
    };
    struct{
        unsigned :2;
        unsigned PID0:1;                /*!< Packet Identifier, bit 0 */
        unsigned PID1:1;                /*!< Packet Identifier, bit 1 */
        unsigned PID2:1;                /*!< Packet Identifier, bit 2 */
        unsigned PID3:1;                /*!< Packet Identifier, bit 3 */
        unsigned :2;
    };
    struct{
        unsigned :2;
        unsigned PID:4;                 /*!< Packet Identifier */
        unsigned :2;
    };
} BDStat;

/** Buffer Descriptor Table<br>
See section 17.4 "Buffer Description and the Buffer Description Table" in datasheet page 171
**/
typedef union
{
    struct
    {
        BDStat Stat;                    /*!< Buffer Descriptor Status Register */
        unsigned char Cnt;              /*!< Number of bytes to send/sent/(that can be )received */
        unsigned char ADRL;             /*!< Buffer Address Low */
        unsigned char ADRH;             /*!< Buffer Address High */
    };
    struct
    {
        unsigned :8;
        unsigned :8;
        __data unsigned int *ADDR;      /*!< Buffer Address */
    };
} BufferDescriptorTable;


/**
 USB Device Descriptor.<br>
 The device descriptor of a USB device represents the entire device. As a result a USB device can only hav
e one device descriptor. It specifies some basic, yet important information about the device such as the s
upported USB version, maximum packet size, vendor and product IDs and the number of possible configuration
s the device can have.
 **/
typedef struct
{
    unsigned char bLength;              /*!< Size of the Descriptor in Bytes (18 bytes = 0x12) */
    unsigned char bDescriptorType;      /*!< Device Descriptor (0x01) */
    unsigned int  bcdUSB;               /*!< USB Specification Number which device complies to. */
    unsigned char bDeviceClass;         /*!< Class Code (Assigned by USB Org). If equal to Zero, each inte
rface specifies it’s own class code. If equal to 0xFF, the class code is vendor specified. Otherwise field
 is valid Class Code.*/
    unsigned char bDeviceSubClass;      /*!< Subclass Code (Assigned by USB Org) */
    unsigned char bDeviceProtocol;      /*!< Protocol Code (Assigned by USB Org) */
    unsigned char bMaxPacketSize0;      /*!< Maximum Packet Size for Zero Endpoint. Valid Sizes are 8, 16,
 32, 64 */
    unsigned int  idVendor;             /*!< Vendor ID (Assigned by USB Org). Microchip Vendor ID is 0x04D
8 */
    unsigned int  idProduct;            /*!< Product ID (Assigned by Manufacturer) */
    unsigned int  bcdDevice;            /*!< Device Release Number */
    unsigned char iManufacturer;        /*!< Index of Manufacturer String Descriptor */
    unsigned char iProduct;             /*!< Index of Product String Descriptor */
    unsigned char iSerialNumber;        /*!< Index of Serial Number String Descriptor */
    unsigned char bNumConfigurations;   /*!< Number of Possible Configurations */
} USB_Device_Descriptor;


/**
Configuration Descriptors<br>
A USB device can have several different configurations although the majority of devices are simple and onl
y have one. The configuration descriptor specifies how the device is powered, what the maximum power consu
mption is, the number of interfaces it has. Therefore it is possible to have two configurations, one for w
hen the device is bus powered and another when it is mains powered. As this is a "header" to the Interface
 descriptors, its also feasible to have one configuration using a different transfer mode to that of anoth
er configuration.<br>
Once all the configurations have been examined by the host, the host will send a SetConfiguration command
with a non zero value which matches the bConfigurationValue of one of the configurations. This is used to
select the desired configuration.
**/
typedef struct
{
    unsigned char bLength;              /*!< Size of Descriptor in Bytes */
    unsigned char bDescriptorType;      /*!< Configuration Descriptor (0x02) */
    unsigned int  wTotalLength;         /*!< Total length in bytes of data returned (Configuration Descriptor + Interface Descriptor + n* Endpoint Descriptor */
    unsigned char bNumInterfaces;       /*!< Number of Interfaces */
    unsigned char bConfigurationValue;  /*!< Value to use as an argument to select this configuration */
    unsigned char iConfiguration;       /*!< Index of String Descriptor describing this configuration */
    unsigned char bmAttributes;         /*!< <ul><li>D7 Reserved, set to 1.(USB 1.0 Bus Powered).</li><li>D6 Self Powered.</li><li>D5 Remote Wakeup.</li><li>D4..0 Reserved, set to 0.</li></ul> */
    unsigned char bMaxPower;            /*!< Maximum Power Consumption in 2mA units */
} USB_Configuration_Descriptor_Header;


//
// Global variables
extern byte deviceState;    // Visible device states (from USB 2.0, chap 9.1.1)
extern byte selfPowered;
extern byte remoteWakeup;
extern byte currentConfiguration;

extern volatile BufferDescriptorTable __at (0x400) ep_bdt[32];
/* Out buffer descriptor of endpoint ep */
/* BEWARE : both work only without ping pong buffers */
#define EP_OUT_BD(ep) (ep_bdt[(ep << 1)])
/* In buffer descriptor of endpoint ep */
#define EP_IN_BD(ep)  (ep_bdt[(ep << 1) + 1])

/**
Every device request starts with an 8 byte setup packet (USB 2.0, chap 9.3)
with a standard layout.  The meaning of wValue and wIndex will
vary depending on the request type and specific request.
See also: http://www.beyondlogic.org/usbnutshell/usb6.htm
TODO: split this Array up to be more precise
TODO: use word instead of LSB/MSB bytes
**/
typedef union //_setupPacketStruct
{
  struct {
    byte bmRequestType; /*!< D7 Data Phase Transfer Direction<ul><li>0 = Host to Device</li><li>1 = Device to Host</li></ul>D6..5 Typ<ul><li>0 = Standard</li><li>1 = Class</li><li>2 = Vendor</li><li>3 = Reserved</li></ul>D4..0 Recipient<ul><li>0 = Device</li><li>1 = Interface</li><li>2 = Endpoint</li><li>3 = Other</li></ul> */
    byte bRequest;      // Specific request
    byte wValue0;       // LSB of wValue
    byte wValue1;       // MSB of wValue
    byte wIndex0;       // LSB of wIndex
    byte wIndex1;       // MSB of wIndex
    word wLength;       // Number of bytes to transfer if there's a data stage
  };
  struct {
    byte extra[EP0_BUFFER_SIZE];     // Fill out to same size as Endpoint 0 max buffer
  };
} setupPacketStruct;


/**
Interface Descriptors<br>
The interface descriptor could be seen as a header or grouping of the endpoints into a functional group performing a single feature of the device.
**/
typedef struct
{
    unsigned char bLength;              /*!< Size of Descriptor in Bytes (9 Bytes) */
    unsigned char bDescriptorType;      /*!< Interface Descriptor (0x04) */
    unsigned char bInterfaceNumber;     /*!< Number of Interface */
    unsigned char bAlternateSetting;    /*!< Value used to select alternative setting */
    unsigned char bNumEndpoints;        /*!< Number of Endpoints used for this interface */
    unsigned char bInterfaceClass;      /*!< Class Code (Assigned by USB Org) e.g. HID, communications, mass storage etc.*/
    unsigned char bInterfaceSubClass;   /*!< Subclass Code (Assigned by USB Org) */
    unsigned char bInterfaceProtocol;   /*!< Protocol Code (Assigned by USB Org) */
    unsigned char iInterface;           /*!< Index of String Descriptor Describing this interface */
} USB_Interface_Descriptor;


/**
Endpoint Descriptor
**/
typedef struct
{
    unsigned char bLength;              /*!< Size of Descriptor in Bytes (7 bytes) */
    unsigned char bDescriptorType;      /*!< Endpoint Descriptor (0x05) */
    unsigned char bEndpointAddress;     /*!< Endpoint Address<ul><li>Bits 0..3b Endpoint Number.</li><li>Bits 4..6b Reserved. Set to Zero</li><li>Bits 7 Direction 0 = Out, 1 = In (Ignored for Control Endpoints)</li></ul> */
    unsigned char bmAttributes;         /*!< Bits 0..1 Transfer Type<br><ul><li>00 = Control</li><li>01 = Isochronous</li><li>10 = Bulk</li><li>11 = Interrupt</li></ul><br>Bits 2..7 are reserved. If Isochronous endpoint,<br>Bits 3..2 = Synchronisation Type (Iso Mode)<br><ul><li>00 = No Synchonisation</li><li>01 = Asynchronous</li><li>10 = Adaptive</li><li>11 = Synchronous</li></ul><br>Bits 5..4 = Usage Type (Iso Mode)<ul><li>00 = Data Endpoint</li><li>01 = Feedback Endpoint</li><li>10 = Explicit Feedback Data Endpoint</li><li>11 = Reserved</li></ul> */
    unsigned int  wMaxPacketSize;       /*!< Maximum Packet Size this endpoint is capable of sending or receiving */
    unsigned char bInterval;            /*!< Interval for polling endpoint data transfers. Value in frame counts. Ignored for Bulk & Control Endpoints. Isochronous must equal 1 and field may range from 1 to 255 for interrupt endpoints. */
} USB_Endpoint_Descriptor;

extern volatile setupPacketStruct SetupPacket;

// inPtr/OutPtr are used to move data from user memory (RAM/ROM/EEPROM) buffers
// from/to USB dual port buffers.
extern byte *outPtr;        // Address of buffer to send to host
extern byte *inPtr;         // Address of buffer to receive data from host
extern unsigned int wCount; // Total # of bytes to move
extern byte deviceState;

// USB Functions
void EnableUSBModule(void);
void ProcessUSBTransactions(void);

// # of bytes from last HID transaction
extern byte hidRxLen;

#endif //PICUSB_H
