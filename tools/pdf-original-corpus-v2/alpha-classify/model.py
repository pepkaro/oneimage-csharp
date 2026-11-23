# SPDX-License-Identifier: MIT
"""Independent arithmetic models for observed opaque-interior route quantization.
These are source-backed compatibility predictions, not an ISO pixel oracle.
"""
import struct

def f32(value):return struct.unpack('<f',struct.pack('<f',value))[0]
def alpha_byte(alpha):return int(f32(f32(alpha)*255))
def pdfium_rgb(alpha,source,backdrop=(255,255,255)):
 q=alpha_byte(alpha);return [((255-q)*b+q*c)//255 for b,c in zip(backdrop,source)]
def mupdf_rgb(alpha,source,backdrop=(255,255,255)):
 q=alpha_byte(alpha);weight=q+(q>>7);return [((256-weight)*b+weight*c)//256 for b,c in zip(backdrop,source)]
