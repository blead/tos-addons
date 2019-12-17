#!/usr/bin/env python3

import struct
import sys
import os
import zlib
import argparse

from binascii import crc32

SUPPORTED_FORMATS = (bytearray(b'\x50\x4b\x05\x06'),)
UNCOMPRESSED_EXT = ('.jpg', '.JPG', '.fsb', '.mp3')
PASSWORD = bytearray(b'\x6F\x66\x4F\x31\x61\x30\x75\x65\x58\x41\x3F\x20\x5B\xFF\x73\x20\x68\x20\x25\x3F')
CRC32_TABLE = [
  0x00000000, 0x77073096, 0xEE0E612C, 0x990951BA, 0x076DC419, 0x706AF48F, 0xE963A535, 0x9E6495A3,
  0x0EDB8832, 0x79DCB8A4, 0xE0D5E91E, 0x97D2D988, 0x09B64C2B, 0x7EB17CBD, 0xE7B82D07, 0x90BF1D91,
  0x1DB71064, 0x6AB020F2, 0xF3B97148, 0x84BE41DE, 0x1ADAD47D, 0x6DDDE4EB, 0xF4D4B551, 0x83D385C7,
  0x136C9856, 0x646BA8C0, 0xFD62F97A, 0x8A65C9EC, 0x14015C4F, 0x63066CD9, 0xFA0F3D63, 0x8D080DF5,
  0x3B6E20C8, 0x4C69105E, 0xD56041E4, 0xA2677172, 0x3C03E4D1, 0x4B04D447, 0xD20D85FD, 0xA50AB56B,
  0x35B5A8FA, 0x42B2986C, 0xDBBBC9D6, 0xACBCF940, 0x32D86CE3, 0x45DF5C75, 0xDCD60DCF, 0xABD13D59,
  0x26D930AC, 0x51DE003A, 0xC8D75180, 0xBFD06116, 0x21B4F4B5, 0x56B3C423, 0xCFBA9599, 0xB8BDA50F,
  0x2802B89E, 0x5F058808, 0xC60CD9B2, 0xB10BE924, 0x2F6F7C87, 0x58684C11, 0xC1611DAB, 0xB6662D3D,
  0x76DC4190, 0x01DB7106, 0x98D220BC, 0xEFD5102A, 0x71B18589, 0x06B6B51F, 0x9FBFE4A5, 0xE8B8D433,
  0x7807C9A2, 0x0F00F934, 0x9609A88E, 0xE10E9818, 0x7F6A0DBB, 0x086D3D2D, 0x91646C97, 0xE6635C01,
  0x6B6B51F4, 0x1C6C6162, 0x856530D8, 0xF262004E, 0x6C0695ED, 0x1B01A57B, 0x8208F4C1, 0xF50FC457,
  0x65B0D9C6, 0x12B7E950, 0x8BBEB8EA, 0xFCB9887C, 0x62DD1DDF, 0x15DA2D49, 0x8CD37CF3, 0xFBD44C65,
  0x4DB26158, 0x3AB551CE, 0xA3BC0074, 0xD4BB30E2, 0x4ADFA541, 0x3DD895D7, 0xA4D1C46D, 0xD3D6F4FB,
  0x4369E96A, 0x346ED9FC, 0xAD678846, 0xDA60B8D0, 0x44042D73, 0x33031DE5, 0xAA0A4C5F, 0xDD0D7CC9,
  0x5005713C, 0x270241AA, 0xBE0B1010, 0xC90C2086, 0x5768B525, 0x206F85B3, 0xB966D409, 0xCE61E49F,
  0x5EDEF90E, 0x29D9C998, 0xB0D09822, 0xC7D7A8B4, 0x59B33D17, 0x2EB40D81, 0xB7BD5C3B, 0xC0BA6CAD,
  0xEDB88320, 0x9ABFB3B6, 0x03B6E20C, 0x74B1D29A, 0xEAD54739, 0x9DD277AF, 0x04DB2615, 0x73DC1683,
  0xE3630B12, 0x94643B84, 0x0D6D6A3E, 0x7A6A5AA8, 0xE40ECF0B, 0x9309FF9D, 0x0A00AE27, 0x7D079EB1,
  0xF00F9344, 0x8708A3D2, 0x1E01F268, 0x6906C2FE, 0xF762575D, 0x806567CB, 0x196C3671, 0x6E6B06E7,
  0xFED41B76, 0x89D32BE0, 0x10DA7A5A, 0x67DD4ACC, 0xF9B9DF6F, 0x8EBEEFF9, 0x17B7BE43, 0x60B08ED5,
  0xD6D6A3E8, 0xA1D1937E, 0x38D8C2C4, 0x4FDFF252, 0xD1BB67F1, 0xA6BC5767, 0x3FB506DD, 0x48B2364B,
  0xD80D2BDA, 0xAF0A1B4C, 0x36034AF6, 0x41047A60, 0xDF60EFC3, 0xA867DF55, 0x316E8EEF, 0x4669BE79,
  0xCB61B38C, 0xBC66831A, 0x256FD2A0, 0x5268E236, 0xCC0C7795, 0xBB0B4703, 0x220216B9, 0x5505262F,
  0xC5BA3BBE, 0xB2BD0B28, 0x2BB45A92, 0x5CB36A04, 0xC2D7FFA7, 0xB5D0CF31, 0x2CD99E8B, 0x5BDEAE1D,
  0x9B64C2B0, 0xEC63F226, 0x756AA39C, 0x026D930A, 0x9C0906A9, 0xEB0E363F, 0x72076785, 0x05005713,
  0x95BF4A82, 0xE2B87A14, 0x7BB12BAE, 0x0CB61B38, 0x92D28E9B, 0xE5D5BE0D, 0x7CDCEFB7, 0x0BDBDF21,
  0x86D3D2D4, 0xF1D4E242, 0x68DDB3F8, 0x1FDA836E, 0x81BE16CD, 0xF6B9265B, 0x6FB077E1, 0x18B74777,
  0x88085AE6, 0xFF0F6A70, 0x66063BCA, 0x11010B5C, 0x8F659EFF, 0xF862AE69, 0x616BFFD3, 0x166CCF45,
  0xA00AE278, 0xD70DD2EE, 0x4E048354, 0x3903B3C2, 0xA7672661, 0xD06016F7, 0x4969474D, 0x3E6E77DB,
  0xAED16A4A, 0xD9D65ADC, 0x40DF0B66, 0x37D83BF0, 0xA9BCAE53, 0xDEBB9EC5, 0x47B2CF7F, 0x30B5FFE9,
  0xBDBDF21C, 0xCABAC28A, 0x53B39330, 0x24B4A3A6, 0xBAD03605, 0xCDD70693, 0x54DE5729, 0x23D967BF,
  0xB3667A2E, 0xC4614AB8, 0x5D681B02, 0x2A6F2B94, 0xB40BBE37, 0xC30C8EA1, 0x5A05DF1B, 0x2D02EF8D
]

class IpfInfo(object):
  """
  This class encapsulates information about a file entry in an IPF archive.

  Attributes:
    filename: A string representing the path and name of the file.
    archivename: The name of the originating IPF archive.
    filename_length: Length of the filename.
    archivename_length: Length of the archive name.
    compressed_length: The length of the compressed file data.
    uncompressed_length: The length of the uncompressed file data.
    data_offset: Offset in the archive file where data for this file begins.
  """

  def __init__(self, filename=None, archivename=None, datafile=None):
    """
    Inits IpfInfo class.
    """
    self._filename_length = 0
    self._unknown1 = None
    self._compressed_length = 0
    self._uncompressed_length = 0
    self._data_offset = 0
    self._archivename_length = 0

    self._filename = filename
    self._archivename = archivename
    self.datafile = datafile

    if filename:
      self._filename_length = len(filename)
    if archivename:
      self._archivename_length = len(archivename)

  @classmethod
  def from_buffer(self, buf):
    """
    Creates IpfInfo instance from a data buffer.
    """
    info = IpfInfo()
    data = struct.unpack('<HIIIIH', buf)

    info._filename_length = data[0]
    info._crc = data[1]
    info._compressed_length = data[2]
    info._uncompressed_length = data[3]
    info._data_offset = data[4]
    info._archivename_length = data[5]
    return info

  def to_buffer(self):
    """
    Creates a data buffer that represents this instance.
    """
    data = struct.pack('<HIIIIH', self.filename_length, self.crc, self.compressed_length, self.uncompressed_length, self.data_offset, self.archivename_length)
    data += self.archivename.encode('ascii')
    data += self.filename.encode('ascii')
    return data

  @property
  def filename(self):
    return self._filename

  @property
  def archivename(self):
    return self._archivename

  @property
  def filename_length(self):
    return self._filename_length

  @property
  def archivename_length(self):
    return self._archivename_length

  @property
  def compressed_length(self):
    return self._compressed_length

  @property
  def uncompressed_length(self):
    return self._uncompressed_length

  @property
  def data_offset(self):
    return self._data_offset

  @property
  def crc(self):
    return self._crc

  @property
  def key(self):
    return '%s_%s' % (self.archivename.lower(), self.filename.lower())

class IpfArchive(object):
  """
  Class that represents an IPF archive file.
  """

  def __init__(self, name, verbose=False, revision=0, base_revision=0, encryption=False):
    """
    Inits IpfArchive with a file `name`.

    Note: IpfArchive will immediately try to open the file. If it does not exist, an exception will be raised.
    """
    self.name = name
    self.verbose = verbose
    self.revision = revision
    self.base_revision = base_revision
    self.encryption = encryption
    self.fullname = os.path.abspath(name)
    _, self.archivename = os.path.split(self.name)

    self.file_handle = None
    self.closed = True

    self._files = None

  @property
  def files(self):
    if self._files is None:
      raise Exception('File has not been opened yet!')
    return self._files

  def close(self):
    """
    Closes all file handles if they are not already closed.
    """
    if self.closed:
      return

    if self.file_handle.mode.startswith('w'):
      self._write()

    if self.file_handle:
      self.file_handle.close()
    self.closed = True

  def open(self, mode='rb'):
    if not self.closed:
      return

    self.file_handle = open(self.name, mode)
    self.closed = False
    self._files = {}

    if mode.startswith('r'):
      self._read()

  def _read(self):
    self.file_handle.seek(-24, 2)
    self._archive_header = self.file_handle.read(24)
    self._file_size = self.file_handle.tell()

    self._archive_header_data = struct.unpack('<HIHI4sII', self._archive_header)
    self.file_count = self._archive_header_data[0]
    self._filetable_offset = self._archive_header_data[1]

    self._filefooter_offset = self._archive_header_data[3]
    self._format = self._archive_header_data[4]
    self.base_revision = self._archive_header_data[5]
    self.revision = self._archive_header_data[6]

    if self._format not in SUPPORTED_FORMATS:
      raise Exception('Unknown archive format: %s' % repr(self._format))

    # start reading file list
    self.file_handle.seek(self._filetable_offset, 0)
    for i in range(self.file_count):
      buf = self.file_handle.read(20)
      info = IpfInfo.from_buffer(buf)
      info._archivename = self.file_handle.read(info.archivename_length)
      info._filename = self.file_handle.read(info.filename_length)

      if info.key in self.files:
        # duplicate file name?!
        raise Exception('Duplicate file name: %s' % info.filename)

      self.files[info.key] = info

  def _write(self):
    pos = 0
    # write data entries first
    for key in self.files:
      fi = self.files[key]

      # read data
      f = open(fi.datafile, 'rb')
      data = f.read()
      f.close()

      fi._crc = crc32(data) & 0xffffffff
      fi._uncompressed_length = len(data)

      # check for extension
      _, extension = os.path.splitext(fi.filename)
      if extension in UNCOMPRESSED_EXT:
        # write data uncompressed
        self.file_handle.write(data)
        fi._compressed_length = fi.uncompressed_length
      else:
        # compress data
        deflater = zlib.compressobj(6, zlib.DEFLATED, -15)
        compressed = deflater.compress(data)
        compressed += deflater.flush()
        if self.encryption:
          compressed = ipf_encrypt(compressed)
        self.file_handle.write(compressed)
        fi._compressed_length = len(compressed)
        deflater = None

      # update file info
      fi._data_offset = pos
      pos += fi.compressed_length

    self._filetable_offset = pos

    # write the file table
    for key in self.files:
      fi = self.files[key]
      buf = fi.to_buffer()
      self.file_handle.write(buf)
      pos += len(buf)

    # write archive footer
    buf = struct.pack('<HIHI4sII', len(self.files), self._filetable_offset, 0, pos, SUPPORTED_FORMATS[0], self.base_revision, self.revision)
    self.file_handle.write(buf)

  def get(self, filename, archive=None):
    """
    Retrieves the `IpfInfo` object for `filename`.

    Args:
      filename: The name of the file.
      archive: The name of the archive. Defaults to the current archive

    Returns:
      An `IpfInfo` instance that describes the file entry.
      If the file could not be found, None is returned.
    """
    if archive is None:
      archive = self.archivename
    key = '%s_%s' % (archive.lower(), filename.lower())
    if key not in self.files:
      return None
    return self.files[key]

  def get_data(self, filename, archive=None):
    """
    Returns the uncompressed data of `filename` in the archive.

    Args:
      filename: The name of the file.
      archive: The name of the archive. Defaults to the current archive

    Returns:
      A string of uncompressed data.
      If the file could not be found, None is returned.
    """
    info = self.get(filename, archive)
    if info is None:
      return None
    self.file_handle.seek(info.data_offset)
    data = self.file_handle.read(info.compressed_length)
    if info.compressed_length == info.uncompressed_length:
      return data
    return zlib.decompress(data, -15)

  def extract_all(self, output_dir, overwrite=False):
    """
    Extracts all files into a directory.

    Args:
      output_dir: A string describing the output directory.
    """
    for filename in self.files:
      info = self.files[filename]
      output_file = os.path.join(output_dir, info.archivename, info.filename)

      if self.verbose:
        print('%s: %s' % (info.archivename, info.filename))

      # print output_file
      # print info.__dict__
      if not overwrite and os.path.isfile(output_file):
        continue
      head, tail = os.path.split(output_file)
      try:
        os.makedirs(head)
      except os.error:
        pass

      f = open(output_file, 'wb')
      try:
        data = self.get_data(info.filename, info.archivename)
        if self.encryption:
          data = ipf_decrypt(data)
        f.write(data)
      except Exception as e:
        print('Could not unpack %s' % info.filename)
        print(info.__dict__)
        print(e)
        print(data)
      f.close()

  def add(self, name, archive=None, newname=None):
    if archive is None:
      archive = self.archivename

    mode = 'Adding'
    fi = IpfInfo(newname or name, archive, datafile=name)
    if fi.key in self.files:
      mode = 'Replacing'
    if self.verbose:
      print('%s %s: %s' % (mode, fi.archivename, fi.filename))
    self.files[fi.key] = fi


def int_crc32(crc, value):
  return CRC32_TABLE[(crc ^ value) & 0xff] ^ (crc >> 8)

def update_keys(keys, ch):
  keys[0] = int_crc32(keys[0], ch)
  keys[1] = ((((keys[0] & 0xff) + keys[1]) * 0x8088405) + 1) & 0xffffffff
  keys[2] = int_crc32(keys[2], keys[1] >> 24)

def generate_keys(password):
  keys = [0x12345678, 0x23456789, 0x34567890]
  for ch in password:
    update_keys(keys, ch)
  return keys

def ipf_encrypt(data):
  encrypted_data = bytearray(data)
  keys = generate_keys(PASSWORD)
  for i in range(0, len(encrypted_data), 2):
    v = (keys[2] & 0xfffd) | 2
    update_keys(keys, encrypted_data[i])
    encrypted_data[i] ^= ((v * (v ^ 1)) & 0xffff) >> 8
  return encrypted_data

def ipf_decrypt(data):
  decrypted_data = bytearray(data)
  keys = generate_keys(PASSWORD)
  for i in range(0, len(decrypted_data), 2):
    v = (keys[2] & 0xfffd) | 2
    decrypted_data[i] ^= ((v * (v ^ 1)) & 0xffff) >> 8
    update_keys(keys, decrypted_data[i])
  return decrypted_data

def print_meta(ipf, args):
  print('{:<15}: {:}'.format('File count', ipf.file_count))
  print('{:<15}: {:}'.format('First file', ipf._filetable_offset))
  print('{:<15}: {:}'.format('Unknown', ipf._archive_header_data[2]))
  print('{:<15}: {:}'.format('Archive header', ipf._filefooter_offset))
  print('{:<15}: {:}'.format('Format', repr(ipf._format)))
  print('{:<15}: {:}'.format('Base revision', ipf.base_revision))
  print('{:<15}: {:}'.format('Revision', ipf.revision))

def print_list(ipf, args):
  for k in ipf.files:
    f = ipf.files[k]
    print('%s _ %s' % (f.archivename, f.filename))

    # crc check
    # data = ipf.get_data(k)
    # print('%s / %s / %s' % (f.crc, crc32(data) & 0xffffffff, ''))

def get_norm_relpath(path, start):
  newpath = os.path.normpath(os.path.relpath(path, args.target))
  if newpath == '.':
    return ''
  return newpath

def create_archive(ipf, args):
  if not args.target:
    raise Exception('No target for --create specified')

  _, filename = os.path.split(ipf.name)

  if os.path.isdir(args.target):
    for root, dirs, files in os.walk(args.target):
      # strip target path
      path = get_norm_relpath(root, args.target)

      # get archivename
      archive = filename
      components = path.split(os.path.sep)
      if components[0].endswith('.ipf'):
        archive = components[0]

      if path.startswith(archive):
        path = path[len(archive) + 1:]

      for f in files:
        newname = '/'.join(path.replace('\\', '/').split('/')) + '/' + f
        ipf.add(os.path.join(root, f), archive=archive, newname=newname.strip('/'))

  elif os.path.isfile(args.target):
    # TODO: Calculate relative path and stuff
    ipf.add(args.target)
  else:
    raise Exception('Target for --create not found')

if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  # functions
  parser.add_argument('-t', '--list', action='store_true', help='list the contents of an archive')
  parser.add_argument('-x', '--extract', action='store_true', help='extract files from an archive')
  parser.add_argument('-m', '--meta', action='store_true', help='show meta information of an archive')
  parser.add_argument('-c', '--create', action='store_true', help='create archive from target')
  # options
  parser.add_argument('-f', '--file', help='use archive file')
  parser.add_argument('-v', '--verbose', action='store_true', help='verbosely list files processed')
  parser.add_argument('-C', '--directory', metavar='DIR', help='change directory to DIR')
  parser.add_argument('-r', '--revision', type=int, help='revision number for the archive')
  parser.add_argument('-b', '--base-revision', type=int, help='base revision number for the archive')
  parser.add_argument('-e', '--encryption', action='store_true', help='encrypt/decrypt the archive')

  parser.add_argument('target', nargs='?', help='target file/directory to be extracted or packed')

  args = parser.parse_args()

  if args.list and args.extract:
    parser.print_help()
    print('You can only use one function!')
  elif not any([args.list, args.extract, args.meta, args.create]):
    parser.print_help()
    print('Please specify a function!')
  else:
    if not args.file:
      parser.print_help()
      print('Please specify a file!')
    else:
      ipf = IpfArchive(args.file, verbose=args.verbose)

      if not args.create:
        ipf.open()
      else:
        ipf.open('wb')

      if args.revision:
        ipf.revision = args.revision
      if args.base_revision:
        ipf.base_revision = args.base_revision
      ipf.encryption = args.encryption

      if args.meta:
        print_meta(ipf, args)

      if args.list:
        print_list(ipf, args)
      elif args.extract:
        ipf.extract_all(args.directory or '.')
      elif args.create:
        create_archive(ipf, args)

      ipf.close()
