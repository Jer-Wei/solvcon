#pragma once

/*
 * Copyright (c) 2016, Yung-Yu Chen <yyc@solvcon.net>
 * BSD 3-Clause License, see COPYING
 */

#include <memory>
#include <utility>
#include <cstdint>
#include <stdexcept>
#include <iterator>
#include <vector>

#include "march/core/core.hpp"

namespace march
{

namespace mesh
{

/**
 * Untyped unresizeable lookup table.
 */
class LookupTableCore {

private:

    std::shared_ptr<Buffer> m_buffer;
    std::vector<index_type> m_dims;
    index_type m_nghost = 0;
    index_type m_nbody = 0;
    index_type m_ncolumn = 1;
    index_type m_elsize = 1; ///< Element size in bytes.
    DataTypeId m_datatypeid = MH_INT8;

public:

    LookupTableCore() : m_buffer(Buffer::construct()), m_dims() { }

    /**
     * \param[in] nghost  Number of ghost (negative index) rows.
     * \param[in] nbody   Number of body (non-negative index) rows.
     * \param[in] dims    The shape of the table, including the combined row
     *                    number.
     * \param[in] datatypeid
     *  The libmarch ID of the data type.
     */
    LookupTableCore(
        index_type nghost
      , index_type nbody
      , const std::vector<index_type> & dims
      , DataTypeId datatypeid
    )
        : m_buffer()
        , m_dims(dims)
        , m_nghost(nghost)
        , m_nbody(nbody)
        , m_elsize(data_type_size(datatypeid))
        , m_datatypeid(datatypeid)
    {
        m_ncolumn = verify(nghost, nbody, dims, m_elsize);
        m_buffer = Buffer::construct((nghost+nbody) * m_ncolumn * m_elsize);
    }

    LookupTableCore(const LookupTableCore &) = delete;

    LookupTableCore(LookupTableCore &&) = delete;

    LookupTableCore & operator=(const LookupTableCore &) = delete;

    LookupTableCore & operator=(LookupTableCore &&) = delete;

    const std::vector<index_type> & dims() const { return m_dims; }

    index_type ndim() const { return m_dims.size(); }

    index_type nghost() const { return m_nghost; }

    index_type nbody() const { return m_nbody; }

    index_type ncolumn() const { return m_ncolumn; }

    index_type nelem() const { return (nghost()+nbody()) * ncolumn(); }

    index_type elsize() const { return m_elsize; }

    DataTypeId datatypeid() const { return m_datatypeid; }

    size_t nbyte() const { return buffer()->nbyte(); }

    /**
     * Pointer at the beginning of the row.
     */
    char * row(index_type loc) {
        return data()+(nghost()+loc)*ncolumn()*elsize();
    }

    /**
     * Pointer at the beginning of the row.
     */
    const char * row(index_type loc) const {
        return data()+(nghost()+loc)*ncolumn()*elsize();
    }

    /**
     * Internal data buffer.
     */
    const std::shared_ptr<Buffer> & buffer() const { return m_buffer; }

    /** Backdoor */
    char * data() const { return buffer()->template data<char>(); }

private:

    /**
     * Verify the shape.
     *
     * \param[in] nghost  Number of ghost (negative index) rows.
     * \param[in] nbody   Number of body (non-negative index) rows.
     * \param[in] dims    The shape of the table, including the combined row
     *                    number.
     * \param[in] elsize  Number of bytes per data element.
     */
    index_type verify(
        index_type nghost
      , index_type nbody
      , const std::vector<index_type> & dims
      , index_type elsize
    ) const {
        if (nghost < 0) { throw std::invalid_argument("negative nghost"); }
        if (nbody < 0) { throw std::invalid_argument("negative nbody"); }
        if (dims.size() == 0) { throw std::invalid_argument("empty dims"); }
        if (dims[0] != (nghost + nbody)) { throw std::invalid_argument("dims[0] != nghost + nbody"); }
        index_type ncolumn = 1;
        if (dims.size() > 1) {
            for (auto it=std::next(dims.begin()); it!=dims.end(); ++it) {
                ncolumn *= *it;
            }
        }
        if (ncolumn < 0) { throw std::invalid_argument("negative ncolumn"); }
        if (elsize < 0) { throw std::invalid_argument("negative elsize"); }
        return ncolumn;
    }

}; /* end class LookupTableCore */

namespace aux
{

/**
 * Helper struct to assign all elements in a fixed-size 1D array.
 */
template < typename ElemType, size_t NCOLUMN, size_t INDEX >
struct array_assign_ {
    typedef ElemType (&array_type)[NCOLUMN];
    typedef const ElemType (&const_array_type)[NCOLUMN];
    static void act(array_type row_out, const_array_type row_in) {
        array_assign_<ElemType, NCOLUMN, INDEX-1>::act(row_out, row_in);
        row_out[INDEX] = row_in[INDEX];
    }
}; /* end struct array_assign_ */

template < typename ElemType, size_t NCOLUMN >
struct array_assign_< ElemType, NCOLUMN, 0 >  {
    typedef ElemType (&array_type)[NCOLUMN];
    typedef const ElemType (&const_array_type)[NCOLUMN];
    static void act(array_type row_out, const_array_type row_in) {
        row_out[0] = row_in[0];
    }
}; /* end struct array_assign_ specialization */

template < typename ElemType, size_t NCOLUMN >
void array_assign(ElemType (&row_out)[NCOLUMN], const ElemType (&row_in)[NCOLUMN]) {
    array_assign_<ElemType, NCOLUMN, NCOLUMN-1>::act(row_out, row_in);
}

} /* end namespace aux */

/**
 * Typed unresizeable lookup table.
 */
template< 
    typename ElemType,
    size_t NCOLUMN
>
class LookupTable: public LookupTableCore
{

public:

