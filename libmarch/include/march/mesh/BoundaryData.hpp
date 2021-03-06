#pragma once

/*
 * Copyright (c) 2016, Yung-Yu Chen <yyc@solvcon.net>
 * BSD 3-Clause License, see COPYING
 */

#include <utility>
#include <string>

#include "march/core.hpp"

namespace march
{

class BoundaryData {

public:

    static constexpr index_type BFREL = 3;

private:

    /**
     * First column is the face index in block.  The second column is the face
     * index in bndfcs.  The third column is the face index of the related
     * block (if exists).
     */
    LookupTable<index_type, BFREL> m_facn;

    /**
     * Values attached (specified) for each boundary face.  Each row is a
     * boundary face, and each column is a value.
     */
    LookupTableCore m_values;

    /**
     * Name of the boundary.
     */
    std::string m_name;

public:

    static const std::string & NONAME() {
        static const std::string str("<NONAME>");
        return str;
    }

    BoundaryData() : m_name(NONAME()) {}

    BoundaryData(index_type nvalue, const std::string & name=NONAME())
        : m_values(0, 0, {0, nvalue}, type_to<real_type>::id)
        , m_name(name)
    {}

    BoundaryData(index_type nbound, index_type nvalue, const std::string & name=NONAME())
        : m_facn(0, nbound)
        , m_values(0, nbound, {nbound, nvalue}, type_to<real_type>::id)
        , m_name(name)
    {}

    BoundaryData(BoundaryData const &  other) {
        if (this != &other) {
            m_facn = other.m_facn;
            m_values = other.m_values;
            m_name = other.m_name;
        }
    }

    BoundaryData(BoundaryData       && other) {
        if (this != &other) {
            m_facn = std::move(other.m_facn);
            m_values = std::move(other.m_values);
            m_name = other.m_name;
        }
    }

    BoundaryData & operator=(BoundaryData const &  other) {
        if (this != &other) {
            m_facn = other.m_facn;
            m_values = other.m_values;
            m_name = other.m_name;
        }
        return *this;
    }

    BoundaryData & operator=(BoundaryData       && other) {
        if (this != &other) {
            m_facn = std::move(other.m_facn);
            m_values = std::move(other.m_values);
            m_name = other.m_name;
        }
        return *this;
    }

    ~BoundaryData() = default;

    index_type nbound() const { return m_facn.nbody(); }

    index_type nvalue() const { return m_values.ncolumn(); }

    LookupTable<index_type, BFREL> const & facn() const { return m_facn; }

    LookupTable<index_type, BFREL>       & facn()       { return m_facn; }

    LookupTableCore const & values() const { return m_values; }

    LookupTableCore       & values()       { return m_values; }

    std::string const & name() const { return m_name; }

    std::string       & name()       { return m_name; }

    template< size_t NVALUE >
    LookupTable< real_type, NVALUE > const & values() const {
        assert(NVALUE == m_values.ncolumn());
        return *reinterpret_cast< LookupTable< real_type, NVALUE > const * >(&m_values);
    }

    template< size_t NVALUE >
    LookupTable< real_type, NVALUE >       & values()       {
        assert(NVALUE == m_values.ncolumn());
        return *reinterpret_cast< LookupTable< real_type, NVALUE >       * >(&m_values);
    }

    bool good_shape() const {
        return m_facn.nghost() == 0 && m_values.nghost() == 0
            && m_facn.nbody() == m_values.nbody();
    }

}; /* end class BoundaryData */

} /* end namespace march */

// vim: set ff=unix fenc=utf8 nobomb et sw=4 ts=4:
