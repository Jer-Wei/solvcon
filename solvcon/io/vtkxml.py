# -*- coding: UTF-8 -*-
#
# Copyright (C) 2008-2010 Yung-Yu Chen <yyc@solvcon.net>.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""
VTK XML file.

For a detailed description of the file format, see:
http://www.geophysik.uni-muenchen.de/intranet/it-service/applications/paraview/vtk-file-formats/
"""

class VtkXmlWriter(object):
    """
    Base class for VTK XML format data writer.

    @cvar cltpn_map: mapper for cell type number.
    @ctype cltpn_map: numpy.ndarray

    @ivar appended: append data at the end of XML file.  Forces binary.
    @itype appended: bool
    @ivar binary: flag for BINARY (False for ASCII).
    @itype binary: bool
    @ivar encoding: encoding for binary data ('base64' or 'raw').  Default is
        raw. Must be base64 if inline (not appended).
    @itype encoding: str
    @ivar compressor: compressor for binary data.  Can only be 'gz' or ''.
    @itype compressor: str
    @ivar fpdtype: floating-point data type (single/double).
    @itype fpdtype: numpy.dtype
    @ivar blk: corresponding block object.
    @itype blk: solvcon.block.Block
    """
    from numpy import array, float32, float64, int32
    cltpn_map = array([1, 3, 9, 5, 12, 10, 13, 14], dtype='int32')
    dtype_map = dict(
        float32='Float32',
        float64='Float64',
        int32='Int32',
    )
    del array, float32, float64, int32

    def __init__(self, blk, *args, **kw):
        self.appended = kw.pop('appended', True)
        binary = kw.pop('binary', False)
        self.binary = True if self.appended else binary
        encoding = kw.pop('encoding', 'raw')
        if self.binary and not self.appended:
            self.encoding = 'base64'
        else:
            self.encoding = encoding
        self.compressor = kw.pop('compressor', 'gz')
        fpdtype = kw.pop('fpdtype', None)
        if fpdtype == None:
            fpdtype = blk.fpdtype
        self.fpdtype = fpdtype
        self.blk = blk
        super(VtkXmlWriter, self).__init__()
        self.lvl = 0

    def _tag_open(self, tag, attr=None, newline=True, close=False):
        """
        Create an opening XML tag.

        @param tag: the name of tag.
        @type tag: str
        @keyword attr: attribute to be assigned to the tag in the format
            ('name1', value1), ('name2', value2) ...
        @type attr: list
        @keyword newline: add newline at the end.  Default is True.
        @type newline: bool
        @keyword close: close the tag while opening.  Default is False.
        @type close:
        @return: contructed opening tag.
        @rtype: str
        """
        if self.lvl < 0:
            raise ValueError('lvl %d < 0 when opening %s' % (lvl, tag))
        lvl = self.lvl
        msg = [' '*(lvl*2)]
        finish = ' />' if close else '>'
        if attr:
            msg.append('<%s %s%s' % (
                tag,
                ' '.join(['%s="%s"'%(key, str(val)) for key, val in attr]),
                finish,
            ))
        else:
            msg.append('<%s%s' % (tag, finish))
        if newline:
            msg.append('\n')
        if not close:
            self.lvl += 1
        return ''.join(msg)
    def _tag_close(self, tag, newline=True):
        """
        Create a closing XML tag.

        @param tag: the name of tag.
        @type tag: str
        @keyword newline: add newline at the end.  Default is True.
        @type newline: bool
        @return: contructed closing tag.
        @rtype: str
        """
        self.lvl -= 1
        if self.lvl < 0:
            raise ValueError('lvl %d < 0 when closing %s' % (lvl, tag))
        lvl = self.lvl
        msg = [' '*(lvl*2)]
        msg.append('</%s>'%tag)
        if newline:
            msg.append('\n')
        return ''.join(msg)

    def _create_data(self, arr):
        """
        Create data buffer from array.

        @param arr: input array.
        @type arr: numpy.ndarray
        @return: the created data buffer.
        @rtype: buffer
        """
        from struct import pack
        from base64 import standard_b64encode
        from zlib import compress
        data = arr.tostring()
        if self.compressor == 'gz':
            osize = len(data)
            data = compress(data)
            zsize = len(data)
        if self.encoding == 'base64':
            data = standard_b64encode(data)
        if self.compressor == 'gz':
            size = pack('iiii', 1, osize, osize, zsize)
        else:
            size = pack('i', len(data))
        if self.encoding == 'base64':
            size = standard_b64encode(size)
        return ''.join([size, data])

    def _write_darr(self, arr, outf, aplist, attr):
        """
        Write data array to a stream.

        @param arr: data array to be written.
        @type arr: numpy.ndarray
        @param outf: output file stream.
        @type outf: file
        @param aplist: appended data list.
        @type aplist: list
        @param attr: additional attributes to the DataArray tag.
        @type attr: list
        @return: nothing
        """
        # craft attributes.
        mattr = [
            ('type', self.dtype_map[str(arr.dtype)]),
        ]
        if self.binary:
            if aplist is None:
                mattr.append(('format', 'binary'))
                mattr.append(('encoding', self.encoding))
            else:
                mattr.append(('format', 'appended'))
                mattr.append(('offset', sum([len(dat) for dat in aplist])))
        else:
            mattr.append(('format', 'ascii'))
        mattr.extend(attr)
        attr = mattr
        # write.
        if self.binary:
            outf.write(self._tag_open('DataArray', attr, close=True))
            data = self._create_data(arr)
            if aplist is None:
                outf.write(data)
                outf.write('\n')
            else:
                aplist.append(data)
        else:
            outf.write(self._tag_open('DataArray', attr))
            arr.tofile(outf, sep=' ')
            outf.write('\n')
            outf.write(self._tag_close('DataArray'))

    def _write_appended(self, aplist, outf):
        """
        Write appended data list to a stream.

        @param aplist: the appendedn data list to be outputted.
        @type aplist: list
        @param outf: the file stream to be written.
        @type outf: file
        @return: nothing
        """
        outf.write(self._tag_open('AppendedData', [
            ('encoding', self.encoding),
        ]))
        outf.write('_')
        for data in aplist:
            outf.write(data)
        outf.write('\n')
        outf.write(self._tag_close('AppendedData'))

class VtkXmlUstGridWriter(VtkXmlWriter):
    """
    VTK XML unstructured mesh file format.  Capable for ASCII or BINARY.

    @ivar cache_grid: flag to cache the grid data (True) or not (False).
        Default True.
    @itype cache_grid: bool
    @ivar scalars: dictionary holding scalar data.
    @itype scalars: dict
    @ivar vectors: dictionary holding vector data.
    @itype vectors: dict
    @ivar griddata: cached grid data.
    @itype griddata: str
    """
    def __init__(self, blk, *args, **kw):
        self.cache_grid = kw.pop('cache_grid', True)
        self.scalars = kw.pop('scalars', dict())
        self.vectors = kw.pop('vectors', dict())
        super(VtkXmlUstGridWriter, self).__init__(blk, *args, **kw)
        self.griddata = None

    def _convert_varr(self, arr):
        """
        Helper to convert vector data array from a block.

        @param arr: array to be converted.  It will be copied and remain
            untouched.
        @type arr: numpy.ndarray
        @return: converted array.
        @rtype: numpy.ndarray
        """
        from numpy import empty
        arr = arr.copy()
        ndim = self.blk.ndim
        nit = arr.shape[0]
        if ndim == 2:
            arrn = empty((nit, ndim+1), dtype=arr.dtype)
            arrn[:,2] = 0.0
            arrn[:,:2] = arr[:,:]
            arr = arrn
        return arr

    @staticmethod
    def _convert_clnds(clnds):
        """
        Convert nodes in cells into a compressed array format.

        @param clnds: the array to be compressed.
        @type clnds: numpy.ndarray
        @return: the compressed array.
        @rtype: numpy.ndarray
        """
        from numpy import empty
        arr = empty(clnds[:,0].sum(), dtype='int32')
        ncell = clnds.shape[0]
        icl = 0
        it = 0
        while icl < ncell:
            ncl = clnds[icl,0]
            arr[it:it+ncl] = clnds[icl,1:ncl+1]
            it += ncl
            icl += 1
        return arr

    def write(self, outf, close_on_finish=False):
        """
        Write to file.

        @param outf: output file object or file name.
        @type outf: file str
        @keyword close_on_finish: flag close on finishing (True).  Default
            False.  If outf is file name, the output file will be close no
            matter what is set in this flag.
        @type close_on_finish: bool
        @return: nothing
        """
        if isinstance(outf, str):
            mode = 'wb' if self.binary else 'w'
            outf = open(outf, mode)
            close_on_finish = True
        # write header.
        outf.write('<?xml version="1.0"?>\n')
        attr = [
            ('type', 'UnstructuredGrid'),
            ('version', '0.1'),
            ('byte_order', 'LittleEndian'),
        ]
        if self.compressor == 'gz':
            attr.append(('compressor', 'vtkZLibDataCompressor'))
        outf.write(self._tag_open('VTKFile', attr))
        outf.write(self._tag_open('UnstructuredGrid'))
        outf.write(self._tag_open('Piece', [
            ('NumberOfPoints', self.blk.nnode),
            ('NumberOfCells', self.blk.ncell),
        ]))
        aplist = list() if self.appended else None
        # write points.
        outf.write(self._tag_open('Points'))
        self._write_darr(self._convert_varr(self.blk.ndcrd), outf, aplist, [
            ('NumberOfComponents', 3),
        ])
        outf.write(self._tag_close('Points'))
        # write cells.
        outf.write(self._tag_open('Cells'))
        self._write_darr(self._convert_clnds(self.blk.clnds), outf, aplist, [
            ('Name', 'connectivity'),
        ])
        self._write_darr(self.blk.clnds[:,0].cumsum(dtype='int32'), outf,
            aplist, [
            ('Name', 'offsets'),
        ])
        self._write_darr(self.cltpn_map[self.blk.cltpn], outf, aplist, [
            ('Name', 'types'),
        ])
        outf.write(self._tag_close('Cells'))
        # write footer.
        outf.write(self._tag_close('Piece'))
        outf.write(self._tag_close('UnstructuredGrid'))
        if aplist:
            self._write_appended(aplist, outf)
        outf.write(self._tag_close('VTKFile'))
        if close_on_finish:
            outf.close()
        # discard griddata if not cached.
        if not self.cache_grid:
            self.griddata = None