    using elem_type = ElemType;

    LookupTable() {}

    LookupTable(index_type nghost, index_type nbody)
        : LookupTableCore(nghost, nbody, std::vector<index_type>({nghost+nbody, NCOLUMN}), type_to<ElemType>::id)
    {}

    LookupTable(index_type nghost, index_type nbody, char * data)
        : LookupTableCore(nghost, nbody, std::vector<index_type>({nghost+nbody, NCOLUMN}), type_to<ElemType>::id, data)
    {}

    elem_type (& operator[](index_type loc)) [NCOLUMN] {
        return *reinterpret_cast<elem_type(*)[NCOLUMN]>(row(loc));
    }

    const elem_type (& operator[](index_type loc) const) [NCOLUMN] {
        return *reinterpret_cast<const elem_type(*)[NCOLUMN]>(row(loc));
    }

    elem_type (& at(index_type loc)) [NCOLUMN] {
        check_range(loc); return (*this)[loc];
    }

    const elem_type (& at(index_type loc) const ) [NCOLUMN] {
        check_range(loc); return (*this)[loc];
    }

    /**
     * Return a std::vector at the input index location.
     */
    std::vector<elem_type> vat(index_type loc) const {
        check_range(loc);
        const elem_type (&row) [NCOLUMN] = (*this)[loc];
        return std::vector<elem_type>(row, row+NCOLUMN);
    }

    /** Backdoor */
    elem_type * data() const { return buffer()->template data<elem_type>(); }

private:

    template < size_t NARG >
    void set_impl(elem_type (&row)[NCOLUMN], elem_type value) {
        row[NARG - 1] = value;
    }

    template < size_t NARG, typename ... ArgTypes >
    void set_impl(elem_type (&row)[NCOLUMN], elem_type value, ArgTypes ... args) {
        row[NARG - 1 - sizeof...(args)] = value;
        set_impl<NARG>(row, args...);
    }

public:

    template < typename ... ArgTypes >
    void set(index_type loc, ArgTypes ... args) {
        static_assert(sizeof...(args) <= NCOLUMN, "too many arguments");
        set_impl<sizeof...(args)>((*this)[loc], args...);
    }

    template < typename ... ArgTypes >
    void set_at(index_type loc, ArgTypes ... args) {
        static_assert(sizeof...(args) <= NCOLUMN, "too many arguments");
        set_impl<sizeof...(args)>(this->at(loc), args...);
    }

    void set(index_type loc, const elem_type (&row_in)[NCOLUMN]) {
        aux::array_assign((*this)[loc], row_in);
    }

    void set_at(index_type loc, const elem_type (&row_in)[NCOLUMN]) {
        aux::array_assign(this->at(loc), row_in);
    }

    template < typename ... ArgTypes >
    void fill(ArgTypes ... args) {
        for (index_type it = -nghost(); it<nbody(); ++it) { set(it, args...); }
    }

    void fill(elem_type value) {
        elem_type * ptr = data();
        for (index_type it = -nghost(); it<nbody(); ++it) {
            for (index_type jt = 0; jt<static_cast<index_type>(NCOLUMN); ++jt) {
               ptr[0] = value;
               ++ptr;
            }
        }
    }

private:

    void check_range(index_type loc) const {
        if (loc < -nghost() || loc >= nbody()) {
            throw std::out_of_range("LookupTable location out of range");
        }
    }

}; /* end class LookupTable */

} /* end namespace mesh */

} /* end namespace march */

// vim: set ff=unix fenc=utf8 nobomb et sw=4 ts=4:
